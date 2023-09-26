# Create a SQLite database
import sqlite3
from common import encode_password

# TODO: figure out database structure and how to store complete schedules and different objects in it


def create_database(curs):

    curs.execute('''CREATE TABLE IF NOT EXISTS users (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')

    # cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
    #         ID INTEGER PRIMARY KEY AUTOINCREMENT,
    #         username TEXT UNIQUE,
    #         password TEXT
    #     )''')
    #
    # cursor.execute('''CREATE TABLE IF NOT EXISTS grades (
    #         ID INTEGER PRIMARY KEY AUTOINCREMENT,
    #         username TEXT UNIQUE,
    #         student_amount INTEGER
    #     )''')
    # cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
    #         ID INTEGER PRIMARY KEY AUTOINCREMENT,
    #         username TEXT UNIQUE,
    #         student_amount INTEGER
    #     )''')


def check_credentials(username, password):
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user:
        if user[1] != username:
            return 'Invalid username'

        elif user[2] == password:
            return 'true'
        else:
            return 'Invalid password'
    else:
        return 'one or more of the fields are empty'


conn = sqlite3.connect("SSB.db")
cursor = conn.cursor()
# Create a table for user credentials
create_database(cursor)

# Add some sample users
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", encode_password("admin")))
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("itay", encode_password("lisker")))

conn.commit()
