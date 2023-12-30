from tkinter import messagebox
from objects import Teacher, Grade, Subject
from common import Enum
import windows
import socket
import json
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5050))


def close_connection(window):
    window.destroy()
    client_socket.close()


# Function to check login credentials
def check_credentials(window, username_entry, password_entry):

    username = username_entry.get()
    password = password_entry.get()
    credentials = f'{Enum.LOGIN_INFO},{username},{password}'

    client_socket.send(credentials.encode())
    cred_check = client_socket.recv(1024).decode()

    if cred_check == 'admin':
        windows.MainApplicationAdmin()
        window.destroy()
    elif cred_check == 'Invalid username':
        messagebox.showerror("login failed", "Username Doesn't Exist")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
    elif cred_check == 'one or more of the fields are empty':
        messagebox.showerror("login failed", "One Or More Of The Fields Are Empty")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
    else:
        messagebox.showerror("login failed", "Wrong Password")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')


def add_subject(subject_name_entry, max_hours_entry, window, parent, subjects):
    #  TODO: insure that max_hours type is int
    subject_name = subject_name_entry.get().title()
    max_hours = max_hours_entry.get()

    if not (subject_name and max_hours):
        messagebox.showerror("Input Error", "Both Fields Must Be Filled.")
    else:
        subject = f'{Enum.ADD_SUBJECT},{subject_name},{max_hours}'
        client_socket.send(subject.encode())
        response = client_socket.recv(1024).decode()
        if response == Enum.EXISTS:
            messagebox.showerror("Input Error", "Subject Already Exists.")
            subject_name_entry.delete(0, 'end')
            max_hours_entry.delete(0, 'end')
        else:

            if type(subjects) != dict:
                subjects = {}
            subjects[int(response)] = Subject(subject_name, max_hours)

            messagebox.showinfo('successfully added', 'Subject Added Successfully')
            window.destroy()
            parent.create_main_app_frame()


def get_subjects():
    client_socket.send(f'{Enum.GET_SUBJECTS}'.encode())
    file_size = client_socket.recv(1024).decode()
    if file_size == 'no subjects found':
        messagebox.showerror("Input Error", "There Are No Subjects In The System")
        return 'no subjects found'
    else:
        subjects = json.loads(client_socket.recv(int(file_size)).decode())  # Convert json string to list[list]
        subjects_dict = {}
        for subject in subjects:
            subjects_dict[subject[0]] = Subject(subject[1], subject[2])
        return subjects_dict


def add_teacher(teacher_name_entry, teacher_password_entry, teacher_subject_id, teacher_day_off_number, teacher_max_hours_day_entry, teacher_max_hours_friday_entry, window, parent, teachers, subjects):
    teacher_name = teacher_name_entry.get().title()
    teacher_day_off = teacher_day_off_number+1
    teacher_max_hours_day = int(teacher_max_hours_day_entry.get())
    teacher_max_hours_friday = int(teacher_max_hours_friday_entry.get())

    print(f'''{teacher_name} , 
                    {teacher_subject_id} , 
                    {teacher_day_off} , 
                    {teacher_max_hours_day} , 
                    {teacher_max_hours_friday}''')

    if not (teacher_name and teacher_subject_id and teacher_day_off and teacher_max_hours_day and teacher_max_hours_friday):
        messagebox.showerror("Input Error", "All fields must be filled.")

    else:
        teacher = f'{Enum.ADD_TEACHER},{teacher_name},{teacher_subject_id},{teacher_day_off},{teacher_max_hours_day},{teacher_max_hours_friday},{teacher_password_entry.get()}'
        client_socket.send(teacher.encode())
        response = client_socket.recv(1024).decode()
        if response == Enum.EXISTS:
            messagebox.showerror("Input Error", "Teacher With This Name already exists.")
        else:
            data = teacher.split(',')
            work_hours = [[True for i in range(int(data[4]))] for day in range(5)]
            work_hours.append([True for i in range(int(data[5]))])
            work_hours[int(data[3]) - 1] = [False for i in range(len(work_hours[int(data[3]) - 1]))]
            try:
                if type(teachers) != dict:
                    teachers = {}
                teachers[int(response)] = Teacher(teacher_name, subjects[teacher_subject_id].name, work_hours)
            finally:
                messagebox.showinfo('successfully added', 'Teacher Added Successfully')
                window.destroy()
                parent.create_main_app_frame()


def get_teachers():
    client_socket.send(f'{Enum.GET_TEACHERS}'.encode())
    file_size = client_socket.recv(1024).decode()
    if file_size == 'no teachers found':
        messagebox.showerror("Input Error", "There Are No Teachers In The System")
        return 'no teachers found'
    else:
        teachers = json.loads(client_socket.recv(int(file_size)).decode())  # Convert json string to list[list]
        teachers_dict = {}
        for teacher in teachers:

            teachers_dict[teacher[0]] = Teacher(teacher[1], teacher[-1], teacher[4])
        return teachers_dict


def add_grade(grade_name_entry, hours_per_subject_dict, window, parent):
    from os import path
    grade_name = grade_name_entry.get().title()

    with open('client/jsons/hours_per_subject.json', 'w') as f:
        json.dump(hours_per_subject_dict, f)
    file_size = str(path.getsize('client/jsons/hours_per_subject.json'))
    size_text = f'{Enum.ADD_GRADE},{file_size}'
    client_socket.send(size_text.encode())
    with open('client/jsons/hours_per_subject.json', 'r') as f:
        hours_per_subject_str = f.read()

    grade = f'{grade_name}|{hours_per_subject_str}'
    client_socket.send(grade.encode())
    response = client_socket.recv(1024).decode()
    if response == Enum.EXISTS:
        messagebox.showerror("Input error", "Grade with this name already exists.")
        window.destroy()
        parent.deiconify()
    else:
        messagebox.showinfo('Successfully added', 'Grade added successfully')


def add_classroom():
    pass


if __name__ == "__main__":
    windows.LoginWindow()
