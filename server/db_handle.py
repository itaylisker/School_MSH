# Create a SQLite database
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from common import encode_password


def connect():
    return psycopg2.connect(host='127.0.0.1', database="postgres", user='postgres', password='postgres')


def insert_dataframe(data: dict):
    conn_string = 'postgresql://postgres:postgres@127.0.0.1/postgres'

    db = create_engine(conn_string)
    conn = db.connect()

    # Create DataFrame
    df = pd.DataFrame(data)
    df.to_sql('lessons', con=conn, if_exists='replace',
              index=False)
    conn = psycopg2.connect(conn_string
                            )
    conn.autocommit = True

    # conn.commit()
    conn.close()


def join_lessons():

    """
    :return: list of tuples, each tuple contains the following:
    [0]-->hour of lesson,
    [1]-->day of lesson,
    [2]-->name of classroom of lesson,
    [3]-->name of teacher of lesson,
    [4]-->name of subject of lesson,
    [5]-->name of grade of lesson
    """
    conn = connect()
    with conn.cursor() as cursor:
        try:
            cursor.execute('''SELECT lessons.hour, lessons.day, classrooms.name as classroom_name, users.name as teacher_name, subjects.name as subject , grades.name as grade_name FROM lessons
                                JOIN users ON lessons.teacher_id = users.id
                                JOIN classrooms ON lessons.classroom_id = classrooms.id
                                JOIN grades ON lessons.grade_id = grades.id
                                JOIN subjects ON subjects.id = users.subject_id''')
            return cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    conn.close()


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
                s += f'{i}=%s AND '
            s = s[:-5]
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
                    s += f'{i}=%s AND '
                s = s[:-5]
                data = tuple([i for i in where.values() if i])
                cursor.execute(f'''SELECT {select} FROM public.{From} WHERE {s};''', data)
                return cursor.fetchall()
            else:
                cursor.execute(f'''SELECT {select} FROM public.{From};''')
                return cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print(f'''SELECT {select} FROM public.{From} WHERE {s};''', data)
    conn.close()


def update_table(table_name: str, update_values: dict, where_clause: str):
    # Connect to the PostgreSQL database
    conn = connect()

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()
    try:

        # Construct the UPDATE query
        update_query = f"UPDATE public.{table_name} SET "

        # Append set values to the update query
        for column, value in update_values.items():
            update_query += f"{column} = %s, "
        update_query = update_query[:-2]  # Remove the trailing comma and space
        update_query += f" WHERE {where_clause};"

        # Construct the parameterized values
        update_values_tuple = tuple([value for value in update_values.values()])
        print(update_query, update_values_tuple)
        # Execute the UPDATE query
        cursor.execute(update_query, update_values_tuple)

        # Commit the transaction
        conn.commit()
        print("Record updated successfully")

    except (Exception, psycopg2.Error) as error:
        print("Error while updating record:", error)

    finally:
        # Close the cursor and connection
        if conn:
            cursor.close()
            conn.close()
