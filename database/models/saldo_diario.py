import sqlite3
import mysql.connector as mysql
from dataclasses import dataclass


@dataclass
class SaldoDiario:
    id: int
    produto_id: int
    data: str
    quantidade_inicial: int
    quantidade_entrada: int
    quantidade_saida: int
    quantidade_final: int

    def get_tuple(self):
        return (self.produto_id, self.data, self.quantidade_inicial, self.quantidade_entrada, self.quantidade_saida, self.quantidade_final)

    def __str__(self):
        return f"Saldo Diário do Produto {self.produto_id} em {self.data}"

    def calc_final_qntd(self):
        self.quantidade_final = (
            self.quantidade_inicial + self.quantidade_entrada - self.quantidade_saida
        )


def create(saldo: SaldoDiario, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            '''INSERT INTO saldo_diario (
                produto_id, data, quantidade_inicial,
                quantidade_entrada, quantidade_saida,
                quantidade_final
            ) VALUES (%s, %s, %s, %s, %s, %s)''',
            saldo.get_tuple()
        )
        saldo.id = cursor.lastrowid
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar saldo diário')


def list_all(cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM saldo_diario ORDER BY data DESC')
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar saldos diários')

    return [SaldoDiario(*row) for row in rows]


def get(_id, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM saldo_diario WHERE id = %s', (_id,))
        row = cursor.fetchone()
    except sqlite3.Error:
        raise Exception('Erro ao recuperar saldo diário')

    return SaldoDiario(*row) if row else None


def update(_id, saldo: SaldoDiario, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            '''UPDATE saldo_diario SET 
                produto_id = %s, data = %s, quantidade_inicial = %s, 
                quantidade_entrada = %s, quantidade_saida = %s, 
                quantidade_final = %s
               WHERE id = %s''',
            saldo.get_tuple() + (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar saldo diário')


def delete(_id, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('DELETE FROM saldo_diario WHERE id = %s', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao deletar saldo diário')


def list_by_date(date: str, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM saldo_diario WHERE data = %s', (date,))
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar saldo diário por data')

    return [SaldoDiario(*row) for row in rows]


def list_by_month(month: str, year: str, cursor: mysql.connection.MySQLCursor):
    if len(month) == 1:
        month = '0' + month

    try:
        cursor.execute(
            '''SELECT * FROM saldo_diario 
               WHERE strftime('%Y', data) = %s 
               AND strftime('%m', data) = %s''',
            (year, month)
        )
        rows = cursor.fetchall()
    except sqlite3.Error:
        raise Exception('Erro ao listar saldo diário por mês')

    return [SaldoDiario(*row) for row in rows]


def get_by_date_and_product(date: str, produto_id: int, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            'SELECT * FROM saldo_diario WHERE data = %s AND produto_id = %s',
            (date, produto_id)
        )
        row = cursor.fetchone()
    except sqlite3.Error:
        raise Exception('Erro ao buscar saldo diário por data e produto')

    return SaldoDiario(*row) if row else None
