def descobrir_treinamentos(exames_selecionados, riscos_selecionados, matriz_regras):
    treinamentos_obrigatorios = set()
    
    # Padroniza as seleções para maiúsculo para garantir o match
    exames_selecionados_upper = [str(e).upper().strip() for e in exames_selecionados]
    riscos_selecionados_upper = [str(r).upper().strip() for r in riscos_selecionados]
    
    for regra in matriz_regras:
        # Verifica se o risco bate
        if regra['risco'] in riscos_selecionados_upper:
            necessarios = set(regra['exames_necessarios'])
            selecionados = set(exames_selecionados_upper)
            
            # Se todos os necessários estiverem nos selecionados
            if necessarios.issubset(selecionados):
                if regra['treinamento'] and str(regra['treinamento']).lower() != 'nan':
                    treinamentos_obrigatorios.add(regra['treinamento'])
                
    return sorted(list(treinamentos_obrigatorios))
