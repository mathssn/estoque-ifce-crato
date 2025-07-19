import sqlite3
import mysql.connector as mysql
from dataclasses import dataclass

@dataclass
class Usuario:
    id: int
    nome: str
    tipo: str
    email: str
    senha: str
    data_nascimento: str

    def get_tuple(self):
        return (self.nome, self.tipo, self.email, self.senha, self.data_nascimento)

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

def create(usuario: Usuario, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            '''
            INSERT INTO usuario (nome, tipo, email, senha, data_nascimento)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            usuario.get_tuple()
        )
        usuario.id = cursor.lastrowid
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar usuário')

def list_all(cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM usuario ORDER BY nome')
    except sqlite3.Error:
        raise Exception('Erro ao listar usuários')
    
    rows = cursor.fetchall()
    usuarios: list[Usuario] = []

    for row in rows:
        usuarios.append(Usuario(*row))

    return usuarios

def get(_id: int, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM usuario WHERE id = %s', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar usuário')
    
    row = cursor.fetchone()
    return Usuario(*row) if row else None

def get_by_email(email: str, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar usuário por e-mail')
    
    row = cursor.fetchone()
    return Usuario(*row) if row else None

def update(_id: int, usuario: Usuario, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            '''
            UPDATE usuario SET nome = %s, tipo = %s, email = %s, senha = %s, data_nascimento = %s
            WHERE id = %s
            ''',
            usuario.get_tuple() + (_id,)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar usuário')

def delete(_id: int, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('DELETE FROM usuario WHERE id = %s', (_id,))
    except sqlite3.Error:
        raise Exception('Erro ao deletar usuário')
