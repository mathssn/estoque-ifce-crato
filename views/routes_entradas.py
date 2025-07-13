from flask import Blueprint, redirect, flash, url_for, request
from datetime import datetime

from database.scripts.db import connect_db
import database.models.entradas as entrada
from database.scripts.utils import check_saldo, recalculate_entries_balance

entradas = Blueprint('entradas', __name__)


@entradas.route('/cadastro/entrada/', methods=['POST'])
def cadastro_entrada():
    produto_id = request.form.get('produto_id')
    data = request.form.get('data_entrada')
    quantidade = request.form.get('quantidade')

    nova_entrada = entrada.Entrada(0, produto_id, data, quantidade)
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
    except:
        flash('Falha ao cadastrar entrada')
    else:
        flash('Entrada cadastrada com sucesso!')

    return redirect(url_for('movimentacoes_diarias', data=data))


@entradas.route('/editar/entrada/<int:entrada_id>/', methods=['POST'])
def editar_entrada(entrada_id):
    try:
        with connect_db() as (conn, cursor):
            entrie = entrada.get(entrada_id, cursor)
            entrie.produto_id = request.form.get('edit_produto_id_entrada')
            entrie.data_entrada = request.form.get('edit_data_entrada')
            entrie.quantidade = request.form.get('edit_quantidade_entrada')
            if not validar_dados(entrie):
                flash('Insira dados válidos')
                return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))

            # Verifica se é possivel alterar o saldo do dia
            if not check_saldo(entrie.data_entrada, cursor):
                flash('Não é possivel adicionar saida para esse dia')
                return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))

            entrada.update(entrada_id, entrie, cursor)
    except:
        flash('Falha ao atualizar entrada!')
    else:
        flash('Entrada atualizada com sucesso')
    
    return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))


@entradas.route('/excluir/entrada/<int:entrada_id>/', methods=['POST'])
def excluir_entrada(entrada_id):
    try:
        with connect_db() as (conn, cursor):
            entrie = entrada.get(entrada_id, cursor)

            # Verifica se é possivel alterar o saldo do dia
            if not check_saldo(entrie.data_entrada, cursor):
                flash('Não é possivel adicionar saida para esse dia')
                return redirect(url_for('movimentacoes_diarias', data=entrie.data_entrada))

            entrada.delete(entrada_id, cursor)
            
            recalculate_entries_balance(entrie.data_entrada, entrie, cursor, delete=True)
    except:
        flash('Falha ao deletar entrada')
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