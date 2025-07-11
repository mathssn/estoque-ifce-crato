from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime, timedelta, date

from database.scripts.db import *
from database.scripts.utils import *
import database.models.produto as prod
import database.models.saidas as saida
import database.models.entradas as entrada
import database.models.saldo_diario as saldos
import database.models.dias_fechados as dias

from views.routes_produto import produtos
from views.routes_saida import saidas
from views.routes_entradas import entradas

create_database()

app = Flask(__name__)
app.secret_key = 'teste123'
app.register_blueprint(produtos)
app.register_blueprint(saidas)
app.register_blueprint(entradas)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movimentacoes/diarias/')
@app.route('/movimentacoes/diarias/<data>')
def movimentacoes_diarias(data=None):
    d = request.args.get('date')
    if d != None:
        data = d
    elif data == None:
        data = date.today().isoformat()

    conn, cursor = connect_db()
    saidas_diarias = {'Café da manhã': [], 'Lanche da manhã': [], 'Almoço': [], 'Lanche da tarde': [], 'Jantar': [], 'Ceia': [], 'Outros': []}
    entradas_diarias = entrada.list_by_date(data, cursor)

    for saida_ in saida.list_by_date(data, cursor):
        saidas_diarias[saida_.destino].append(saida_)
        
    produtos_dict = {p.id: p for p in prod.list_all(cursor)}
    saldos_diarios = saldos.list_by_date(data, cursor)

    conn.close()
    return render_template('movimentacoes_diarias.html', saidas=saidas_diarias, data=data, produtos=produtos_dict, entradas=entradas_diarias, saldos_diarios=saldos_diarios)

@app.route('/fechar/dia/<data>')
def fechar_dia(data: str):
    conn, cursor = connect_db()
    saldos_ = saldos.list_by_date(data, cursor)

    if not check_saldo(data, cursor):
        conn.close()
        flash('Não foi possivel fechar o dia')
        return redirect(url_for('movimentacoes_diarias', data=data))
    
    dia = dias.get(data, cursor)
    dia.fechado = True
    if not dias.update(data, dia, cursor):
        conn.rollback()
        conn.close()
        flash('Não foi possivel fechar o dia')
        return redirect(url_for('movimentacoes_diarias', data=data))

    data = data.replace('-', '/')
    # Soma 1 dia a data
    new_date = datetime.strptime(data, '%Y/%m/%d').date() + timedelta(days=1)
    new_date = new_date.isoformat() # retorna a string da data
    data = data.replace('/', '-')

    dia = dias.DiasFechados(new_date, False)
    if not dias.create(dia, cursor):
        conn.rollback()
        conn.close()
        flash('Não foi possivel fechar o dia')
        return redirect(url_for('movimentacoes_diarias', data=data))

    for saldo in saldos_:
        new_saldo = saldos.SaldoDiario(0, saldo.produto_id, new_date, saldo.quantidade_final, 0, 0, saldo.quantidade_final)
        if not saldos.create(new_saldo, cursor):
            conn.rollback()
            conn.close()
            flash('Não foi possivel fechar o dia')
            return redirect(url_for('movimentacoes_diarias', data=data))

    conn.commit()
    conn.close()
    return redirect(url_for('movimentacoes_diarias', data=data))
