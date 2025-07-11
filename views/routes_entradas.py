from flask import Blueprint, redirect, flash, url_for, request

from database.scripts.db import connect_db
import database.models.entradas as entrada
from database.scripts.utils import check_saldo, recalculate_entries_balance

entradas = Blueprint('entradas', __name__)


@entradas.route('/cadastro/entrada/', methods=['POST'])
def cadastro_entrada():
    produto_id = request.form.get('produto_id')
    data = request.form.get('data_entrada')
    quantidade = request.form.get('quantidade')

    # Verifica se é possivel alterar o saldo do dia
    conn, cursor = connect_db()
    if not check_saldo(data, cursor):
        conn.close()
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=data))

    nova_entrada = entrada.Entrada(0, produto_id, data, quantidade)
    if not entrada.create(nova_entrada, cursor):
        conn.rollback()
        flash('Erro ao cadastrar entradas')
    else:
        conn.commit()

    conn.close()
    return redirect(url_for('movimentacoes_diarias', data=data))


@entradas.route('/editar/entrada/<int:entrada_id>/', methods=['POST'])
def editar_entrada(entrada_id):
    conn, cursor = connect_db()
    entrada_ = entrada.get(entrada_id, cursor)
    entrada_.produto_id = request.form.get('edit_produto_id_entrada')
    entrada_.data_entrada = request.form.get('edit_data_entrada')
    entrada_.quantidade = request.form.get('edit_quantidade_entrada')

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(entrada_.data_entrada, cursor):
        conn.close()
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=entrada_.data_entrada))

    if not entrada.update(entrada_id, entrada_, cursor):
        conn.rollback()
        flash('Erro ao atualizar entrada')
    else:
        conn.commit()
    
    conn.close()
    return redirect(url_for('movimentacoes_diarias', data=entrada_.data_entrada))


@entradas.route('/excluir/entrada/<int:entrada_id>/', methods=['POST'])
def excluir_entrada(entrada_id):
    conn, cursor = connect_db()
    entrada_ = entrada.get(entrada_id, cursor)

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(entrada_.data_entrada, cursor):
        conn.close()
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=entrada_.data_entrada))

    if not entrada.delete(entrada_id, cursor):
        conn.rollback()
        conn.close()
        flash('Erro ao deletar entradas')
        return redirect(url_for('movimentacoes_diarias', data=entrada_.data_entrada))
    
    if not recalculate_entries_balance(entrada_.data_entrada, entrada_, cursor, delete=True):
        flash('Erro ao atualizar o saldo do dia')
        conn.rollback()
    else:
        conn.commit()

    conn.close()
    return redirect(url_for('movimentacoes_diarias', data=entrada_.data_entrada))

