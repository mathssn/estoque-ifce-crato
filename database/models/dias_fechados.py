from database.scripts.db import connect_db
import sqlite3

class DiasFechados:
    def __init__(self, data=None, fechado=False):
        self.data = data
        self.fechado = fechado

    def get_tuple(self):
        return (self.data, self.fechado)

    def __str__(self):
        return f"Dia {self.data} {'fechado' if self.fechado else 'aberto'}"

def create(dia: DiasFechados, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            '''INSERT INTO dias_fechados (
                data, fechado
            ) VALUES (?, ?)''',
            dia.get_tuple()
        )
    except sqlite3.Error as e:
        print(e)
        return False

    return True


def list_all(cursor: sqlite3.Cursor):
    cursor.execute('SELECT * FROM dias_fechados ORDER BY data DESC')
    rows = cursor.fetchall()
    dias = [DiasFechados(data=row[0], fechado=bool(row[1])) for row in rows]

    return dias


def get(data, cursor: sqlite3.Cursor):
    cursor.execute('SELECT * FROM dias_fechados WHERE data = ?', (data,))
    row = cursor.fetchone()

    if row:
        return DiasFechados(data=row[0], fechado=bool(row[1]))
    return None


def update(data, dia: DiasFechados, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            '''UPDATE dias_fechados SET 
                fechado = ?
               WHERE data = ?''',
            (dia.fechado, data)
        )
    except sqlite3.Error:
        return False

    return True


def delete(data, cursor: sqlite3.Cursor):
    try:
        cursor.execute('DELETE FROM dias_fechados WHERE data = ?', (data,))
    except sqlite3.Error:
        return False

    return True
