import pandas as pd
import re

def carregar_planilha_exames(caminho):
    try:
        df = pd.read_excel(caminho, skiprows=2)
        # Limpa espaços em branco em toda a base bruta
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        return None

def carregar_matriz_treinamentos(caminho):
    try:
        df = pd.read_excel(caminho, skiprows=3)
        regras = []
        for _, linha in df.iterrows():
            if pd.isna(linha[0]) or pd.isna(linha[2]):
                continue
            
            # Limpa o Risco e o Treinamento
            risco = str(linha[0]).strip()
            treinamento = str(linha[3]).strip()
            
            # Limpa a lista de exames do combo
            exames_limpos = []
            for item in str(linha[2]).split('\n'):
                # Remove "1. ", "2. " e espaços nas pontas
                exame = re.sub(r'^\d+\.\s*', '', item).strip()
                if exame:
                    exames_limpos.append(exame)
            
            regras.append({
                "risco": risco,
                "exames_necessarios": exames_limpos,
                "treinamento": treinamento
            })
        return regras
    except Exception as e:
        return []
