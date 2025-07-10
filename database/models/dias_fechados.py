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

def create(dia: DiasFechados):
    conn, cursor = connect_db()

    try:
        cursor.execute(
            '''INSERT INTO dias_fechados (
                data, fechado
            ) VALUES (?, ?)''',
            dia.get_tuple()
        )
        conn.commit()
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        conn.close()

    return True


def list_all():
    conn, cursor = connect_db()

    cursor.execute('SELECT * FROM dias_fechados ORDER BY data DESC')
    rows = cursor.fetchall()
    dias = [DiasFechados(data=row[0], fechado=bool(row[1])) for row in rows]

    conn.close()
    return dias


def get(data):
    conn, cursor = connect_db()

    cursor.execute('SELECT * FROM dias_fechados WHERE data = ?', (data,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return DiasFechados(data=row[0], fechado=bool(row[1]))
    return None


def update(data, dia: DiasFechados):
    conn, cursor = connect_db()

    try:
        cursor.execute(
            '''UPDATE dias_fechados SET 
                fechado = ?
               WHERE data = ?''',
            (dia.fechado, data)
        )
        conn.commit()
    except sqlite3.Error:
        return False
    finally:
        conn.close()

    return True


def delete(data):
    conn, cursor = connect_db()

    try:
        cursor.execute('DELETE FROM dias_fechados WHERE data = ?', (data,))
        conn.commit()
    except sqlite3.Error:
        return False
    finally:
        conn.close()

    return True
