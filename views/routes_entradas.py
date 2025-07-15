from flask import Blueprint, redirect, flash, url_for, request, session
from datetime import datetime

from database.scripts.db import connect_db
import database.models.entradas as entrada
from database.scripts.utils import check_saldo, recalculate_entries_balance
from database.scripts.utils import login_required

entradas = Blueprint('entradas', __name__)

@entradas.route('/cadastro/entrada/', methods=['POST'])
@login_required
def cadastro_entrada():
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('movimentacoes_diarias'))
    
    produto_id = request.form.get('produto_id')
    data = request.form.get('data_entrada')
    quantidade = request.form.get('quantidade')
    observacao = request.form.get('observacao')

    nova_entrada = entrada.Entrada(0, produto_id, data, quantidade, observacao, session['user_id'])
    if not validar_dados(nova_entrada):
        flash('Insira dados validos')
        return redirect(url_for('movimentacoes_diarias', data=data))
    
    # Verifica se é possivel alterar o saldo do dia
    try:
        with connect_db() as (conn, cursor):
            if not check_saldo(data, cursor):
                flash('Não é possivel adicionar saida para esse dia')
                return redirect(url_for('movimentacoes_diarias', data=data))

            entrada.create(nova_entrada, cursor)
    except Exception as e:
        flash(f'Falha ao cadastrar entrada: {e}')
    else:
        flash('Entrada cadastrada com sucesso!')

    return redirect(url_for('movimentacoes_diarias', data=data))


@entradas.route('/editar/entrada/<int:entrada_id>/', methods=['POST'])
@login_required
def editar_entrada(entrada_id):
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('movimentacoes_diarias'))
    
    try:
        with connect_db() as (conn, cursor):
            entrie = entrada.get(entrada_id, cursor)
            entrie.produto_id = request.form.get('edit_produto_id_entrada')
            entrie.data_entrada = request.form.get('edit_data_entrada')
            entrie.quantidade = request.form.get('edit_quantidade_entrada')
            entrie.observacao = request.form.get('edit_observacao_entrada')
            
            if not validar_dados(entrie):
                flash('Insira dados válidos')
                return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))

            # Verifica se é possivel alterar o saldo do dia
            if not check_saldo(entrie.data_entrada, cursor):
                flash('Não é possivel adicionar saida para esse dia')
                return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))

            entrada.update(entrada_id, entrie, cursor)
    except Exception as e:
        flash(f'Falha ao atualizar entrada: {e}')
    else:
        flash('Entrada atualizada com sucesso')
    
    return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))


@entradas.route('/excluir/entrada/<int:entrada_id>/', methods=['POST'])
@login_required
def excluir_entrada(entrada_id):
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('movimentacoes_diarias'))
    
    try:
        with connect_db() as (conn, cursor):
            entrie = entrada.get(entrada_id, cursor)

            # Verifica se é possivel alterar o saldo do dia
            if not check_saldo(entrie.data_entrada, cursor):
                flash('Não é possivel adicionar saida para esse dia')
                return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))

            entrada.delete(entrada_id, cursor)
            
            recalculate_entries_balance(entrie.data_entrada, entrie, cursor, delete=True)
    except Exception as e:
        flash(f'Falha ao deletar entrada: {e}')
    else:
        flash('Entrada deletada com sucesso')

    return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))


def validar_dados(entrie: entrada.Entrada):
    try:
        datetime.strptime(entrie.data_entrada, '%Y-%m-%d')
    except ValueError:
        return False

    try:
        quantidade = int(entrie.quantidade)
    except (ValueError, TypeError):
        return False
    
    if quantidade <= 0:
        return False
    
    return True