import socket
import json
import os
from threading import Thread
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET =Ipv4 | SOCK_STREAM- TCP

server_socket.bind((f'127.0.0.1', 5050))
server_socket.listen()

clients = {}


def login(data, client):
    from db_handle import check_credentials
    username = data[1]
    password = data[2]
    client.send(check_credentials(username, password).encode())


def add_subject(data, client):
    from db_handle import select_data, insert_data
    if select_data('subjects', 'id', f'name = {data[1]}'):
        client.send(b'exists')
    else:
        insert_data('subjects', 'name, max_hours_per_day', (data[1], data[2]))
        client.send(b'success')


def get_and_send_subjects(client):
    from db_handle import select_data
    subjects: list[tuple] = select_data('subjects', '*')
    if subjects:
        with open('subjects.json', 'w') as f:
            json.dump(subjects, f)
        file_size = os.path.getsize('subjects.json')
        client.send(bin(file_size))
        with open('subjects.json', 'rb') as f:
            client.send(f.read())
    else:
        client.send(b'no subjects found')


def add_teacher(data, client):
    from db_handle import select_data, insert_data
    if select_data('users', 'id', f'name = {data[1]} AND is_teacher = true'):
        client.send(b'exists')
    else:
        work_hours = [[True for i in range(data[4])] for day in range(5)]
        work_hours.append([True for i in range(data[5])])
        work_hours[data[3]] = [False for i in range(len(work_hours[data[3]]))]
        insert_data('users', 'name, sub_id, work_hours, is_teacher, password', (data[1], data[2], work_hours, True, data[6]))
        client.send(b'success')


def client_handle(client_object):
    while True:
        data = client_object.recv(1024).decode().split(',')

        if data[0] == 'Login':
            login(data, client_object)

        elif data[0] == 'add_subject':
            add_subject(data, client_object)

        elif data[0] == 'get_subjects':
            get_and_send_subjects(client_object)
        elif data[0] == 'add_teacher':
            add_teacher(data, client_object)


if __name__ == '__main__':
    while True:
        client_obj, ip = server_socket.accept()
        Thread(target=client_handle, args=(client_obj,)).start()
        clients[client_obj] = ip
