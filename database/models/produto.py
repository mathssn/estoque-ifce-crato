import sqlite3
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

def create(produto: Produto, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            'INSERT INTO produto (codigo, nome, descricao, unidade, quantidade_minima, status) VALUES (?, ?, ?, ?, ?, ?)',
            produto.get_tuple()
        )
        produto.id = cursor.lastrowid
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar produto')


def list_all(cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM produto ORDER BY codigo')
    except sqlite3.Error:
        raise Exception('Erro ao listar produtos')
    
    rows = cursor.fetchall()
    produtos: list[Produto] = []

    for row in rows:
        produtos.append(Produto(*row))

    return produtos


def get(_id, cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM produto WHERE id = ?', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar produto')
    row = cursor.fetchone()

    return Produto(*row) if row else None


def get_by_cod(cod, cursor: sqlite3.Cursor):
    
    try:
        cursor.execute('SELECT * FROM produto WHERE codigo = ?', (cod,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar produto')
    row = cursor.fetchone()

    return Produto(*row) if row else None


def update(_id, produto: Produto, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            'UPDATE produto SET codigo = ?, nome = ?, descricao = ?, unidade = ?, quantidade_minima = ?, status = ? WHERE id = ?',
            produto.get_tuple() + (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar produto')


def delete(_id, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            'DELETE FROM produto WHERE id = ?',
            (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao deletar produto')
