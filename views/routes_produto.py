from flask import Blueprint, render_template, redirect, flash, url_for, request
from datetime import date

from database.scripts.db import connect_db
import database.models.produto as prod
import database.models.dias_fechados as dias
import database.models.saldo_diario as saldos
import database.models.entradas as entradas

produtos = Blueprint('produtos', __name__)


@produtos.route('/produtos/')
def produtos_lista():
    conn, cursor = connect_db()
    produtos_list = prod.list_all(cursor)
    conn.close()

    return render_template('produtos.html', produtos=produtos_list)

@produtos.route('/cadastro/produtos/', methods=['POST'])
def cadastro_produtos():
    codigo = request.form.get('codigo')
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    unidade = request.form.get('unidade')
    quantidade_minima = request.form.get('quantidade_minima')
    quantidade_atual = request.form.get('quantidade_atual')
    status = request.form.get('status')

    novo_produto = prod.Produto(0, codigo, nome, descricao, unidade, quantidade_minima, status)

    conn, cursor = connect_db()
    if not prod.create(novo_produto, cursor):
        flash('Erro ao cadastrar produto')
        conn.rollback()
        conn.close()
        return redirect(url_for('produtos.produtos_lista'))
    
    # Cria a entrada inicial do produto
    data_atual = date.today().isoformat()

    dia = dias.get(data_atual, cursor)
    if not dia:
        dia = dias.DiasFechados(data_atual, False)
        if not dias.create(dia, cursor):
            conn.rollback()
            conn.close()
            return redirect(url_for('produtos.produtos_lista'))

    saldo_diario = saldos.SaldoDiario(0, novo_produto.id, data_atual, 0, quantidade_atual, 0, quantidade_atual)
    if not saldos.create(saldo_diario, cursor):
        flash('Erro ao cadastrar a quantidade atual')
        conn.rollback()
        conn.close()
        return redirect(url_for('produtos.produtos_lista'))
        
    entrada = entradas.Entrada(0, novo_produto.id, data_atual, quantidade_atual)
    if not entradas.create(entrada, cursor):
        flash('Erro ao cadastrar a quantidade atual')
        conn.rollback()
        conn.close()
        return redirect(url_for('produtos.produtos_lista'))
    
    conn.commit()
    conn.close()
    flash('Produto cadastrado com sucesso')
    return redirect(url_for('produtos.produtos_lista'))

@produtos.route('/editar/produto/<int:produto_id>/', methods=['POST'])
def editar_produto(produto_id):
    conn, cursor = connect_db()

    produto = prod.get(produto_id, cursor)
    produto.codigo = request.form.get('edit_codigo')
    produto.nome = request.form.get('edit_nome')
    produto.descricao = request.form.get('edit_descricao')
    produto.unidade = request.form.get('edit_unidade')
    produto.quantidade_minima = request.form.get('edit_quantidade_minima')

    if not prod.update(produto.id, produto, cursor):
        flash('Erro ao atualizar produto')
        conn.rollback()
    else:
        conn.commit()

    conn.close()
    return redirect(url_for('produtos.produtos_lista'))


@produtos.route('/excluir/produto/<int:produto_id>/', methods=['POST'])
def excluir_produto(produto_id):
    conn, cursor = connect_db()
    if not prod.delete(produto_id, cursor):
        flash('Erro ao deletar produto')
        conn.rollback()
    else:
        conn.commit()

    conn.close()
    return redirect(url_for('produtos.produtos_lista'))
