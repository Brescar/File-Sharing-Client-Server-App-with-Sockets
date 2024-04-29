import socket
import threading
import pickle
import os

from util.constant import HOST, PORT

last_sent_command = ''

def handle_server_write(s):
    while True:
        data = s.recv(1024)
        try:
            file_content = pickle.loads(data)
            file_name = os.path.basename(last_sent_command.split()[-1])
            downloads_dir = os.path.join(os.getcwd(), 'downloads')
            os.makedirs(downloads_dir, exist_ok=True)

            file_path = os.path.join(downloads_dir, file_name)
            counter = 1

            while os.path.exists(file_path):
                base_name, ext = os.path.splitext(file_name)
                file_path = os.path.join(downloads_dir, f"{base_name}_{counter}{ext}")
                counter += 1

            with open(file_path, 'wb') as f:
                f.write(file_content)
        except pickle.UnpicklingError:
            print("Server says", data.decode())
            
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    server_write_thread = threading.Thread(target=handle_server_write, args=(s,))
    server_write_thread.start()
    while True:
        line = input('>')
        last_sent_command = line
        s.sendall(line.encode())