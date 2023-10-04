from tkinter import messagebox
from objects import Teacher, Grade, Subject
from common import encode_password
import windows
import socket
import json
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5050))

LOGIN_INFO = 'Login'
ADD_SUBJECT = 'add_subject'
GET_SUBJECTS = 'get_subjects'
ADD_TEACHER = 'add_teacher'


# Function to check login credentials
def check_credentials(window, username_entry, password_entry):

    username = username_entry.get()
    password = encode_password(password_entry.get())
    credentials = f'{LOGIN_INFO},{username},{password}'

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


def add_subject(subject_name_entry, max_hours_entry, window, parent):
    subject_name = subject_name_entry.get().title()
    max_hours = max_hours_entry.get()

    if not (subject_name and max_hours):
        messagebox.showerror("Input Error", "Both Fields Must Be Filled.")
    else:
        subject = f'{ADD_SUBJECT},{subject_name},{max_hours}'
        client_socket.send(subject.encode())
        response = client_socket.recv(1024).decode()
        if response == 'exists':
            messagebox.showerror("Input Error", "Subject Already Exists.")
            subject_name_entry.delete(0, 'end')
            max_hours_entry.delete(0, 'end')
        else:
            messagebox.showinfo('successfully added', 'Subject Added Successfully')
            window.destroy()  # Close the window
            parent.deiconify()  # Show the parent window again


def get_subjects():
    client_socket.send(f'{GET_SUBJECTS}'.encode())
    file_size = client_socket.recv(1024).decode()
    if file_size == 'no subjects found':
        messagebox.showerror("Input Error", "There Are No Subjects In The System")
        return 'no subjects found'
    else:
        subjects = json.loads(client_socket.recv(int(file_size)).decode())  # Convert json string to list[list]
        subjects_dict = {}
        for subject in subjects:
            subjects_dict[subject[0]] = subject[1]
        return subjects_dict


def add_teacher(teacher_name_entry, teacher_password_entry, teacher_subject_id, teacher_day_off_number, teacher_max_hours_day_entry, teacher_max_hours_friday_entry, window, parent):
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
        teacher = f'{ADD_TEACHER},{teacher_name},{teacher_subject_id},{teacher_day_off},{teacher_max_hours_day},{teacher_max_hours_friday},{encode_password(teacher_password_entry.get())}'
        client_socket.send(teacher.encode())
        response = client_socket.recv(1024).decode()
        if response == 'exists':
            messagebox.showerror("Input Error", "Teacher With This Name already exists.")
        else:
            messagebox.showinfo('successfully added', 'Teacher Added Successfully')
            window.destroy()  # Close the window
            parent.deiconify()  # Show the parent window again


if __name__ == "__main__":
    windows.LoginWindow()
