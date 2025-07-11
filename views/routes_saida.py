from flask import Blueprint, redirect, flash, url_for, request

from database.scripts.db import connect_db
import database.models.saidas as saida
from database.scripts.utils import check_saldo, recalculate_exits_balance

saidas = Blueprint('saidas', __name__)


@saidas.route('/cadastro/saida/', methods=['POST'])
def cadastro_saida():
    produto_id = request.form.get('produto_id')
    destino = request.form.get('destino')
    data = request.form.get('data_saida')
    quantidade = request.form.get('quantidade')

    # Verifica se é possivel alterar o saldo do dia
    conn, cursor = connect_db()
    if not check_saldo(data, cursor):
        conn.close()
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=data))

    nova_saida = saida.Saida(0, produto_id, destino, data, quantidade)
    if not saida.create(nova_saida, cursor):
        flash('Erro ao cadastrar saida')
        conn.rollback()
    else:
        conn.commit()
    
    conn.close()
    return redirect(url_for('movimentacoes_diarias', data=data))


@saidas.route('/editar/saida/<int:saida_id>/', methods=['POST'])
def editar_saida(saida_id):
    conn, cursor = connect_db()
    saida_ = saida.get(saida_id, cursor)
    saida_.produto_id = request.form.get('edit_produto_id_saida')
    saida_.destino = request.form.get('edit_destino_saida')
    saida_.data_saida = request.form.get('edit_data_saida')
    saida_.quantidade = request.form.get('edit_quantidade_saida')

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(saida_.data_saida, cursor):
        conn.close()
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=saida_.data_saida))

    if not saida.update(saida_.id, saida_, cursor):
        flash('Erro ao atualizar saida')
        conn.rollback()
    else:
        conn.commit()

    conn.close()
    return redirect(url_for('movimentacoes_diarias', data=saida_.data_saida))


@saidas.route('/excluir/saida/<int:saida_id>/', methods=['POST'])
def excluir_saida(saida_id):
    conn, cursor = connect_db()
    saida_ = saida.get(saida_id, cursor)

    # Verifica se é possivel alterar o saldo do dia
    if not check_saldo(saida_.data_saida, cursor):
        conn.close()
        flash('Não é possivel adicionar saida para esse dia')
        return redirect(url_for('movimentacoes_diarias', data=saida_.data_saida))

    if not saida.delete(saida_id, cursor):
        flash('Erro ao deletar saida')
        conn.rollback()
        conn.close()
        return redirect(url_for('movimentacoes_diarias', data=saida_.data_saida))
    
    if not recalculate_exits_balance(saida_.data_saida, saida_, cursor, delete=True):
        flash('Erro ao atualizar o saldo do dia')
        conn.rollback()
    else:
        conn.commit()

    conn.close()
    return redirect(url_for('movimentacoes_diarias', data=saida_.data_saida))

