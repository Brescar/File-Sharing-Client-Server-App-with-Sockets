import os
import socket
import threading
import pickle
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from util.constant import *
from lib.topic import TopicProtocol, TopicList
from lib.serialize import *


def serialize(response):
    return bytes(str(response.status) + ' ' + response.payload, encoding='utf-8')


def deserialize(request):
    items = request.decode('utf-8').strip().split(' ')
    if len(items) > 1:
        return Request(items[0], items[1:])
    return Request(items[0], [])


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, username, global_state):
        self.username = username
        self.global_state = global_state

    def on_modified(self, event):
        self.notify_clients(f'File {event.src_path} has been modified')

    def on_created(self, event):
        self.notify_clients(f'File {event.src_path} has been created')

    def on_deleted(self, event):
        self.notify_clients(f'File {event.src_path} has been deleted')

    def notify_clients(self, message):
        for client in self.global_state.clients:
            client.sendall(bytes(message, encoding='utf-8'))


def verify_credentials(username, password, logged_in_users):
    with open(CREDENTIALS_FILE, 'r') as file:
        for line in file:
            user, passw = line.strip().split(':')
            if user == username and passw == password and user not in logged_in_users:
                return True
    return False


def create_user_folder(username):
    user_folder = os.path.join(USER_FOLDER_PATH, f'{username}_files')
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_folder(username: str) -> str:
    user_folder = os.path.join(USER_FOLDER_PATH, f'{username}_files')

    if not os.path.exists(user_folder):
        raise FileNotFoundError(f'Requested file {user_folder} does not exist.')

    return user_folder 

def start_observer(user_folder, username, global_state):
    event_handler = FileChangeHandler(username, global_state)
    observer = Observer()
    observer.schedule(event_handler, user_folder, recursive=True)
    observer.start()

def notify_clients(username, user_folder, global_state):
    files = os.listdir(user_folder)
    message = f'User {username} has logged in. They have the following files: {", ".join(files)}'
    for client in global_state.clients:
        client.sendall(bytes(message, encoding='utf-8'))

def notify_clients_disconnect(username: str, user_folder: str, global_state: TopicList) -> None:
    files = os.listdir(user_folder)
    message = f'User {username} has logged out. You have lost access to the following files {", ".join(files)}'

    for client in global_state.clients:
        client.sendall(bytes(message, encoding='utf-8'))

def request_connect(request, global_state, client):
    if len(request.params) > 1:
        username = request.params[0]
        password = request.params[1]
        if verify_credentials(username, password, global_state.logged_in_users):
            global_state.logged_in_users.append(username)
            global_state.client_user_map[client] = username
            user_folder = create_user_folder(username)
            start_observer(user_folder, username, global_state)
            notify_clients(username, user_folder, global_state)
            list_all_files(request, global_state, client)
            return ('auth', Response(0, 'you are in'))
        else:
            return ('start', Response(-2, 'you do not know the secret or user is already logged in'))
    else:
        return ('start', Response(-1, 'not enough params. username & password required'))


def request_disconnect(request, global_state, client):
    username = global_state.client_user_map.get(client)
    
    notify_clients_disconnect(username, get_user_folder(username), global_state)

    if username:
        global_state.logged_in_users.remove(username)
        del global_state.client_user_map[client]
    return ('start', Response(0, 'you are now out'))

def list_my_files(request, global_state, client):
    username = global_state.client_user_map.get(client)  # Get the username associated with the client
    if username:
        user_folder = os.path.join(USER_FOLDER_PATH, f'{username}_files')
        files = os.listdir(user_folder)
        message = f'You have the following files: {", ".join(files)}'
        client.sendall(bytes(message, encoding='utf-8'))
        return ('auth', Response(0, 'Listed your files'))
    else:
        return ('auth', Response(-3, 'User is not logged in'))

def list_all_files(request, global_state, client):
    message = ''
    for username in global_state.logged_in_users:
        user_folder = os.path.join(USER_FOLDER_PATH, f'{username}_files')
        if os.path.exists(user_folder):
            files = os.listdir(user_folder)
            message += f'User {username} has the following files: {", ".join(files)}\n'
    client.sendall(bytes(message, encoding='utf-8'))
    return ('auth', Response(0, 'Listed all files'))

# TODO: trying to download files from the server of a user which is not logged in should not work,
# with message, but currently it does work. Fix this.
def download_file(request, global_state, requesting_client):
    if len(request.params) < 2:
        return ('auth', Response(-1, 'Not enough parameters. Target client name and file name (extension included) are required.'))
    
    target_client_name, file_name = request.params
    requesting_client_name = global_state.client_user_map.get(requesting_client)
    
    if not requesting_client_name:
        return ('auth', Response(-3, 'User is not logged in'))
    
    target_user_directory = get_user_folder(target_client_name)
    target_user_file = os.path.join(target_user_directory, file_name)
    target_user_file = target_user_file.replace('\\', os.sep).replace('/', os.sep)
    
    if not os.path.exists(target_user_file):
        return ('auth', Response(-2, 'File does not exist'))
    
    with open(target_user_file, 'rb') as f:
        file_content = f.read()
    serialized_file = pickle.dumps(file_content)
    requesting_client.sendall(serialized_file)
    
    return ('auth', Response(0, 'File downloaded successfully'))

is_running = True
global_state = TopicList()


def handle_client_write(client, response):
    client.sendall(serialize(response))


def handle_client_read(client):
    try:
        protocol = TopicProtocol(client, global_state, [
            ['start', 'connect', request_connect],
            ['auth', 'disconnect', request_disconnect],
            ['auth', 'list_my_files', list_my_files],
            ['auth', 'list_all_files', list_all_files],
            ['auth', 'download_file', download_file]
        ])
        while True:
            if client == None:
               return 
            data = client.recv(1024)
            if not data:
                break
            unpacked_request = deserialize(data)
            response = protocol.process_command(unpacked_request)
            handle_client_write(client, response)

    except OSError as e:
        global_state.clients.remove(client)


def accept(server):
    while is_running:
        client, addr = server.accept()
        global_state.add_client(client)
        print(f"{addr} has connected")
        client_read_thread = threading.Thread(target=handle_client_read, args=(client,))
        client_read_thread.start()


def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        accept_thread = threading.Thread(target=accept, args=(server,))
        accept_thread.start()
        accept_thread.join()
    except BaseException as err:
        print(err)
    finally:
        if server:
            server.close()


if __name__ == '__main__':
    main()