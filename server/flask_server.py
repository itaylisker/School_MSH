from flask import Flask, request, render_template, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import os
import socket
from common import Enum, encrypt_message, decrypt_message
import json
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5050))

app = Flask(__name__)
app.secret_key = os.urandom(32)
login_manager = LoginManager(app)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# client_socket.send(encrypt_message(f'{Enum.GET_LESSONS}'))
# file_size = decrypt_message(client_socket.recv(4096))
# lessons = json.loads(decrypt_message(client_socket.recv(int(file_size))))
# client_socket.send(encrypt_message(f'{Enum.GET_GRADES}'))
# file_size = decrypt_message(client_socket.recv(4096))
# grades = json.loads(decrypt_message(client_socket.recv(int(file_size))))
# client_socket.send(encrypt_message(f'{Enum.GET_TEACHERS}'))
# file_size = decrypt_message(client_socket.recv(4096))
# teachers = json.loads(decrypt_message(client_socket.recv(int(file_size))))
# teachers_subject = {teacher[1]: teacher[-1] for teacher in teachers}
# teachers_names_list = [teacher[1] for teacher in teachers]
# grades_names_list = [grade[1] for grade in grades]
# lessons_dict_by_grade = {grade_name: [[], [], [], [], [], [], [], [], []] for grade_name in grades_names_list}
# lessons_dict_by_teacher = {teacher_name: [[], [], [], [], [], [], [], [], []] for teacher_name in teachers_names_list}
# for lesson in lessons:
#     hour = lesson[0]
#     day = lesson[1]
#     classroom = lesson[2]
#     teacher = lesson[3]
#     subject = lesson[4]
#     grade = lesson[5]
#     lessons_dict_by_grade[grade][hour].append(lesson[:5])
#     new_lesson = lesson[:3]
#     new_lesson.append(lesson[4])
#     new_lesson.append(lesson[5])
#     lessons_dict_by_teacher[teacher][hour].append(new_lesson)
#
# for key in lessons_dict_by_grade.keys():
#     for lesson in range(9):
#         lessons_dict_by_grade[key][lesson].sort(key=lambda x: x[1])
# for key in lessons_dict_by_teacher.keys():
#     for lesson in range(9):
#         lessons_dict_by_teacher[key][lesson].sort(key=lambda x: x[1])
# print(lessons_dict_by_grade)
# print(lessons_dict_by_teacher)
lessons_dict_by_grade = {}
lessons_dict_by_teacher = {}
teachers_names_list = []
grades_names_list = []
teachers_subject = {}

@app.route('/')
def index():
    return redirect(f'/class/{grades_names_list[0]}')


@app.route("/class/<selected_grade>", methods=["GET", "POST"])
def home(selected_grade=None):
    global grades_names_list, teachers_names_list, lessons_dict_by_teacher, lessons_dict_by_grade, teachers_subject
    logout_user()
    client_socket.send(encrypt_message(f'{Enum.GET_LESSONS}'))
    file_size = decrypt_message(client_socket.recv(4096))
    lessons = json.loads(decrypt_message(client_socket.recv(int(file_size))))
    client_socket.send(encrypt_message(f'{Enum.GET_GRADES}'))
    file_size = decrypt_message(client_socket.recv(4096))
    grades = json.loads(decrypt_message(client_socket.recv(int(file_size))))
    client_socket.send(encrypt_message(f'{Enum.GET_TEACHERS}'))
    file_size = decrypt_message(client_socket.recv(4096))
    teachers = json.loads(decrypt_message(client_socket.recv(int(file_size))))
    teachers_subject = {teacher[1]: teacher[-1] for teacher in teachers}
    teachers_names_list = [teacher[1] for teacher in teachers]
    grades_names_list = [grade[1] for grade in grades]
    lessons_dict_by_grade = {grade_name: [[], [], [], [], [], [], [], [], []] for grade_name in grades_names_list}
    lessons_dict_by_teacher = {teacher_name: [[], [], [], [], [], [], [], [], []] for teacher_name in
                               teachers_names_list}
    for lesson in lessons:
        hour = lesson[0]
        day = lesson[1]
        classroom = lesson[2]
        teacher = lesson[3]
        subject = lesson[4]
        grade = lesson[5]
        lessons_dict_by_grade[grade][hour].append(lesson[:5])
        new_lesson = lesson[:3]
        new_lesson.append(lesson[4])
        new_lesson.append(lesson[5])
        lessons_dict_by_teacher[teacher][hour].append(new_lesson)

    for key in lessons_dict_by_grade.keys():
        for lesson in range(9):
            lessons_dict_by_grade[key][lesson].sort(key=lambda x: x[1])
    for key in lessons_dict_by_teacher.keys():
        for lesson in range(9):
            lessons_dict_by_teacher[key][lesson].sort(key=lambda x: x[1])
    if selected_grade:
        print('no wayyyyyyyyyyyyyyyyyyyyy')
        selected_class = selected_grade
    else:
        selected_class = grades_names_list[0]
    print('selected: ', selected_class)
    selected_class_lessons = lessons_dict_by_grade[selected_class]
    if request.method == "POST":
        selected_class = request.form.get("selectedClass")
        print('selected: ')
        print(selected_class)
        return redirect(url_for('home', selected_grade=selected_class))

    return render_template("home.html", lessons=selected_class_lessons, classes=grades_names_list, selected_class=selected_class)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    logout_user()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        credentials = f'{Enum.LOGIN_INFO},{username},{password}'

        client_socket.send(encrypt_message(credentials))
        cred_check = decrypt_message(client_socket.recv(4096))
        print('got here: ', cred_check)
        if cred_check == Enum.SUCCESS:
            print('success!!')
            user = User(username)
            login_user(user)
            return redirect(url_for('teacher_schedule', username=username))
        elif cred_check == Enum.ADMIN:
            user = User(username)
            login_user(user)
            return redirect(url_for('admin_page'))
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login_page.html', error=error, grades_names_list=grades_names_list)

    return render_template('login_page.html', grades_names_list=grades_names_list)


@app.route('/teacher/<username>')
@login_required
def teacher_schedule(username):
    selected_teacher = username
    selected_teacher_lessons = lessons_dict_by_teacher[selected_teacher]

    return render_template('schedule.html', lessons=selected_teacher_lessons, teacher=selected_teacher, grades_names_list=grades_names_list)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    selected_teacher = teachers_names_list[0]
    print('innnnnnnnnnnnnn')
    print(selected_teacher)
    selected_teacher_lessons = lessons_dict_by_teacher[selected_teacher]
    print(selected_teacher_lessons)

    if request.method == "POST":
        print('outttttttttttttttttttttttttttt')
        selected_teacher = request.form["selectedTeacher"]
        print(selected_teacher)
        selected_teacher_lessons = lessons_dict_by_teacher[selected_teacher]
    print(selected_teacher_lessons)

    return render_template("teachers.html", lessons=selected_teacher_lessons, teachers=teachers_names_list, selected_teacher=selected_teacher, subject=teachers_subject[selected_teacher], grades_names_list=grades_names_list)


if __name__ == '__main__':
    app.run(port=80, debug=True, host=f'0.0.0.0')
