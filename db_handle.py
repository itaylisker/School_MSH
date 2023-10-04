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
        print(f'''INSERT INTO public.{table}({columns}) VALUES ({values_tuple});''' % data)


def delete_data(table: str, where: dict):
    try:
        s = ''
        for i in where.keys():
            if i == 'AND':
                s += ' AND'
            else:
                s += f'{i}=%s'
        data = tuple([i for i in where.values() if i])
        cursor.execute(f'''DELETE FROM public.{table} WHERE {s};''', data)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def select_data(table: str, select: str, where: dict = None):
    try:
        if where:
            s = ''
            for i in where.keys():
                if i == 'AND':
                    s += ' AND'
                else:
                    s += f'{i}=%s'
            data = tuple([i for i in where.values()])
            cursor.execute(f'''SELECT {select} FROM public.{table} WHERE {s};''', data)
            return cursor.fetchall()
        else:
            cursor.execute(f'''SELECT {select} FROM public.{table};''')
            return cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def check_credentials(username, password):
    user = select_data('users', '*', {'name': username})

    if user:
        user = user[0]
        print (f'''{user} 
{username not in user}
{password in user}
{True in user}''')
        if username not in user:
            return 'Invalid username'

        elif password in user:
            print('got here')
            if (True in user) and (1 not in user):
                return 'true'
            return 'admin'
        else:
            return 'Invalid password'
    else:
        return 'one or more of the fields are empty'
