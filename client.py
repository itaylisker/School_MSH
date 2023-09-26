import tkinter as tk
from tkinter import messagebox
from objects import Teacher, Grade, Subject
from common import encode_password
import windows
import socket
# TODO: multi-client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5050))

LOGIN_INFO = 'Login'

# TODO: lists below this line should be stored in database
hours_per_subject = {}
subjects_list = []
teachers_list = []
grades_list = []
DOW_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


# Function to check login credentials
def check_credentials(window, username_entry, password_entry):

    username = username_entry.get()
    password = encode_password(password_entry.get())
    credentials = f'{LOGIN_INFO},{username},{password}'

    client_socket.send(credentials.encode())
    cred_check = client_socket.recv(1024).decode()

    if cred_check == 'true':
        windows.MainApplication()
        window.destroy()
    elif cred_check == 'Invalid username':
        messagebox.showerror("Login Failed", "username doesn't exist")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
    elif cred_check == 'one or more of the fields are empty':
        messagebox.showerror("Login Failed", "one or more of the fields are empty")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
    else:
        messagebox.showerror("Login Failed", "wrong password")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')


if __name__ == "__main__":
    windows.LoginWindow()
