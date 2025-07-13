import sqlite3
from dataclasses import dataclass
from database.scripts.utils import recalculate_entries_balance


@dataclass
class Entrada:
    id: int
    produto_id: int
    data_entrada: str
    quantidade: int

    def get_tuple(self):
        return (self.produto_id, self.data_entrada, self.quantidade)

    def __str__(self):
        return f"Entrada de Produto {self.produto_id} em {self.data_entrada}"


def create(entrada: Entrada, cursor: sqlite3.Cursor):
    try:
        recalculate_entries_balance(entrada.data_entrada, entrada, cursor)
        
        cursor.execute(
            'INSERT INTO entradas (produto_id, data_entrada, quantidade) VALUES (?, ?, ?)',
            entrada.get_tuple()
        )
        entrada.id = cursor.lastrowid
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar entrada')


def list_all(cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM entradas ORDER BY data_entrada DESC')
    except sqlite3.Error:
        raise Exception('Erro ao listar entradas')

    rows = cursor.fetchall()
    entradas: list[Entrada] = [Entrada(*row) for row in rows]
    return entradas


def get(_id, cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM entradas WHERE id = ?', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar entrada')

    row = cursor.fetchone()
    return Entrada(*row) if row else None


def update(_id, entrada: Entrada, cursor: sqlite3.Cursor):
    try:
        recalculate_entries_balance(entrada.data_entrada, entrada, cursor, True)
        
        cursor.execute(
            'UPDATE entradas SET produto_id = ?, data_entrada = ?, quantidade = ? WHERE id = ?',
            entrada.get_tuple() + (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar entrada')


def delete(_id, cursor: sqlite3.Cursor):
    try:
        cursor.execute('DELETE FROM entradas WHERE id = ?', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao deletar entrada')


def list_by_date(date: str, cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM entradas WHERE data_entrada = ?', (date,))
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar entradas por data')

    return [Entrada(*row) for row in rows]


def list_by_month(month: str, year: str, cursor: sqlite3.Cursor):
    if len(month) == 1:
        month = '0' + month

    try:
        cursor.execute(
            "SELECT * FROM entradas WHERE strftime('%Y', data_entrada) = ? AND strftime('%m', data_entrada) = ?",
            (year, month)
        )
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar entradas por mês')

    return [Entrada(*row) for row in rows]
