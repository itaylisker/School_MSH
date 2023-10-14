import socket
import json
import os
from threading import Thread
from common import encode_password, Enum
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
    if select_data('subjects', 'id', {'name': data[1]}):
        client.send(b'exists')
    else:
        insert_data('subjects', 'name, max_hours_per_day', (data[1], data[2]))
        new_sub_id = str(select_data('subjects', 'id', {'name': data[1]})[0][0])
        client.send(new_sub_id.encode())


def get_and_send_subjects(client):
    from db_handle import select_data
    subjects: list[tuple] = select_data('subjects', '*')
    if subjects:
        with open('server/jsons/subjects.json', 'w') as f:
            json.dump(subjects, f)
        file_size = str(os.path.getsize('server/jsons/subjects.json'))
        client.send(file_size.encode())
        with open('server/jsons/subjects.json', 'rb') as f:
            client.send(f.read())
    else:
        client.send(b'no subjects found')


def add_teacher(data, client):
    from db_handle import select_data, insert_data
    if select_data('users', 'id', {'name': data[1], 'AND': None, 'is_teacher': True}):
        client.send(b'exists')
    else:
        work_hours = [[True for i in range(int(data[4]))] for day in range(5)]
        work_hours.append([True for i in range(int(data[5]))])
        work_hours[int(data[3])-1] = [False for i in range(len(work_hours[int(data[3])-1]))]

        with open('server/jsons/work_hours.json', 'w') as f:
            json.dump(work_hours, f)

        with open('server/jsons/work_hours.json', 'r') as f:
            work_hours_json = f.read()

        insert_data('users', 'name, is_teacher, password, work_hours_json, subject_id', (data[1], 'true', encode_password(data[6]), work_hours_json, data[2]))
        new_teacher_id = str(select_data('users', 'id', {'name': data[1]})[0][0])
        client.send(new_teacher_id.encode())


def get_and_send_teachers(client):
    from db_handle import select_data
    teachers: list[tuple] = select_data('users AS u JOIN public.subjects AS s on u.subject_id = s.id', 'u.*, s.name as subject_name')
    if teachers:
        with open('server/jsons/teachers.json', 'w') as f:
            json.dump(teachers, f)
        file_size = str(os.path.getsize('server/jsons/teachers.json'))
        client.send(file_size.encode())
        with open('server/jsons/teachers.json', 'rb') as f:
            client.send(f.read())
    else:
        client.send(b'no teachers found')


def add_grade(data, client):
    from db_handle import select_data, insert_data
    file_size = data[1]

    grade = client.recv(int(file_size)+1024).decode().split('|')  # json file size plus extra for grade name
    grade_name = grade[0]
    hours_per_subject = grade[1]

    if select_data('grades', 'name', {'name': grade_name, 'AND': None}):
        client.send(b'exists')

    else:
        insert_data('grades', 'name, hours_per_subject', (grade_name, hours_per_subject))
        client.send(b'success')


def client_handle(client_object):
    while True:
        data = client_object.recv(1024).decode().split(',')

        if data[0] == Enum.LOGIN_INFO:
            login(data, client_object)

        elif data[0] == Enum.ADD_SUBJECT:
            add_subject(data, client_object)

        elif data[0] == Enum.GET_SUBJECTS:
            get_and_send_subjects(client_object)

        elif data[0] == Enum.ADD_TEACHER:
            add_teacher(data, client_object)

        elif data[0] == Enum.GET_TEACHERS:
            get_and_send_teachers(client_object)

        elif data[0] == Enum.ADD_GRADE:
            add_grade(data, client_object)


if __name__ == '__main__':
    while True:
        client_obj, ip = server_socket.accept()
        Thread(target=client_handle, args=(client_obj,)).start()
        clients[client_obj] = ip
