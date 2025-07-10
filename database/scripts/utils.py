
def recalculate_diary_balance(data, produto_id):
    import database.models.saldo_diario as saldos
    import database.models.saidas as saidas
    import database.models.entradas as entradas

    saldo = saldos.get_by_date_and_product(data, produto_id)
    if not saldo:
        return False

    saidas_ = saidas.list_by_date(data)
    entradas_ = entradas.list_by_date(data)

    total_saidas = 0
    total_entradas = 0

    for saida in saidas_:
        if saida.produto_id == produto_id:
            total_saidas += saida.quantidade
    
    for entrada in entradas_:
        if entrada.produto_id == produto_id:
            total_entradas += entrada.quantidade
    
    qntd_final = saldo.quantidade_inicial + total_entradas - total_saidas
    if qntd_final < 0:
        return False
    
    saldo.quantidade_saida = total_saidas
    saldo.quantidade_entrada = total_entradas
    saldo.quantidade_final = qntd_final
    saldos.update(saldo.id, saldo)
    return True

def recalculate_exits_balance(data, saida, update=False):
    import database.models.saldo_diario as saldos
    import database.models.saidas as saidas

    saldo = saldos.get_by_date_and_product(data, saida.produto_id)
    if not saldo:
        return False

    saidas_ = saidas.list_by_date(data)
    total_saidas = 0

    for s in saidas_:
        if s.produto_id == int(saida.produto_id):
            if update and s.id == saida.id:
                total_saidas += int(saida.quantidade)
            else:
                total_saidas += s.quantidade
    
    if not update:
        total_saidas += int(saida.quantidade)
    
    qntd_final = saldo.quantidade_inicial + saldo.quantidade_entrada - total_saidas
    print(f'{saldo.quantidade_inicial} + {saldo.quantidade_entrada} - {total_saidas} = {qntd_final}')
    if qntd_final < 0:
        return False

    saldo.quantidade_saida = total_saidas
    saldo.quantidade_final = qntd_final
    saldos.update(saldo.id, saldo)
    return True


def recalculate_entries_balance(data, entrada, update=False):
    import database.models.saldo_diario as saldos
    import database.models.entradas as entradas

    saldo = saldos.get_by_date_and_product(data, entradas.produto_id)
    if not saldo:
        return False

    entradas_ = entradas.list_by_date(data)
    total_entradas = 0

    for e in entradas_:
        if e.produto_id == int(entrada.produto_id):
            if update and e.id == entrada.id:
                total_entradas += int(entrada.quantidade)
            else:
                total_entradas += e.quantidade
    
    if not update:
        total_entradas += int(entrada.quantidade)
    
    qntd_final = saldo.quantidade_inicial + total_entradas - saldo.quantidade_saida
    if qntd_final < 0:
        return False

    saldo.quantidade_entrada = total_entradas
    saldo.quantidade_final = qntd_final
    saldos.update(saldo.id, saldo)
    return True


def check_saldo(data):
    import database.models.dias_fechados as dias
    dia = dias.get(data)
    if not dia:
        return False
    if dia.fechado:
        return False
    
    return True