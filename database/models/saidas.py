from database.scripts.db import connect_db
import sqlite3
from database.scripts.utils import recalculate_exits_balance


class Saida:

    def __init__(self, _id=None, produto_id=None, destino=None, data_saida=None, quantidade=None):
        self.id = _id
        self.produto_id = produto_id
        self.destino = destino
        self.data_saida = data_saida
        self.quantidade = quantidade

    def get_tuple(self):
        return (self.produto_id, self.destino, self.data_saida, self.quantidade)

    def __str__(self):
        return f"Saída de Produto {self.produto_id} para {self.destino} em {self.data_saida}"


def create(saida: Saida) -> bool:
    conn, cursor = connect_db()

    try:
        sucess = recalculate_exits_balance(saida.data_saida, saida)
        if not sucess:
            return False
        
        cursor.execute(
            'INSERT INTO saidas (produto_id, destino, data_saida, quantidade) VALUES (?, ?, ?, ?)',
            saida.get_tuple()
        )
        saida.id = cursor.lastrowid
        conn.commit()
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        conn.close()

    return True


def list_all() -> list[Saida]:
    conn, cursor = connect_db()

    cursor.execute('SELECT * FROM saidas ORDER BY data_saida DESC')
    rows = cursor.fetchall()
    saidas: list[Saida] = []

    for row in rows:
        saida = Saida(*row)
        saidas.append(saida)

    conn.close()
    return saidas


def get(_id) -> Saida:
    conn, cursor = connect_db()

    cursor.execute('SELECT * FROM saidas WHERE id = ?', (_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return Saida(*row)

    return None


def update(_id, saida: Saida) -> bool:
    conn, cursor = connect_db()

    try:
        sucess = recalculate_exits_balance(saida.data_saida, saida, True)
        if not sucess:
            return False
        
        cursor.execute(
            'UPDATE saidas SET produto_id = ?, destino = ?, data_saida = ?, quantidade = ? WHERE id = ?',
            saida.get_tuple() + (_id,)
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
        cursor.execute('DELETE FROM saidas WHERE id = ?', (_id,))
        conn.commit()
    except sqlite3.Error:
        return False
    finally:
        conn.close()

    return True


def list_by_date(date: str) -> list[Saida]:
    conn, cursor = connect_db()

    try:
        cursor.execute(
            'SELECT * FROM saidas WHERE data_saida = ?',
            (date,)
        )
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        return []
    finally:
        conn.close()

    saidas = []
    for row in rows:
        saidas.append(Saida(*row))
    
    return saidas


def list_by_month(month: str, year: str) -> list[Saida]:
    conn, cursor = connect_db()

    if len(month) == 1:
        month = '0' + month

    try:
        cursor.execute(
            "SELECT * FROM saidas WHERE strftime('%Y', data_saida) = ? AND strftime('%m', data_saida) = ?",
            (year, month)
        )
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        return []
    finally:
        conn.close()

    saidas = []
    for row in rows:
        saidas.append(Saida(*row))
    
    return saidas