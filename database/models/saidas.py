import sqlite3
from dataclasses import dataclass
from database.scripts.utils import recalculate_exits_balance


@dataclass
class Saida:
    id: int
    produto_id: int
    destino: str
    data_saida: str
    quantidade: int

    def get_tuple(self):
        return (self.produto_id, self.destino, self.data_saida, self.quantidade)

    def __str__(self):
        return f"Saída de Produto {self.produto_id} para {self.destino} em {self.data_saida}"


def create(saida: Saida, cursor: sqlite3.Cursor):
    try:
        recalculate_exits_balance(saida.data_saida, saida, cursor)        
        cursor.execute(
            'INSERT INTO saidas (produto_id, destino, data_saida, quantidade) VALUES (?, ?, ?, ?)',
            saida.get_tuple()
        )
        saida.id = cursor.lastrowid
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar saída')


def list_all(cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM saidas ORDER BY data_saida DESC')
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar saídas')

    return [Saida(*row) for row in rows]


def get(_id, cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM saidas WHERE id = ?', (_id,))
        row = cursor.fetchone()
    except sqlite3.Error:
        raise Exception('Erro ao recuperar saída')

    return Saida(*row) if row else None


def update(_id, saida: Saida, cursor: sqlite3.Cursor):
    try:
        recalculate_exits_balance(saida.data_saida, saida, cursor, True)

        cursor.execute(
            'UPDATE saidas SET produto_id = ?, destino = ?, data_saida = ?, quantidade = ? WHERE id = ?',
            saida.get_tuple() + (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar saída')


def delete(_id, cursor: sqlite3.Cursor):
    try:
        cursor.execute('DELETE FROM saidas WHERE id = ?', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao deletar saída')


def list_by_date(date: str, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            'SELECT * FROM saidas WHERE data_saida = ?',
            (date,)
        )
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar saídas por data')

    return [Saida(*row) for row in rows]


def list_by_month(month: str, year: str, cursor: sqlite3.Cursor):
    if len(month) == 1:
        month = '0' + month

    try:
        cursor.execute(
            "SELECT * FROM saidas WHERE strftime('%Y', data_saida) = ? AND strftime('%m', data_saida) = ?",
            (year, month)
        )
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar saídas por mês')

    return [Saida(*row) for row in rows]
