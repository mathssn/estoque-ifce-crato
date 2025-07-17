from flask import Flask, render_template, request, redirect, flash, url_for, session
from datetime import date

from database.scripts.db import *
from database.scripts.utils import *
import database.models.produto as prod
import database.models.saidas as saida
import database.models.entradas as entrada
import database.models.saldo_diario as saldos
import database.models.dias_fechados as dias
import database.models.usuario as user

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
@login_required
def index():
    with connect_db() as (conn, cursor):
        dia = dias.get_open_day(cursor)

    return render_template('index.html', dia=dia)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method != 'POST':
        return redirect('/')
    
    email = request.form.get('email')
    senha = request.form.get('password')
    
    with connect_db() as (conn, cursor):
        cod, user = check_login(email, senha, cursor)
        if cod == 1:
            flash('Usuário inexistente!')
        elif cod == 2:
            flash('Senha incorreta!')
        elif cod == 0:
            session['user_id'] = user.id
            session['nome'] = user.nome
            session['tipo'] = user.tipo
            flash('Usuário logado com sucesso!')

    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()

    return redirect('/')

@app.route('/movimentacoes/diarias/')
@app.route('/movimentacoes/diarias/<data>')
@login_required
def movimentacoes_diarias(data=None):
    d = request.args.get('date')
    if d != None:
        data = d
    elif data == None:
        data = date.today().isoformat()

    with connect_db() as (conn, cursor):
        saidas_diarias = {'Café da manhã': [], 'Lanche da manhã': [], 'Almoço': [], 'Lanche da tarde': [], 'Jantar': [], 'Ceia': [], 'Outros': []}
        entradas_diarias = entrada.list_by_date(data, cursor)

        for saida_ in saida.list_by_date(data, cursor):
            saidas_diarias[saida_.destino].append(saida_)
            
        produtos_dict = {p.id: p for p in prod.list_all(cursor)}
        saldos_diarios = saldos.list_by_date(data, cursor)

        dia = dias.get(data, cursor)

        usuarios = {}
        for entrie in entradas_diarias:
            if entrie.usuario_id not in usuarios.keys():
                usuario = user.get(entrie.usuario_id, cursor)
                if usuario:
                    usuarios[usuario.id] = usuario.nome
                else:
                    usuarios[entrie.usuario_id] = 'Desconhecido'
        
        for destino, exits in saidas_diarias.items():
            for exit in exits:
                if exit.usuario_id not in usuarios.keys():
                    usuario = user.get(exit.usuario_id, cursor)
                    if usuario:
                        usuarios[usuario.id] = usuario.nome
                    else:
                        usuarios[entrie.usuario_id] = 'Desconhecido'

    return render_template('movimentacoes_diarias.html', saidas=saidas_diarias, data=data, produtos=produtos_dict, entradas=entradas_diarias, saldos_diarios=saldos_diarios, dia=dia, usuarios=usuarios)

@app.route('/fechar/dia/<data>')
@login_required
def fechar_dia(data: str):
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('movimentacoes_diarias'))

    cod = verificar_dias_abertos()
    if cod == 1:
        flash('Não há dia aberto')
        return
    
    try:
        with connect_db() as (conn, cursor):
            saldos_ = saldos.list_by_date(data, cursor)

            if not check_saldo(data, cursor):
                return redirect(url_for('movimentacoes_diarias', data=data))
    
            dia = dias.get(data, cursor)
            dia.fechado = True
            dias.update(data, dia, cursor)

            # Soma 1 dia a data
            new_date = somar_dia(data, '%Y-%m-%d')

            dia = dias.DiasFechados(new_date, False)
            dias.create(dia, cursor)

            for saldo in saldos_:
                new_saldo = saldos.SaldoDiario(0, saldo.produto_id, new_date, saldo.quantidade_final, 0, 0, saldo.quantidade_final)
                saldos.create(new_saldo, cursor)
    except:
        flash(f'Falha ao fechar dia: {data}')
    else:
        flash(f'Dia {data} fechado com sucesso')
        
    return redirect(url_for('movimentacoes_diarias', data=data))


def verificar_dias_abertos() -> int:
    try:
        with connect_db() as (conn, cursor):
            dias_ = dias.get_open_days(cursor)

            if len(dias_) == 0:
                mais_recente = dias.get_last_day(cursor)
                if mais_recente == None:
                        return 1
            
            elif len(dias_) > 1:
                for dia in dias_[:-1]:
                    dia.fechado = True
                    dias.update(dia.data, dia, cursor)
                return 2
    except Exception as e:
        flash(f'Não foi possivel verificar os dias: {e}')
        return 3
    
    return 0
