import sqlite3
import mysql.connector as mysql
from dataclasses import dataclass


@dataclass
class Produto:
    id: int
    codigo: int
    nome: str
    descricao: str
    unidade: str
    quantidade_minima: int
    status: str

    def get_tuple(self):
        return (self.codigo, self.nome, self.descricao, self.unidade, self.quantidade_minima, self.status)

    def __str__(self):
        return self.nome

def create(produto: Produto, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            'INSERT INTO produto (codigo, nome, descricao, unidade, quantidade_minima, status) VALUES (%s, %s, %s, %s, %s, %s)',
            produto.get_tuple()
        )
        produto.id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise Exception('Não é possivel cadastrar produto com código já existente')
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar produto')


def list_all(cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM produto ORDER BY codigo')
    except sqlite3.Error:
        raise Exception('Erro ao listar produtos')
    
    rows = cursor.fetchall()
    produtos: list[Produto] = []

    for row in rows:
        produtos.append(Produto(*row))

    return produtos


def get(_id, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM produto WHERE id = %s', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar produto')
    row = cursor.fetchone()

    return Produto(*row) if row else None


def get_by_cod(cod, cursor: mysql.connection.MySQLCursor):
    
    try:
        cursor.execute('SELECT * FROM produto WHERE codigo = %s', (cod,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar produto')
    row = cursor.fetchone()

    return Produto(*row) if row else None


def update(_id, produto: Produto, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            'UPDATE produto SET codigo = %s, nome = %s, descricao = %s, unidade = %s, quantidade_minima = %s, status = %s WHERE id = %s',
            produto.get_tuple() + (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar produto')


def delete(_id, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            'DELETE FROM produto WHERE id = %s',
            (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao deletar produto')
