from flask import Flask, request, flash, render_template, url_for, redirect
import os
import socket
from common import Enum
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5050))

app = Flask(__name__)
app.secret_key = os.urandom(32)
client_socket.send(f'{Enum.GET_LESSONS}'.encode())
file_size = client_socket.recv(1024).decode()
lessons = json.loads(client_socket.recv(int(file_size)).decode())
client_socket.send(f'{Enum.GET_GRADES}'.encode())
file_size = client_socket.recv(1024)
grades = json.loads(client_socket.recv(int(file_size)).decode())
client_socket.send(f'{Enum.GET_TEACHERS}'.encode())
file_size = client_socket.recv(1024)
teachers = json.loads(client_socket.recv(int(file_size)).decode())
teachers_names_list = [teacher[1] for teacher in teachers]
grades_names_list = [grade[1] for grade in grades]
lessons_dict_by_grade = {grade_name: [[], [], [], [], [], [], [], [], []] for grade_name in grades_names_list}
lessons_dict_by_teacher = {teacher_name: [[], [], [], [], [], [], [], [], []] for teacher_name in teachers_names_list}
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
print(lessons_dict_by_grade)
print(lessons_dict_by_teacher)


@app.route("/", methods=["GET", "POST"])
def home():
    selected_class = grades_names_list[0]
    selected_class_lessons = lessons_dict_by_grade[selected_class]
    if request.method == "POST":
        selected_class = request.form.get("selectedClass")
        print(selected_class)
        selected_class_lessons = lessons_dict_by_grade[selected_class]

    return render_template("home.html", lessons=selected_class_lessons, classes=grades_names_list, selected_class=selected_class)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        credentials = f'{Enum.LOGIN_INFO},{username},{password}'

        client_socket.send(credentials.encode())
        cred_check = client_socket.recv(1024).decode()
        print('got here: ', cred_check)
        if cred_check == Enum.SUCCESS:
            print('success!!')
            return teacher_schedule(username)
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login_page.html', error=error)

    return render_template('login_page.html')


@app.route('/schedule', methods=['GET', 'POST'])
def teacher_schedule(username):
    selected_teacher = username
    selected_teacher_lessons = lessons_dict_by_teacher[selected_teacher]

    return render_template('schedule.html', lessons=selected_teacher_lessons, teacher=selected_teacher)


if __name__ == '__main__':
    app.run(port=80, debug=True, host='127.0.0.1')
