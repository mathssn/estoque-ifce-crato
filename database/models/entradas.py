import sqlite3
import mysql.connector as mysql
from dataclasses import dataclass
from database.scripts.utils import recalculate_entries_balance


@dataclass
class Entrada:
    id: int
    produto_id: int
    data_entrada: str
    quantidade: int
    observacao: str
    usuario_id: int

    def get_tuple(self):
        return (self.produto_id, self.data_entrada, self.quantidade, self.observacao, self.usuario_id)

    def __str__(self):
        return f"Entrada de Produto {self.produto_id} em {self.data_entrada} pelo usuário: {self.usuario_id}"


def create(entrada: Entrada, cursor: mysql.connection.MySQLCursor):
    try:
        recalculate_entries_balance(entrada.data_entrada, entrada, cursor)
        
        cursor.execute(
            'INSERT INTO entradas (produto_id, data_entrada, quantidade, observacao, usuario_id) VALUES (%s, %s, %s, %s, %s)',
            entrada.get_tuple()
        )
        entrada.id = cursor.lastrowid
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar entrada')


def list_all(cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM entradas ORDER BY data_entrada DESC')
    except sqlite3.Error:
        raise Exception('Erro ao listar entradas')

    rows = cursor.fetchall()
    entradas: list[Entrada] = [Entrada(*row) for row in rows]
    return entradas


def get(_id, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM entradas WHERE id = %s', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar entrada')

    row = cursor.fetchone()
    return Entrada(*row) if row else None


def update(_id, entrada: Entrada, cursor: mysql.connection.MySQLCursor):
    try:
        recalculate_entries_balance(entrada.data_entrada, entrada, cursor, True)
        
        cursor.execute(
            'UPDATE entradas SET produto_id = %s, data_entrada = %s, quantidade = %s, observacao = %s, usuario_id = %s WHERE id = %s',
            entrada.get_tuple() + (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar entrada')


def delete(_id, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('DELETE FROM entradas WHERE id = %s', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao deletar entrada')


def list_by_date(date: str, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM entradas WHERE data_entrada = %s', (date,))
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar entradas por data')

    return [Entrada(*row) for row in rows]


def list_by_month(month: str, year: str, cursor: mysql.connection.MySQLCursor):

    try:
        query = """
            SELECT * FROM entradas
            WHERE YEAR(data_entrada) = %s AND MONTH(data_entrada) = %s
        """
        cursor.execute(query, (year, month))
        rows = cursor.fetchall()
    except mysql.connection.Error as e:
        raise Exception(f'Erro ao listar entradas por mês')

    return [Entrada(*row) for row in rows]