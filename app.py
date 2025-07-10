from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime, timedelta, date

from database.scripts.db import *
from database.scripts.utils import *
import database.models.produto as prod
import database.models.saidas as saidas
import database.models.entradas as entradas
import database.models.saldo_diario as saldos
import database.models.dias_fechados as dias

create_database()

app = Flask(__name__)
app.secret_key = 'teste123'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/produtos/')
def produtos():
    produtos_lista = prod.list_all()

    return render_template('produtos.html', produtos=produtos_lista)

@app.route('/cadastro/produtos/', methods=['POST'])
def cadastro_produtos():
    codigo = request.form.get('codigo')
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    unidade = request.form.get('unidade')
    quantidade_minima = request.form.get('quantidade_minima')
    quantidade_atual = request.form.get('quantidade_atual')
    status = request.form.get('status')

    novo_produto = prod.Produto(0, codigo, nome, descricao, unidade, quantidade_minima, status)
    if not prod.create(novo_produto):
        flash('Erro ao cadastrar produto')
    
    # Cria a entrada inicial do produto
    data_atual = date.today().isoformat()
    entrada = entradas.Entrada(0, novo_produto.id, data_atual, quantidade_atual)
    if not entradas.create(entrada):
        flash('Erro ao cadastrar a quantidade atual')

    saldo_diario = saldos.SaldoDiario(0, novo_produto.id, data_atual, 0, entrada.quantidade, 0, entrada.quantidade)
    if not saldos.create(saldo_diario):
        flash('Erro ao cadastrar a quantidade atual')

    dia = dias.get(data_atual)
    if not dia:
        dia = dias.DiasFechados(data_atual, False)
        dias.create(dia)
    
    return redirect('/produtos')

@app.route('/editar/produto/<int:produto_id>/', methods=['POST'])
def editar_produto(produto_id):
    produto = prod.get(produto_id)
    produto.codigo = request.form.get('edit_codigo')
    produto.nome = request.form.get('edit_nome')
    produto.descricao = request.form.get('edit_descricao')
    produto.unidade = request.form.get('edit_unidade')
    produto.quantidade_minima = request.form.get('edit_quantidade_minima')

    if not prod.update(produto.id, produto):
        flash('Erro ao atualizar produto')
    
    return redirect('/produtos')


@app.route('/excluir/produto/<int:produto_id>/', methods=['POST'])
def excluir_produto(produto_id):
    if not prod.delete(produto_id):
        flash('Erro ao deletar produto')

    return redirect('/produtos')


@app.route('/movimentacoes/diarias/')
@app.route('/movimentacoes/diarias/<data>')
def movimentacoes_diarias(data=None):
    d = request.args.get('date')
    if d != None:
        data = d
    elif data == None:
        data = date.today().isoformat()

    saidas_diarias = {'Café da manhã': [], 'Lanche da manhã': [], 'Almoço': [], 'Lanche da tarde': [], 'Jantar': [], 'Ceia': [], 'Outros': []}
    entradas_diarias = entradas.list_by_date(data)

    for saida in saidas.list_by_date(data):
        saidas_diarias[saida.destino].append(saida)
        
    produtos_dict = {p.id: p for p in prod.list_all()}

    saldos_diarios = saldos.list_by_date(data)
            
    return render_template('movimentacoes_diarias.html', saidas=saidas_diarias, data=data, produtos=produtos_dict, entradas=entradas_diarias, saldos_diarios=saldos_diarios)


@app.route('/cadastro/saida/', methods=['POST'])
def cadastro_saida():
    produto_id = request.form.get('produto_id')
    destino = request.form.get('destino')
    data = request.form.get('data_saida')
    quantidade = request.form.get('quantidade')

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(data):
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=data))

    nova_saida = saidas.Saida(0, produto_id, destino, data, quantidade)
    if not saidas.create(nova_saida):
        flash('Erro ao cadastrar saida')
        
    return redirect(url_for('movimentacoes_diarias', data=data))


@app.route('/editar/saida/<int:saida_id>/', methods=['POST'])
def editar_saida(saida_id):
    saida = saidas.get(saida_id)
    saida.produto_id = request.form.get('edit_produto_id_saida')
    saida.destino = request.form.get('edit_destino_saida')
    saida.data_saida = request.form.get('edit_data_saida')
    saida.quantidade = request.form.get('edit_quantidade_saida')

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(saida.data_saida):
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=saida.data_saida))

    if not saidas.update(saida.id, saida):
        flash('Erro ao atualizar saida')
    
    return redirect(url_for('movimentacoes_diarias', data=saida.data_saida))


@app.route('/excluir/saida/<int:saida_id>/', methods=['POST'])
def excluir_saida(saida_id):
    saida = saidas.get(saida_id)

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(saida.data_saida):
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=saida.data_saida))

    if not saidas.delete(saida_id):
        flash('Erro ao deletar saida')
    
    recalculate_diary_balance(saida.data_saida, int(saida.produto_id))
    
    return redirect(url_for('movimentacoes_diarias', data=saida.data_saida))


@app.route('/cadastro/entrada/', methods=['POST'])
def cadastro_entrada():
    produto_id = request.form.get('produto_id')
    data = request.form.get('data_entrada')
    quantidade = request.form.get('quantidade')

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(data):
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=data))

    nova_entrada = entradas.Entrada(0, produto_id, data, quantidade)
    if not entradas.create(nova_entrada):
        flash('Erro ao cadastrar entradas')
    
    return redirect(url_for('movimentacoes_diarias', data=data))


@app.route('/editar/entrada/<int:entrada_id>/', methods=['POST'])
def editar_entrada(entrada_id):
    entrada = entradas.get(entrada_id)
    entrada.produto_id = request.form.get('edit_produto_id_entrada')
    entrada.data_entrada = request.form.get('edit_data_entrada')
    entrada.quantidade = request.form.get('edit_quantidade_entrada')

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(entrada.data_entrada):
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=entrada.data_entrada))


    if not entradas.update(entrada_id, entrada):
        flash('Erro ao atualizar entrada')
    
    return redirect(url_for('movimentacoes_diarias', data=entrada.data_entrada))


@app.route('/excluir/entrada/<int:entrada_id>/', methods=['POST'])
def excluir_entrada(entrada_id):
    entrada = entradas.get(entrada_id)

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(entrada.data_entrada):
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=entrada.data_entrada))

    if not entradas.delete(entrada_id):
        flash('Erro ao deletar entradas')
    
    recalculate_diary_balance(entrada.data_entrada, int(entrada.produto_id))

    return redirect(url_for('movimentacoes_diarias', data=entrada.data_entrada))


@app.route('/fechar/dia/<data>')
def fechar_dia(data: str):
    saldos_ = saldos.list_by_date(data)
    if len(saldos_) == 0:
        flash('Não foi possivel fechar o dia')
        return redirect(url_for('movimentacoes_diarias', data=data))
    elif saldos_[0].fechado:
        flash('Não foi possivel fechar o dia')
        return redirect(url_for('movimentacoes_diarias', data=data))

    [saldos.fechar_dia(saldo.id) for saldo in saldos_]
    data = data.replace('-', '/')
    # Soma 1 dia a data
    new_date = datetime.strptime(data, '%Y/%m/%d').date() + timedelta(days=1)
    new_date = new_date.isoformat() # retorna a string da data

    for saldo in saldos_:
        new_saldo = saldos.SaldoDiario(0, saldo.produto_id, new_date, saldo.quantidade_final, 0, 0, saldo.quantidade_final, False)
        saldos.create(new_saldo)

    return redirect(url_for('movimentacoes_diarias', data=data))
