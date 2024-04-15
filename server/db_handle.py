# Create a SQLite database
import psycopg2
from common import encode_password


def connect():
    return psycopg2.connect(host='127.0.0.1', database="postgres", user='postgres', password='1098qpoi')


def insert_data(table: str, columns: str, data: tuple):
    conn = connect()
    with conn.cursor() as cursor:
        values_tuple = ','.join(['%s' for value in data])
        try:
            cursor.execute(f'''INSERT INTO public.{table}({columns}) VALUES ({values_tuple});''', data)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print(f'''INSERT INTO public.{table}({columns}) VALUES ({values_tuple});''' % data)

    conn.close()


def delete_data(table: str, where: dict):
    conn = connect()
    with conn.cursor() as cursor:

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
    conn.close()


def select_data(From: str, select: str, where: dict = None):
    conn = connect()
    with conn.cursor() as cursor:

        try:
            if where:
                s = ''
                for i in where.keys():
                    if i == 'AND':
                        s += ' AND'
                    else:
                        s += f'{i}=%s'
                data = tuple([i for i in where.values()])
                cursor.execute(f'''SELECT {select} FROM public.{From} WHERE {s};''', data)
                return cursor.fetchall()
            else:
                cursor.execute(f'''SELECT {select} FROM public.{From};''')
                return cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    conn.close()
