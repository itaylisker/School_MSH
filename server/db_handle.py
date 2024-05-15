# Create a SQLite database
import psycopg2
import pandas as pd
from sqlalchemy import create_engine


def connect():
    """

    :return: connects to database.
    """
    return psycopg2.connect(host='127.0.0.1', database="postgres", user='postgres', password='1098qpoi')


def insert_dataframe(data: dict):
    """

    :param data: dataframe of data to insert into the database --> dict{column: list[data]}
    :return: insert dataframe into the database.
    """
    conn_string = 'postgresql://postgres:1098qpoi@127.0.0.1/postgres'

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
    """

    :param table: table name --> str
    :param columns: column names --> str
    :param data: data to add --> tuple(data)
    :return: inserts the data to the specified table.
    """
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
    """

    :param table: table name -->str
    :param where: dict containing column and data to compare --> dict{column_name: data}
    :return: deletes the data from the specified table.
    """
    conn = connect()
    with conn.cursor() as cursor:

        try:
            s = ''
            for i in where.keys():
                s += f'{i}=%s AND '
            s = s[:-5]
            data = tuple([i for i in where.values() if i])
            print(f'''DELETE FROM public.{table} WHERE {s};''' % data)
            cursor.execute(f'''DELETE FROM public.{table} WHERE {s};''', data)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    conn.close()


def select_data(From: str, select: str, where: dict = None):
    """

    :param From:  table_name --> str
    :param select: column_names --> str
    :param where: dict containing column and data to compare --> dict{column_name: data}
    :return: result of select query.
    """
    conn = connect()
    with conn.cursor() as cursor:

        try:
            if where:
                s = ''
                for i in where.keys():
                    s += f'{i}=%s AND '
                s = s[:-5]
                print(s)
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
    """

    :param table_name: table name --> str
    :param update_values: dict containing column and data to set --> dict{column_name: data}
    :param where_clause: where clause --> str
    :return: updates specified values in specified table.
    """
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
