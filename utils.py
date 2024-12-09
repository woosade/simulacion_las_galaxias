def es_horario_punta(tiempo_actual, horarios_punta):
    tiempo_dia = tiempo_actual % (24*3600)
    for inicio, fin in horarios_punta:
        if inicio <= tiempo_dia <= fin:
            return True
    return False
