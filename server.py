import socket
import threading

HOST = "127.0.0.1"
PORT = 3334
CREDENTIALS_FILE = './resources/credentials.txt'


class Request:
    def __init__(self, command, params):
        self.type = command
        self.params = params


class Response:
    def __init__(self, status, payload):
        self.status = status
        self.payload = payload


def serialize(response):
    return bytes(str(response.status) + ' ' + response.payload, encoding='utf-8')


def deserialize(request):
    items = request.decode('utf-8').strip().split(' ')
    if len(items) > 1:
        return Request(items[0], items[1:])
    return Request(items[0], [])


class StateMachine:
    def __init__(self, client, global_state):
        self.transitions = {}
        self.start_state = None
        self.end_states = []
        self.current_state = None
        self.global_state = global_state
        self.client = client

    def add_transition(self, state_name, command, transition, end_state=0):
        self.transitions.setdefault(state_name, {})
        self.transitions[state_name][command] = transition
        if end_state:
            self.end_states.append(state_name)

    def set_start(self, name):
        self.start_state = name
        self.current_state = name

    def process_command(self, unpacked_request):
        print('state before %s' % self.current_state)
        if unpacked_request.type not in self.transitions[self.current_state]:
            valid_commands = ', '.join(self.transitions[self.current_state].keys())
            return Response(-4, f'Invalid command. Valid commands are: {valid_commands}')
        handler = self.transitions[self.current_state][unpacked_request.type]
        (new_state, response) = handler(unpacked_request, self.global_state, self.client)
        self.current_state = new_state
        print('state after %s' % self.current_state)
        return response


def verify_credentials(username, password):
    with open(CREDENTIALS_FILE, 'r') as file:
        for line in file:
            user, passw = line.strip().split(':')
            if user == username and passw == password:
                return True
    return False

def request_connect(request, global_state, client):
    if len(request.params) > 1:
        username = request.params[0]
        password = request.params[1]
        if verify_credentials(username, password):
            return ('auth', Response(0, 'you are in'))
        else:
            return ('start', Response(-2, 'you do not know the secret'))
    else:
        return ('start', Response(-1, 'not enough params. username & password required'))


def request_disconnect(request, global_state, client):
    return ('start', Response(0, 'you are now out'))


class TopicProtocol(StateMachine):
    def __init__(self, client, global_state):
        super().__init__(client, global_state)
        self.set_start('start')
        self.add_transition('start', 'connect', request_connect)
        self.add_transition('auth', 'disconnect', request_disconnect)


class TopicList:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def add_client(self, client):
        with self.lock:
            self.clients.append(client)

    def remove_client(self, client):
        with self.lock:
            self.clients.remove(client)


is_running = True
global_state = TopicList()


def handle_client_write(client, response):
    client.sendall(serialize(response))


def handle_client_read(client):
    try:
        protocol = TopicProtocol(client, global_state)
        while True:
            if client == None:
                break
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