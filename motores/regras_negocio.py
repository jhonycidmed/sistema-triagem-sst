def descobrir_treinamentos(exames_selecionados, riscos_selecionados, matriz_regras):
    """
    Só recomenda o treinamento se:
    1. O Risco da regra foi selecionado pela atendente.
    2. TODOS os exames necessários para aquele risco foram selecionados.
    """
    treinamentos_finais = []
    
    set_exames_user = set(exames_selecionados)
    set_riscos_user = set(riscos_selecionados)

    for regra in matriz_regras:
        nome_risco_regra = regra["risco"]
        set_exames_regra = set(regra["exames_necessarios"])
        
        # CONDIÇÃO DE GATILHO: Risco presente E Combo de Exames completo
        if nome_risco_regra in set_riscos_user:
            if set_exames_regra.issubset(set_exames_user):
                treino = regra["treinamento"]
                # Ignora se estiver vazio ou com o texto de placeholder
                if treino and "Nenhum curso" not in treino and str(treino).lower() != "nan":
                    if treino not in treinamentos_finais:
                        treinamentos_finais.append(treino)

    return treinamentos_finais
