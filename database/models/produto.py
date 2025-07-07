from database.scripts.db import connect_db
import sqlite3


class Produto:

    def __init__(self, _id=None, codigo=None, nome=None, descricao=None, unidade=None, quantidade_minima=None, status=None):
        self.id = _id
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.unidade = unidade
        self.quantidade_minima = quantidade_minima
        self.status = status

    def get_tuple(self):
        return (self.codigo, self.nome, self.descricao, self.unidade, self.quantidade_minima, self.status)

    def __str__(self):
        return self.nome

def create(produto: Produto):
    conn, cursor = connect_db()

    try:
        cursor.execute(
            'INSERT INTO produto (codigo, nome, descricao, unidade, quantidade_minima, status) VALUES (?, ?, ?, ?, ?, ?)',
            produto.get_tuple()
        )
        conn.commit()
    except sqlite3.Error:
        return False
    finally:
        conn.close()

    return True


def list_all():
    conn, cursor = connect_db()

    cursor.execute('SELECT * FROM produto ORDER BY codigo')
    rows = cursor.fetchall()
    produtos: list[Produto] = []

    for row in rows:
        produtos.append(Produto(*row))

    conn.close()    
    return produtos


def get(_id):
    conn, cursor = connect_db()

    cursor.execute('SELECT * FROM produto WHERE id = ?', (_id,))
    row = cursor.fetchone()
    conn.close()    

    if row:
        return Produto(*row)
    
    return None


def update(_id, produto: Produto):
    conn, cursor = connect_db()

    try:
        cursor.execute(
            'UPDATE produto SET codigo = ?, nome = ?, descricao = ?, unidade = ?, quantidade_minima = ?, status = ? WHERE id = ?',
            produto.get_tuple() + (_id,)
        )
        conn.commit()
    except sqlite3.Error:
        return False
    finally:
        conn.close()

    return True

def delete(_id):
    conn, cursor = connect_db()

    try:
        cursor.execute(
            'DELETE FROM produto WHERE id = ?',
            (_id,)
        )
        conn.commit()
    except sqlite3.Error:
        return False
    finally:
        conn.close()

    return True