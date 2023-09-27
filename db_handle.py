# Create a SQLite database
import psycopg2
from common import encode_password

# TODO: figure out database structure and how to store complete schedules and different objects in it
# TODO: build database (complete Grades Table)


def create_database(curs):

    curs.execute('''CREATE TABLE IF NOT EXISTS users (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        username text UNIQUE,
        password text
    )''')

    curs.execute('''CREATE TABLE IF NOT EXISTS Classrooms (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Class text unique
            Available boolean[][]
    )''')

    curs.execute('''CREATE TABLE IF NOT EXISTS Subjects (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name text unique
                max_hours_in_a_day integer
    )''')

    curs.execute('''CREATE TABLE IF NOT EXISTS teachers (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name text
                subject text
                work_hours boolean[][]
    )''')

    curs.execute('''CREATE TABLE IF NOT EXISTS Grades (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name text
                
    )''')


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


conn = psycopg2.connect(host='127.0.0.1', database="SSM", user='postgres', password='1098qpoi')
cursor = conn.cursor()
# Create a table for user credentials
# TODO: complete Lesson TYPE
cursor.execute('''
CREATE TYPE Lesson AS(
        Hour integer
        day integer
        
)''')
create_database(cursor)

# Add some sample users
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", encode_password("admin")))
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("itay", encode_password("lisker")))

conn.commit()
