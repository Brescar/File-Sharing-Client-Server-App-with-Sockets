import socket
import threading
import pickle

HOST = "127.0.0.1"
PORT = 3334

last_sent_command = ''

def handle_server_write(s):
    while True:
        data = s.recv(1024)
        try:
            deserialized_file = pickle.loads(data)
            
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