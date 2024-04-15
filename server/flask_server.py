from flask import Flask, request, flash, render_template, url_for, redirect
import os
import socket
from common import Enum

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 1111))

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route('/')
def home():
    return redirect(url_for('login_page'))
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        credentials = f'{Enum.FLASK},{username},{password}'

        client_socket.send(credentials.encode())
        cred_check = client_socket.recv(1024).decode()

        if cred_check == Enum.SUCCESS:
            return redirect(url_for("schedule"))
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login_page.html', error=error)

    return render_template('login_page.html')


@app.route('/schedule')
def schedule():
    return render_template('schedule.html')


if __name__ == '__main__':
    app.run(port=80, debug=True, host='127.0.0.1')
