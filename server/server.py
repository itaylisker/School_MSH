import socket
import json
from threading import Thread
from common import encode_password, decrypt_message, encrypt_message, Enum
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET =Ipv4 | SOCK_STREAM- TCP

server_socket.bind(('127.0.0.1', 5050))
server_socket.listen()

clients = {}


def login(data, client):
    """

    :param data: data to login --> list[str]
    :param client: client_object --> socket.socket
    :return: checks if credentials typed by user match credentials in database and sends corresponding message to client.
    """
    print("Login: ", type(client))
    from db_handle import select_data
    username = data[1]
    password = data[2]

    user = select_data('users', '*', {'name': username})

    if user:
        user = user[0]
        if username != user[1]:
            client.send(encrypt_message('Invalid username'))

        elif encode_password(password) == user[3]:

            if user[2]:

                client.send(encrypt_message(f'{Enum.SUCCESS}'))
            elif not user[2]:
                client.send(encrypt_message(f'{Enum.ADMIN}'))
        else:
            client.send(encrypt_message('Invalid password'))
    else:
        client.send(encrypt_message('one or more of the fields are empty'))


def add_lessons(data, client):
    """

    :param data: size of the data --> list[str, int]
    :param client: client_object --> socket.socket
    :return: adds lessons to database and updates teachers and classrooms in database.
    """
    from db_handle import insert_dataframe, update_table
    file_size = data[1]
    lessons_json = decrypt_message(client.recv(int(file_size))).split('|')
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', lessons_json)

    lessons = json.loads(lessons_json[0])
    print('llllllllllllllllllllllllllllll', lessons)
    teachers = json.loads(lessons_json[1])
    print('ttttttttttttttttttttttttttttttttttttttttttttttttttttt', teachers)
    classrooms = json.loads(lessons_json[2])
    print('cccccccccccccccccccccccccccccccccccccccccccccccc', classrooms)
    df = {'hour': [], 'day': [], 'classroom_id': [], 'teacher_id': [], 'grade_id': []}

    for lesson in lessons:
        hour = lesson[0]
        day = lesson[1]
        classroom_id = lesson[2]
        teacher_id = lesson[3]
        grade_id = lesson[4]
        df['hour'].append(hour); df['day'].append(day); df['classroom_id'].append(classroom_id); df['teacher_id'].append(teacher_id); df['grade_id'].append(grade_id)
    insert_dataframe(df)

    for teacher_id, teacher_work_hours in teachers.items():
        update_table('users', {'work_hours_json': json.dumps(teacher_work_hours)}, f'id = {teacher_id}')

    for classroom_id, classroom_availability in classrooms.items():
        update_table('classrooms', {'available': json.dumps(classroom_availability)}, f'id = {classroom_id}')
    client.send(encrypt_message(Enum.SUCCESS))


def get_and_send_send_lessons(client):
    """

    :param client: client_object --> socket.socket
    :return: get lessons from database and sends them in json format to client.
    """
    from db_handle import join_lessons
    lessons = join_lessons()
    file_size = str(len(encrypt_message(json.dumps(lessons))))
    client.send(encrypt_message(file_size))
    client.send(encrypt_message(json.dumps(lessons)))


def add_subject(data, client):
    """

    :param data: data of subject to add --> list[str, int]
    :param client: client_object --> socket.socket
    :return: checks if subject in database, if not, adds subject to database, if in, sends corresponding message.
    """
    from db_handle import select_data, insert_data
    if select_data('subjects', 'id', {'name': data[1]}):
        client.send(encrypt_message(Enum.EXISTS))
    else:
        insert_data('subjects', 'name, max_hours_per_day', (data[1], data[2]))
        new_sub_id = str(select_data('subjects', 'id', {'name': data[1]})[0][0])
        client.send(encrypt_message(new_sub_id))


def get_and_send_subjects(client):
    """

    :param client: client_object --> socket.socket
    :return: gets subjects from database and sends them in json format to client.
    """
    from db_handle import select_data
    subjects: list[tuple] = select_data('subjects', '*')
    if subjects:
        file_size = str(len(encrypt_message(json.dumps(subjects))))
        client.send(encrypt_message(file_size))
        client.send(encrypt_message(json.dumps(subjects)))
    else:
        client.send(b'no subjects found')


def delete_subject(data, client):
    """

    :param data: data of subject to delete --> list[str, int]
    :param client: client_object --> socket.socket
    :return: deletes subject from database.
    """
    from db_handle import delete_data
    subject_id = data[1]
    delete_data('subjects', {'id': subject_id})
    print('deleteddddddddddddddddddddddddddddddddddddddd')
    client.send(encrypt_message(Enum.SUCCESS))


def add_teacher(data, client):
    """

    :param data: data of teacher to add --> list[str, int]
    :param client: client_object --> socket.socket
    :return: checks if teacher in database, if not, adds teacher to database, if in, sends corresponding message.
    """
    from db_handle import select_data, insert_data
    if select_data('users', 'id', {'name': data[1], 'is_teacher': True}):
        client.send(encrypt_message(Enum.EXISTS))
    else:
        work_hours = [[True for i in range(int(data[4]))] for day in range(5)]
        work_hours.append([True for i in range(int(data[5]))])
        work_hours[int(data[3])-1] = [False for i in range(len(work_hours[int(data[3])-1]))]

        insert_data('users', 'name, is_teacher, password, work_hours_json, subject_id', (data[1], 'true', encode_password(data[6]), json.dumps(work_hours), data[2]))
        insert_data('default_teachers', 'name, is_teacher, password, subject_id, work_hours_json', (data[1], 'true', encode_password(data[6]), data[2], json.dumps(work_hours)))
        new_teacher_id = str(select_data('users', 'id', {'name': data[1]})[0][0])
        client.send(encrypt_message(new_teacher_id))


def get_and_send_teachers(client, original=False):
    """

    :param client: client_object --> socket.socket
    :param original: flag indicating if should get original teachers or scheduled teachers --> bool
    :return: gets teachers from database and sends them in json format to client.
    """
    from db_handle import select_data
    if original:
        teachers: list[tuple] = select_data('default_teachers AS u JOIN public.subjects AS s on u.subject_id = s.id', 'u.*, s.name as subject_name')
    else:
        teachers: list[tuple] = select_data('users AS u JOIN public.subjects AS s on u.subject_id = s.id', 'u.*, s.name as subject_name')

    if teachers:
        file_size = str(len(encrypt_message(json.dumps(teachers))))
        client.send(encrypt_message(file_size))
        client.send(encrypt_message(json.dumps(teachers)))
    else:
        client.send(b'no teachers found')


def delete_teacher(data, client):
    """

    :param data: data of teacher to delete --> list[str, int]
    :param client: client_object --> socket.socket
    :return: deletes teacher from database.
    """
    from db_handle import delete_data
    delete_data('users', {'name': data[1]})
    delete_data('default_teachers', {'name': data[1]})
    client.send(encrypt_message(Enum.SUCCESS))


def add_grade(data, client):
    """

    :param data: data of grade to add --> list[str, int]
    :param client: client_object --> socket.socket
    :return: checks if grade in database, if not, adds grade to database, if in, sends corresponding message.
    """
    from db_handle import select_data, insert_data
    file_size = data[1]

    grade = decrypt_message(client.recv(int(file_size)+4096)).split('|')  # json file size plus extra for grade name
    grade_name = grade[0]
    max_hours_day = grade[1]
    max_hours_friday = grade[2]
    hours_per_subject = grade[3]

    if select_data('grades', 'name', {'name': grade_name}):
        client.send(encrypt_message(Enum.EXISTS))

    else:
        insert_data('grades', 'name, hours_per_subject, max_hours_per_day, max_hours_per_friday', (grade_name, hours_per_subject, max_hours_day, max_hours_friday))
        add_classroom([Enum.ADD_CLASSROOM, grade_name, False], client, True)
        data_to_send = f"{(select_data('grades', 'id', {'name': grade_name})[0][0], select_data('classrooms', 'id', {'name': grade_name})[0][0])}"
        print('dataaaaaaaaaaaaaaaaaaaa', data_to_send)
        client.send(encrypt_message(data_to_send))


def update_grades(data, client):
    """

    :param data: data of grades to update --> list[str, int]
    :param client: client_object --> socket.socket
    :return: updates the specified grades in the database.
    """
    from db_handle import update_table
    file_size = data[1]
    grades = json.loads(decrypt_message(client.recv(int(file_size))))
    print('gradessssssssssssssssssssssssssssssssssssss', grades)

    for grade_id, hours_per_subject in grades.items():
        update_table('grades', {'hours_per_subject': hours_per_subject}, f'id = {grade_id}')

    print('updatedddddddddddddddddddddddddddddddddddddddddd')
    client.send(encrypt_message(Enum.SUCCESS))


def get_and_send_grades(client):
    """

    :param client: client_object --> socket.socket
    :return: gets grades from database and sends them in json format to client.
    """
    from db_handle import select_data

    grades: list[tuple] = select_data('Grades', '*')

    if grades:
        print(grades)
        file_size = str(len(encrypt_message(json.dumps(grades))))
        client.send(encrypt_message(file_size))
        client.send(encrypt_message(json.dumps(grades)))
    else:
        client.send(b'no grades found')


def delete_grade(data, client):
    """

    :param data: data of grade to delete --> list[str, int]
    :param client: client_object --> socket.socket
    :return: deletes grade and corresponding classroom from database.
    """
    from db_handle import delete_data
    delete_data('grades', {'name': data[1]})
    delete_data('classrooms', {'name': data[1]})
    client.send(encrypt_message(Enum.SUCCESS))


def add_classroom(data, client, with_grade=False):
    """

    :param data: data of classroom to add --> list[str, int]
    :param client: client_object --> socket.socket
    :param with_grade: true if added with grade, false if added by itself --> bool
    :return: checks if classroom in database, if not, adds classroom to database, if in, sends corresponding message.
    """
    from db_handle import select_data, insert_data
    classroom_name = data[1]

    available = [[True for i in range(11)] for day in range(6)]
    if select_data('classrooms', 'name', {'name': classroom_name}):
        if data[2]:
            client.send(encrypt_message(Enum.EXISTS))
        else:
            client.send(encrypt_message(Enum.SUCCESS))

    else:
        insert_data('classrooms', 'name, available', (classroom_name, json.dumps(available)))
        if not with_grade:
            client.send(encrypt_message(Enum.SUCCESS))


def get_and_send_classrooms(client):
    """

    :param client: client_object --> socket.socket
    :return: gets classrooms from database and sends them in json format to client.
    """
    from db_handle import select_data

    classrooms: list[tuple] = select_data('Classrooms', '*')

    if classrooms:
        file_size = str(len(encrypt_message(json.dumps(classrooms))))
        client.send(encrypt_message(file_size))
        client.send(encrypt_message(json.dumps(classrooms)))
    else:
        client.send(b'no classrooms found')


def client_handle(client_object):
    """

    :param client_object:  client_object --> socket.socket
    :return: runs while the client is connected. handles requests from client.
    """
    while True:
        data = decrypt_message(client_object.recv(4096)).split(',')

        if data[0] == Enum.LOGIN_INFO:
            print('Login info: ', data)
            login(data, client_object)

        elif data[0] == Enum.ADD_LESSONS:
            add_lessons(data, client_object)

        elif data[0] == Enum.GET_LESSONS:
            get_and_send_send_lessons(client_object)

        elif data[0] == Enum.ADD_SUBJECT:
            add_subject(data, client_object)

        elif data[0] == Enum.GET_SUBJECTS:
            get_and_send_subjects(client_object)

        elif data[0] == Enum.DELETE_SUBJECT:
            delete_subject(data, client_object)

        elif data[0] == Enum.ADD_TEACHER:
            add_teacher(data, client_object)

        elif data[0] == Enum.GET_TEACHERS:
            print(data, data[-1])
            if data[-1] == 'True':
                print('here')
                get_and_send_teachers(client_object, original=True)
            else:
                get_and_send_teachers(client_object)

        elif data[0] == Enum.DELETE_TEACHER:
            delete_teacher(data, client_object)

        elif data[0] == Enum.ADD_GRADE:
            add_grade(data, client_object)

        elif data[0] == Enum.UPDATE_GRADES:
            update_grades(data, client_object)

        elif data[0] == Enum.GET_GRADES:
            get_and_send_grades(client_object)

        elif data[0] == Enum.DELETE_GRADE:
            delete_grade(data, client_object)

        elif data[0] == Enum.ADD_CLASSROOM:
            add_classroom(data, client_object)

        elif data[0] == Enum.GET_CLASSROOMS:
            get_and_send_classrooms(client_object)


if __name__ == '__main__':
    # accepts clients while server is running and distributes them to threads
    while True:
        client_obj, ip = server_socket.accept()
        Thread(target=client_handle, args=(client_obj,)).start()
        clients[client_obj] = ip
