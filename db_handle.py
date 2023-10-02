# Create a SQLite database
import psycopg2
from common import encode_password

conn = psycopg2.connect(host='127.0.0.1', database="postgres", user='postgres', password='1098qpoi')
cursor = conn.cursor()


def insert_data(table: str, columns: str, data: tuple):
    values_tuple = ','.join(['%s' for value in data])
    try:
        cursor.execute(f'''INSERT INTO public.{table}({columns}) VALUES ({values_tuple});''', data)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def delete_data(table: str, where: str):
    try:
        cursor.execute(f'''DELETE FROM public.{table} WHERE {where};''')
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def select_data(table: str, select: str, where: str = None):
    try:
        if where:
            cursor.execute(f'''SELECT {select} FROM public.{table} WHERE {where};''')
            return cursor.fetchall()
        else:
            cursor.execute(f'''SELECT {select} FROM public.{table};''')
            return cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def check_credentials(username, password):
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user:
        if user[1] != username:
            return 'Invalid username'

        elif user[5] == password:
            if user[4]:
                return 'true'
            return 'admin'
        else:
            return 'Invalid password'
    else:
        return 'one or more of the fields are empty'
