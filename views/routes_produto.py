from flask import Blueprint, render_template, redirect, flash, url_for, request, session
from datetime import date

from database.scripts.db import connect_db
import database.models.produto as prod
import database.models.dias_fechados as dias
import database.models.saldo_diario as saldos
import database.models.entradas as entradas
from database.scripts.utils import login_required

produtos = Blueprint('produtos', __name__)

@produtos.route('/produtos/')
@login_required
def produtos_lista():
    with connect_db() as (conn, cursor):
        produtos_list = prod.list_all(cursor)

    return render_template('produtos.html', produtos=produtos_list)

@produtos.route('/cadastro/produtos/', methods=['POST'])
@login_required
def cadastro_produtos():
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('produtos.produtos_lista'))
    
    codigo = request.form.get('codigo')
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    unidade = request.form.get('unidade')
    quantidade_minima = request.form.get('quantidade_minima')
    quantidade_atual = request.form.get('quantidade_atual')
    status = request.form.get('status')

    novo_produto = prod.Produto(0, codigo, nome, descricao, unidade, quantidade_minima, status)
    if not validar_dados(novo_produto, quantidade_atual):
        flash('Insira dados válidos')
        return redirect(url_for('produtos.produtos_lista'))

    try:
        with connect_db() as (conn, cursor):
            prod.create(novo_produto, cursor)

            # Cria a entrada inicial do produto
            data_atual = date.today().isoformat()

            dia = dias.get(data_atual, cursor)
            if not dia:
                dia = dias.DiasFechados(data_atual, False)
                dias.create(dia, cursor)

            saldo_diario = saldos.SaldoDiario(0, novo_produto.id, data_atual, 0, quantidade_atual, 0, quantidade_atual)
            saldos.create(saldo_diario, cursor)
                
            entrada = entradas.Entrada(0, novo_produto.id, data_atual, quantidade_atual, 'Entrada inicial', session['user_id'])
            entradas.create(entrada, cursor)
    except Exception as e:
        flash(f'Falha ao cadastrar produto: {e}')
    else:
        flash('Produto cadastrado com sucesso!')

    return redirect(url_for('produtos.produtos_lista'))

@produtos.route('/editar/produto/<int:produto_id>/', methods=['POST'])
@login_required
def editar_produto(produto_id):
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('produtos.produtos_lista'))
    
    try:
        with connect_db() as (conn, cursor):
            produto = prod.get(produto_id, cursor)
            produto.codigo = request.form.get('edit_codigo')
            produto.nome = request.form.get('edit_nome')
            produto.descricao = request.form.get('edit_descricao')
            produto.unidade = request.form.get('edit_unidade')
            produto.quantidade_minima = request.form.get('edit_quantidade_minima')

            if not validar_dados(produto, 0):
                flash('Insira dados válidos')
                return redirect(url_for('produtos.produtos_lista'))

            prod.update(produto_id, produto, cursor)
    except Exception as e:
        flash(f'Falha ao atualizar produto: {e}')
    else:
        flash('Produto atualizado com sucesso!')

    return redirect(url_for('produtos.produtos_lista'))


@produtos.route('/excluir/produto/<int:produto_id>/', methods=['POST'])
@login_required
def excluir_produto(produto_id):
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('produtos.produtos_lista'))
    
    try:
        with connect_db() as (conn, cursor):
            prod.delete(produto_id, cursor)
    except Exception as e:
        flash(f'Falha ao deletar produto: {e}')
    else:
        flash('Produto deletado com sucesso!')

    return redirect(url_for('produtos.produtos_lista'))


def validar_dados(produto: prod.Produto, quantidade_atual):
    if produto.codigo == '' or produto.nome == '' or produto.quantidade_minima == '' or produto.status == '' or quantidade_atual == '':
        return False
    
    try:
        codigo = int(produto.codigo)
        quantidade_minima = int(produto.quantidade_minima)
        quantidade_atual = int(quantidade_atual)
    except (ValueError, TypeError):
        return False

    if codigo < 0 or quantidade_minima <= 0 or quantidade_atual < 0:
        return False
    
    return True
