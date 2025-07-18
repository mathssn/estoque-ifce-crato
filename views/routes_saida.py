from flask import Blueprint, redirect, flash, url_for, request, session
from datetime import datetime

from database.scripts.db import connect_db
import database.models.saidas as saida
from database.scripts.utils import check_saldo, recalculate_exits_balance
from database.scripts.utils import login_required

saidas = Blueprint('saidas', __name__)

@saidas.route('/cadastro/saida/', methods=['POST'])
@login_required
def cadastro_saida():
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('movimentacoes_diarias'))
    
    produto_id = request.form.get('produto_id')
    destino = request.form.get('destino')
    data = request.form.get('data_saida')
    quantidade = request.form.get('quantidade')
    observacao = request.form.get('observacao')

    nova_saida = saida.Saida(0, produto_id, destino, data, quantidade, observacao, session['user_id'])
    
    if not validar_dados(nova_saida):
        flash('Insira dados válidos para o cadastro da saída.')
        return redirect(url_for('movimentacoes_diarias', data=data))
    
    try:
        with connect_db() as (conn, cursor):
            if not check_saldo(data, cursor):
                flash('Não é possível adicionar saída para esse dia')
                return redirect(url_for('movimentacoes_diarias', data=data))

            saida.create(nova_saida, cursor)
    except Exception as e:
        flash(f'Falha ao cadastrar saída: {e}')
    else:
        flash('Saída cadastrada com sucesso!')

    return redirect(url_for('movimentacoes_diarias', data=data))


@saidas.route('/editar/saida/<int:saida_id>/', methods=['POST'])
@login_required
def editar_saida(saida_id):
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('movimentacoes_diarias'))
    
    try:
        with connect_db() as (conn, cursor):
            exit = saida.get(saida_id, cursor)
            
            exit.produto_id = request.form.get('edit_produto_id_saida')
            exit.destino = request.form.get('edit_destino_saida')
            exit.data_saida = request.form.get('edit_data_saida')
            exit.quantidade = request.form.get('edit_quantidade_saida')
            exit.observacao = request.form.get('edit_observacao_saida')
            
            if not validar_dados(exit):
                flash('Insira dados válidos para a edição da saída.')
                return redirect(url_for('movimentacoes_diarias', data=exit.data_saida))

            if not check_saldo(exit.data_saida, cursor):
                flash('Não é possível editar saída para esse dia')
                return redirect(url_for('movimentacoes_diarias', data=exit.data_saida))

            saida.update(saida_id, exit, cursor)
    except Exception as e:
        flash(f'Falha ao atualizar saída: {e}')
    else:
        flash('Saída atualizada com sucesso!')
    
    return redirect(url_for('movimentacoes_diarias', data=exit.data_saida))


@saidas.route('/excluir/saida/<int:saida_id>/', methods=['POST'])
@login_required
def excluir_saida(saida_id):
    if session['tipo'] not in ['Admin', 'Editor']:
        flash('Permissão negada')
        return redirect(url_for('movimentacoes_diarias'))
    
    try:
        with connect_db() as (conn, cursor):
            exit = saida.get(saida_id, cursor)

            if not check_saldo(exit.data_saida, cursor):
                flash('Não é possível excluir saída para esse dia. Saldo bloqueado.')
                return redirect(url_for('movimentacoes_diarias', data=exit.data_saida))

            saida.delete(saida_id, cursor)
            
            recalculate_exits_balance(exit.data_saida, exit, cursor, delete=True)
    except Exception as e:
        flash(f'Falha ao deletar saída: {e}')
    else:
        flash('Saída deletada com sucesso!')

    return redirect(url_for('movimentacoes_diarias', data=exit.data_saida))


def validar_dados(exit: saida.Saida):
    try:
        datetime.strptime(exit.data_saida, '%Y-%m-%d')
    except ValueError:
        return False

    try:
        quantidade = int(exit.quantidade)
    except (ValueError, TypeError):
        return False
    
    if quantidade <= 0:
        return False
    
    return True

