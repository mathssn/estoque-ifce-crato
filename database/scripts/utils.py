import mysql.connector as mysql
from flask import session, flash, redirect
from functools import wraps
from datetime import datetime, timedelta


def recalculate_exits_balance(data, saida, cursor: mysql.connection.MySQLCursor, update=False, delete=False):
    import database.models.saldo_diario as saldos
    import database.models.saidas as saidas

    saldo = saldos.get_by_date_and_product(data, saida.produto_id, cursor)
    if not saldo:
        raise Exception('Não é possivel atualizar o saldo do dia')

    saidas_ = saidas.list_by_date(data, cursor)
    total_saidas = 0

    for s in saidas_:
        if s.produto_id == int(saida.produto_id):
            if s.id == saida.id:
                if update and not delete:
                    total_saidas += int(saida.quantidade)
            else:
                total_saidas += s.quantidade
    
    if not update and not delete:
        total_saidas += int(saida.quantidade)
    
    qntd_final = saldo.quantidade_inicial + saldo.quantidade_entrada - total_saidas
    if qntd_final < 0:
        raise Exception('Valor inválido')

    saldo.quantidade_saida = total_saidas
    saldo.quantidade_final = qntd_final
    saldos.update(saldo.id, saldo, cursor)


def recalculate_entries_balance(data, entrada, cursor: mysql.connection.MySQLCursor, update=False, delete=False):
    import database.models.saldo_diario as saldos
    import database.models.entradas as entradas

    saldo = saldos.get_by_date_and_product(data, entrada.produto_id, cursor)
    if not saldo:
        raise Exception('Não é possivel atualizar o saldo do dia')

    entradas_ = entradas.list_by_date(data, cursor)
    total_entradas = 0

    for e in entradas_:
        if e.produto_id == int(entrada.produto_id):
            if e.id == entrada.id:
                if update and not delete:
                    total_entradas += int(entrada.quantidade)
            else:
                total_entradas += e.quantidade
    
    if not update and not delete:
        total_entradas += int(entrada.quantidade)
    
    qntd_final = saldo.quantidade_inicial + total_entradas - saldo.quantidade_saida
    if qntd_final < 0:
        raise Exception('Valor inválido')

    saldo.quantidade_entrada = total_entradas
    saldo.quantidade_final = qntd_final
    saldos.update(saldo.id, saldo, cursor)


def check_saldo(data, cursor: mysql.connection.MySQLCursor):
    import database.models.dias_fechados as dias

    dia = dias.get(data, cursor)
    if not dia:
        return False
    if dia.fechado:
        return False
    
    return True


def check_login(email: str, senha: str, cursor: mysql.connection.MySQLCursor):
    import database.models.usuario as user

    usuario = user.get_by_email(email, cursor)
    if usuario == None:
        return 1, None
    elif usuario.senha != senha:
        return 2, None
    return 0, usuario


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nome' not in session or 'user_id' not in session:
            flash('Você precisa estar logado para acessar essa página')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def somar_dia(data: str, formato: str, quantidade: int = 1) -> str:
    new_date = datetime.strptime(data, formato).date() + timedelta(days=quantidade)
    new_date = new_date.isoformat() # retorna a string da data
    return new_date