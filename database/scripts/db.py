import sqlite3 as sq
import mysql.connector as mysql
from mysql.connector import errorcode
import os.path
from contextlib import contextmanager


@contextmanager
def connect_db():
    conn = mysql.connect(
        host='localhost',
        user='root',
        password='1234',
        database='estoque_ifce'
    )
    cursor: mysql.connection.MySQLCursor = conn.cursor()

    try:
        yield conn, cursor
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def create_database(db_name: str):
    try:
        conn = mysql.connect(
            host='localhost',
            user='root',
            password='1234'
        )
        cursor = conn.cursor()

        cursor.execute('SHOW DATABASES LIKE %s', (db_name,))
        row = cursor.fetchone()

        if not row:
            cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.database = db_name

            with open('database/sql/schema.sql', encoding='utf-8') as file:
                comands = file.read().split(';')
            
            for comand in comands:
                cursor.execute(comand.strip())

            with open('database/sql/insert.sql', encoding='utf-8') as file:
                comands = file.read().split(';')
            
            for comand in comands:
                cursor.execute(comand.strip())
        
        conn.commit()

    except mysql.connection.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro: usuário ou senha inválidos.")
        else:
            print(err)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
