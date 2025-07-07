from flask import Flask, render_template, request, redirect, flash, url_for
import datetime

from database.scripts.db import *
import database.models.produto as prod
import database.models.saidas as saidas

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
    status = request.form.get('status')

    novo_produto = prod.Produto(0, codigo, nome, descricao, unidade, quantidade_minima, status)
    if not prod.create(novo_produto):
        flash('Erro ao cadastrar produto')
    
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
@app.route('/movimentacoes/diarias/<date>')
def movimentacoes_diarias(date=None):
    d = request.args.get('date')
    if d != None:
        date = d
    elif date == None:
        date = datetime.date.today().isoformat()

    saidas_diarias = {'Café da manhã': [], 'Lanche da manhã': [], 'Almoço': [], 'Lanche da tarde': [], 'Jantar': [], 'Ceia': [], 'Outros': []}

    for saida in saidas.list_by_date(date):
        saidas_diarias[saida.destino].append(saida)
        
    produtos_dict = {p.id: p for p in prod.list_all()}
            
    return render_template('movimentacoes_diarias.html', saidas=saidas_diarias, data=date, produtos=produtos_dict)


@app.route('/cadastro/saida/', methods=['POST'])
def cadastro_saida():
    produto_id = request.form.get('produto_id')
    destino = request.form.get('destino')
    data = request.form.get('data')
    quantidade = request.form.get('quantidade')

    nova_saida = saidas.Saida(0, produto_id, destino, data, quantidade)
    if not saidas.create(nova_saida):
        flash('Erro ao cadastrar saida')
    
    return redirect(url_for('movimentacoes_diarias', date=data))


@app.route('/editar/saida/<int:saida_id>/', methods=['POST'])
def editar_saida(saida_id):
    saida = saidas.get(saida_id)
    saida.produto_id = request.form.get('edit_produto_id')
    saida.destino = request.form.get('edit_destino')
    saida.data_saida = request.form.get('edit_data')
    saida.quantidade = request.form.get('edit_quantidade')

    if not saidas.update(saida.id, saida):
        flash('Erro ao atualizar saida')
    
    return redirect(url_for('movimentacoes_diarias', date=saida.data_saida))


@app.route('/excluir/saida/<int:saida_id>/', methods=['POST'])
def excluir_saida(saida_id):
    saida = saidas.get(saida_id)
    if not saidas.delete(saida_id):
        flash('Erro ao deletar saida')

    return redirect(url_for('movimentacoes_diarias', date=saida.data_saida))
