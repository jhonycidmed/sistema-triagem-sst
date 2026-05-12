def descobrir_treinamentos(exames_selecionados_limpos, riscos_selecionados_limpos, matriz_regras):
    treinamentos_obrigatorios = set()
    
    for regra in matriz_regras:
        # Se o risco selecionado (limpo) está na regra
        if regra['risco'] in riscos_selecionados_limpos:
            necessarios = set(regra['exames_necessarios'])
            selecionados = set(exames_selecionados_limpos)
            
            # Se todos os necessários da regra estão entre os selecionados
            if necessarios.issubset(selecionados):
                if regra['treinamento'] and str(regra['treinamento']).lower() != 'nan':
                    treinamentos_obrigatorios.add(regra['treinamento'])
                
    return sorted(list(treinamentos_obrigatorios))
