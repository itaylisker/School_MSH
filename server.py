import socket
import os
from db_handle import check_credentials

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET =Ipv4 | SOCK_STREAM- TCP

server_socket.bind((f'127.0.0.1', 5050))
server_socket.listen()

client_obj, ip = server_socket.accept()


while True:
    data = client_obj.recv(1024).decode().split(',')
    if data[0] == 'Login':
        username = data[1]
        password = data[2]
        client_obj.send(check_credentials(username, password).encode())
    elif data[0] == 'cmd':
        output = os.popen(data[1]).read()
        if output:
            client_obj.send(output.encode())
        else:
            client_obj.send(b'ERROR')
