from database.scripts.db import connect_db
import sqlite3


class SaldoDiario:
    def __init__(self, _id=None, produto_id=None, data=None, quantidade_inicial=None, quantidade_entrada=None, quantidade_saida=None, quantidade_final=None):
        self.id = _id
        self.produto_id = produto_id
        self.data = data
        self.quantidade_inicial = quantidade_inicial
        self.quantidade_entrada = quantidade_entrada
        self.quantidade_saida = quantidade_saida
        self.quantidade_final = quantidade_final

    def get_tuple(self):
        return (self.produto_id, self.data, self.quantidade_inicial, self.quantidade_entrada, self.quantidade_saida, self.quantidade_final)

    def __str__(self):
        return f"Saldo Diário do Produto {self.produto_id} em {self.data}"

    def calc_final_qntd(self):
        self.quantidade_final = self.quantidade_inicial + self.quantidade_entrada - self.quantidade_saida


def create(saldo: SaldoDiario, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            '''INSERT INTO saldo_diario (
                produto_id, data, quantidade_inicial, 
                quantidade_entrada, quantidade_saida, 
                quantidade_final
            ) VALUES (?, ?, ?, ?, ?, ?)''',
            saldo.get_tuple()
        )
    except sqlite3.Error as e:
        print(e)
        return False

    return True


def list_all(cursor: sqlite3.Cursor):
    cursor.execute('SELECT * FROM saldo_diario ORDER BY data DESC')
    rows = cursor.fetchall()
    saldos = []
    for row in rows:
        saldos.append(SaldoDiario(*row))

    return saldos


def get(_id, cursor: sqlite3.Cursor):
    cursor.execute('SELECT * FROM saldo_diario WHERE id = ?', (_id,))
    row = cursor.fetchone()

    return SaldoDiario(*row) if row else None


def update(_id, saldo: SaldoDiario, cursor: sqlite3.Cursor):
    try:
        cursor.execute(
            '''UPDATE saldo_diario SET 
                produto_id = ?, data = ?, quantidade_inicial = ?, 
                quantidade_entrada = ?, quantidade_saida = ?, 
                quantidade_final = ?
               WHERE id = ?''',
            saldo.get_tuple() + (_id,)
        )
    except sqlite3.Error:
        return False

    return True


def delete(_id, cursor: sqlite3.Cursor):
    try:
        cursor.execute('DELETE FROM saldo_diario WHERE id = ?', (_id,))
    except sqlite3.Error:
        return False

    return True


def list_by_date(date: str, cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM saldo_diario WHERE data = ?', (date,))
        rows = cursor.fetchall()
    except sqlite3.Error:
        return []

    return [SaldoDiario(*row) for row in rows]


def list_by_month(month: str, year: str, cursor: sqlite3.Cursor):
    if len(month) == 1:
        month = '0' + month

    try:
        cursor.execute(
            '''SELECT * FROM saldo_diario 
               WHERE strftime('%Y', data) = ? 
               AND strftime('%m', data) = ?''',
            (year, month)
        )
        rows = cursor.fetchall()
    except sqlite3.Error:
        return []

    return [SaldoDiario(*row) for row in rows]


def get_by_date_and_product(date: str, produto_id: int, cursor: sqlite3.Cursor):
    try:
        cursor.execute('SELECT * FROM saldo_diario WHERE data = ? AND produto_id = ?', (date, produto_id))
        row = cursor.fetchone()
    except sqlite3.Error:
        return None

    return SaldoDiario(*row) if row else None
