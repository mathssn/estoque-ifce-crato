import sqlite3 as sq
import os.path
from contextlib import contextmanager


@contextmanager
def connect_db():
    conn = sq.connect('database/db.db')
    try:
        yield conn, conn.cursor()
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def create_database():
    
    if not os.path.exists('database/db.db'):
        with connect_db() as (conn, cursor):

            with open('database/sql/schema.sql', encoding='utf-8') as file:
                comands = file.read().split(';')
            
            for comand in comands:
                cursor.execute(comand)

            with open('database/sql/insert.sql', encoding='utf-8') as file:
                comands = file.read().split(';')
            
            for comand in comands:
                cursor.execute(comand)
                