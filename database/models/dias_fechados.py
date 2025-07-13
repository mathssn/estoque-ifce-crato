import sqlite3
from dataclasses import dataclass


@dataclass
class DiasFechados:
    data: str
    fechado: bool

    def get_tuple(self):
        return (self.data, self.fechado)

    def __str__(self):
        return f"Dia {self.data} {'fechado' if self.fechado else 'aberto'}"


def create(dia: DiasFechados, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            '''INSERT INTO dias_fechados (
                data, fechado
            ) VALUES (?, ?)''',
            dia.get_tuple()
        )
    except sqlite3.Error:
        raise Exception('Erro ao cadastrar dia')


def list_all(cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM dias_fechados ORDER BY data DESC')
    except sqlite3.Error:
        raise Exception('Erro ao listar dias')
    
    rows = cursor.fetchall()
    dias = [DiasFechados(data=row[0], fechado=bool(row[1])) for row in rows]

    return dias


def get(data, cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM dias_fechados WHERE data = ?', (data,))
    except sqlite3.Error:
        raise Exception('Erro ao recuperar dia')
    
    row = cursor.fetchone()

    if row:
        return DiasFechados(data=row[0], fechado=bool(row[1]))
    return None


def update(data, dia: DiasFechados, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            '''UPDATE dias_fechados SET 
                fechado = ?
               WHERE data = ?''',
            (dia.fechado, data)
        )
    except sqlite3.Error:
        raise Exception('Erro ao atualizar dia')


def delete(data, cursor: sqlite3.Cursor):
    try:
        cursor.execute('DELETE FROM dias_fechados WHERE data = ?', (data,))
    except sqlite3.Error:
        raise Exception('Erro ao deletar dia')

