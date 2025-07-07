import sqlite3 as sq
import os.path


def connect_db():
    conn = sq.connect('database/db.db')
    cursor = conn.cursor()

    return conn, cursor

def create_database():
    
    if not os.path.exists('database/db.db'):
        conn, cursor = connect_db()

        with open('database/sql/schema.sql', encoding='utf-8') as file:
            comands = file.read().split(';')
        
        for comand in comands:
            cursor.execute(comand)
            conn.commit()
        
        conn.close()
