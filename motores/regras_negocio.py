def descobrir_treinamentos(exames_selecionados, riscos_selecionados, matriz_regras):
    """
    Função que cruza os dados selecionados com a matriz de regras.
    Utiliza lógica de Interseção (Gatilho Rápido).
    """
    treinamentos_obrigatorios = set()
    
    # Transformamos as listas em Sets (conjuntos) para cálculos matemáticos mais rápidos
    set_exames_usuario = set(exames_selecionados)
    set_riscos_usuario = set(riscos_selecionados)
    
    for regra in matriz_regras:
        # 1. VERIFICAÇÃO DO RISCO:
        # Se o risco da regra está presente na lista que o usuário selecionou
        if regra['risco'] in set_riscos_usuario:
            
            # 2. VERIFICAÇÃO DO EXAME (Gatilho Rápido):
            # Criamos um conjunto com os exames necessários para esta regra
            exames_da_regra = set(regra['exames_necessarios'])
            
            # Verificamos se há INTERSEÇÃO entre o que a regra pede e o que o usuário marcou.
            # Se houver pelo menos um item em comum, a condição é verdadeira.
            if exames_da_regra.intersection(set_exames_usuario):
                treinamento = str(regra['treinamento']).strip()
                
                # Evita adicionar valores vazios ou erros de planilha (nan)
                if treinamento and treinamento.lower() != 'nan':
                    treinamentos_obrigatorios.add(treinamento)
                
    # Retorna a lista organizada por ordem alfabética
    return sorted(list(treinamentos_obrigatorios))
