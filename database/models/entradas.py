from database.scripts.db import connect_db
import sqlite3
from database.scripts.utils import recalculate_entries_balance


class Entrada:
    def __init__(self, _id=None, produto_id=None, data_entrada=None, quantidade=None):
        self.id = _id
        self.produto_id = produto_id
        self.data_entrada = data_entrada
        self.quantidade = quantidade

    def get_tuple(self):
        return (self.produto_id, self.data_entrada, self.quantidade)

    def __str__(self):
        return f"Entrada de Produto {self.produto_id} em {self.data_entrada}"


def create(entrada: Entrada) -> bool:
    conn, cursor = connect_db()

    try:
        sucess = recalculate_entries_balance(entrada.data_entrada, entrada)
        if not sucess:
            return False
        cursor.execute(
            'INSERT INTO entradas (produto_id, data_entrada, quantidade) VALUES (?, ?, ?)',
            entrada.get_tuple()
        )
        entrada.id = cursor.lastrowid
        conn.commit()

    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        conn.close()

    return True


def list_all() -> list[Entrada]:
    conn, cursor = connect_db()

    cursor.execute('SELECT * FROM entradas ORDER BY data_entrada DESC')
    rows = cursor.fetchall()
    entradas: list[Entrada] = []

    for row in rows:
        entrada = Entrada(*row)
        entradas.append(entrada)

    conn.close()
    return entradas


def get(_id) -> Entrada:
    conn, cursor = connect_db()

    cursor.execute('SELECT * FROM entradas WHERE id = ?', (_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return Entrada(*row)

    return None


def update(_id, entrada: Entrada) -> bool:
    conn, cursor = connect_db()

    try:
        sucess = recalculate_entries_balance(entrada.data_entrada, entrada, True)
        if not sucess:
            return False
        
        cursor.execute(
            'UPDATE entradas SET produto_id = ?, data_entrada = ?, quantidade = ? WHERE id = ?',
            entrada.get_tuple() + (_id,)
        )
        conn.commit()
    except sqlite3.Error:
        return False
    finally:
        conn.close()

    return True


def delete(_id) -> bool:
    conn, cursor = connect_db()

    try:
        cursor.execute('DELETE FROM entradas WHERE id = ?', (_id,))
        conn.commit()
    except sqlite3.Error:
        return False
    finally:
        conn.close()

    return True


def list_by_date(date: str) -> list[Entrada]:
    conn, cursor = connect_db()

    try:
        cursor.execute(
            'SELECT * FROM entradas WHERE data_entrada = ?',
            (date,)
        )
        rows = cursor.fetchall()
    except sqlite3.Error:
        return []
    finally:
        conn.close()

    entradas = [Entrada(*row) for row in rows]
    return entradas


def list_by_month(month: str, year: str) -> list[Entrada]:
    conn, cursor = connect_db()

    if len(month) == 1:
        month = '0' + month

    try:
        cursor.execute(
            "SELECT * FROM entradas WHERE strftime('%Y', data_entrada) = ? AND strftime('%m', data_entrada) = ?",
            (year, month)
        )
        rows = cursor.fetchall()
    except sqlite3.Error:
        return []
    finally:
        conn.close()

    entradas = [Entrada(*row) for row in rows]
    return entradas
