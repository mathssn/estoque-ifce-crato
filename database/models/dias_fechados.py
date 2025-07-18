import sqlite3
import mysql.connector as mysql
from dataclasses import dataclass


@dataclass
class DiasFechados:
    data: str
    fechado: bool

    def get_tuple(self):
        return (self.data, self.fechado)

    def __str__(self):
        return f"Dia {self.data} {'fechado' if self.fechado else 'aberto'}"


def create(dia: DiasFechados, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            '''INSERT INTO dias_fechados (
                data, fechado
            ) VALUES (%s, %s)''',
            dia.get_tuple()
        )
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar dia')


def list_all(cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM dias_fechados ORDER BY data ASC')
    except sqlite3.Error:
        raise Exception('Erro ao listar dias')
    
    rows = cursor.fetchall()
    dias = [DiasFechados(data=row[0], fechado=bool(row[1])) for row in rows]

    return dias


def get(data, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM dias_fechados WHERE data = %s', (data,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar dia')
    
    row = cursor.fetchone()

    if row:
        return DiasFechados(data=row[0], fechado=bool(row[1]))
    return None


def update(data, dia: DiasFechados, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute(
            '''UPDATE dias_fechados SET 
                fechado = %s
               WHERE data = %s''',
            (dia.fechado, data)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar dia')


def delete(data, cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('DELETE FROM dias_fechados WHERE data = %s', (data,))
    except sqlite3.Error:
        raise Exception('Erro ao deletar dia')

def get_open_day(cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM dias_fechados WHERE fechado = %s', (0,))
    except:
        raise Exception('Erro ao recuperar dia aberto')
    
    row = cursor.fetchone()
    return DiasFechados(*row) if row else None


def get_open_days(cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM dias_fechados WHERE fechado = %s ORDER BY data ASC', (0,))
    except:
        raise Exception('Erro ao recuperar dias abertos')
    
    rows = cursor.fetchall()
    return [DiasFechados(*row) for row in rows]


def get_last_day(cursor: mysql.connection.MySQLCursor):
    try:
        cursor.execute('SELECT * FROM dias_fechados ORDER BY data DESC LIMIT 1')
    except:
        raise Exception('Não foi possivel recuperar o último dia')
    
    row = cursor.fetchone()
    return DiasFechados(*row) if row else None
