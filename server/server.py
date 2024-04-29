import socket
import json
import os
from threading import Thread
from common import encode_password, Enum
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET =Ipv4 | SOCK_STREAM- TCP

server_socket.bind(('127.0.0.1', 5050))
server_socket.listen()

clients = {}


def login(data, client):
    from db_handle import select_data
    username = data[1]
    password = data[2]

    user = select_data('users', '*', {'name': username})

    if user:
        user = user[0]

        if username not in user:
            client.send(b'Invalid username')

        elif encode_password(password) in user:
            if (True in user) and (1 not in user):
                client.send(b'true')
            client.send(b'admin')
        else:
            client.send(b'Invalid password')
    else:
        client.send(b'one or more of the fields are empty')


def add_lessons(data, client):
    from db_handle import insert_dataframe
    file_size = data[1]
    lessons_json = client.recv(int(file_size)).decode()
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', lessons_json)
    lessons = json.loads(lessons_json)
    df = {'hour':[], 'day':[], 'classroom_id':[], 'teacher_id':[], 'grade_id':[]}
    for lesson in lessons:
        hour = lesson[0]
        day = lesson[1]
        classroom_id = lesson[2]
        teacher_id = lesson[3]
        grade_id = lesson[4]
        df['hour'].append(hour); df['day'].append(day); df['classroom_id'].append(classroom_id); df['teacher_id'].append(teacher_id); df['grade_id'].append(grade_id)
    insert_dataframe(df)
    client.send(Enum.SUCCESS.encode())


def add_subject(data, client):
    from db_handle import select_data, insert_data
    if select_data('subjects', 'id', {'name': data[1]}):
        client.send(Enum.EXISTS.encode())
    else:
        insert_data('subjects', 'name, max_hours_per_day', (data[1], data[2]))
        new_sub_id = str(select_data('subjects', 'id', {'name': data[1]})[0][0])
        client.send(new_sub_id.encode())


def get_and_send_subjects(client):
    from db_handle import select_data
    subjects: list[tuple] = select_data('subjects', '*')
    if subjects:
        with open('jsons/subjects.json', 'w') as f:
            json.dump(subjects, f)
        file_size = str(os.path.getsize('jsons/subjects.json'))
        client.send(file_size.encode())
        with open('jsons/subjects.json', 'rb') as f:
            client.send(f.read())
    else:
        client.send(b'no subjects found')


def add_teacher(data, client):
    from db_handle import select_data, insert_data
    if select_data('users', 'id', {'name': data[1], 'AND': None, 'is_teacher': True}):
        client.send(Enum.EXISTS.encode())
    else:
        work_hours = [[True for i in range(int(data[4]))] for day in range(5)]
        work_hours.append([True for i in range(int(data[5]))])
        work_hours[int(data[3])-1] = [False for i in range(len(work_hours[int(data[3])-1]))]

        with open('jsons/work_hours.json', 'w') as f:
            json.dump(work_hours, f)

        with open('jsons/work_hours.json', 'r') as f:
            work_hours_json = f.read()

        insert_data('users', 'name, is_teacher, password, work_hours_json, subject_id', (data[1], 'true', encode_password(data[6]), work_hours_json, data[2]))
        new_teacher_id = str(select_data('users', 'id', {'name': data[1]})[0][0])
        client.send(new_teacher_id.encode())


def get_and_send_teachers(client):
    from db_handle import select_data
    teachers: list[tuple] = select_data('users AS u JOIN public.subjects AS s on u.subject_id = s.id', 'u.*, s.name as subject_name')
    if teachers:
        with open('jsons/teachers.json', 'w') as f:
            json.dump(teachers, f)
        file_size = str(os.path.getsize('jsons/teachers.json'))
        client.send(file_size.encode())
        with open('jsons/teachers.json', 'rb') as f:
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
        client.send(Enum.EXISTS.encode())

    else:
        insert_data('grades', 'name, hours_per_subject', (grade_name, hours_per_subject))
        add_classroom([Enum.ADD_CLASSROOM, grade_name, False], client)


def get_and_send_grades(client):
    from db_handle import select_data

    grades: list[tuple] = select_data('Grades', '*')

    if grades:
        with open('jsons/grades.json', 'w') as f:
            json.dump(grades, f)
            print(grades)
        file_size = str(os.path.getsize('jsons/grades.json'))
        client.send(file_size.encode())
        with open('jsons/grades.json', 'rb') as f:
            client.send(f.read())
    else:
        client.send(b'no grades found')


def add_classroom(data, client):
    from db_handle import select_data, insert_data
    classroom_name = data[1]

    available = [[True for i in range(11)] for day in range(6)]
    if select_data('classrooms', 'name', {'name': classroom_name}):
        if data[2]:
            client.send(Enum.EXISTS.encode())
        else:
            client.send(Enum.SUCCESS.encode())

    else:
        with open('jsons/available_hours.json', 'w') as f:
            json.dump(available, f)

        with open('jsons/available_hours.json', 'r') as f:
            available = f.read()

        insert_data('classrooms', 'name, available', (classroom_name, available))
        client.send(Enum.SUCCESS.encode())


def get_and_send_classrooms(client):
    from db_handle import select_data

    classrooms: list[tuple] = select_data('Classrooms', '*')

    if classrooms:
        with open('jsons/classrooms.json', 'w') as f:
            json.dump(classrooms, f)
            print(classrooms)
        file_size = str(os.path.getsize('jsons/classrooms.json'))
        client.send(file_size.encode())
        with open('jsons/classrooms.json', 'rb') as f:
            client.send(f.read())
    else:
        client.send(b'no classrooms found')


def flask_login(data, client):
    from db_handle import select_data
    if select_data('users', 'id', {'name': data[1], 'AND': None, 'is_teacher': True}):
        client.send(Enum.SUCCESS.encode())
    else:
        client.send(Enum.FAIL.encode())


def flask_handle(client_object):

    while True:

        data = client_object.recv(1024).decode().split(',')

        if data[0] == Enum.LOGIN_INFO:
            flask_login(data, client_object)


def client_handle(client_object):

    while True:
        data = client_object.recv(1024).decode().split(',')

        if data[0] == Enum.FLASK:
            flask_handle(client_object)

        elif data[0] == Enum.LOGIN_INFO:
            login(data, client_object)

        elif data[0] == Enum.ADD_LESSONS:
            add_lessons(data, client_object)

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

        elif data[0] == Enum.GET_GRADES:
            get_and_send_grades(client_object)

        elif data[0] == Enum.ADD_CLASSROOM:
            add_classroom(data, client_object)

        elif data[0] == Enum.GET_CLASSROOMS:
            get_and_send_classrooms(client_object)


if __name__ == '__main__':
    while True:
        client_obj, ip = server_socket.accept()
        Thread(target=client_handle, args=(client_obj,)).start()
        clients[client_obj] = ip