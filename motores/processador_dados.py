import pandas as pd
import re
import unicodedata

def normalizar_texto(texto):
    if pd.isna(texto): return ""
    # Remove acentos, transforma em maiúsculo e tira espaços extras
    texto = str(texto).strip().upper()
    texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Remove números iniciais (ex: "1. CLINICO" -> "CLINICO")
    texto = re.sub(r'^\d+\.\s*', '', texto)
    return texto

def carregar_planilha_exames(caminho):
    try:
        df = pd.read_excel(caminho, skiprows=2)
        # Criamos uma coluna 'Busca' para o motor e mantemos a original para a tela
        df['Exame_Limpo'] = df['Nome Exame'].apply(normalizar_texto)
        df['Risco_Limpo'] = df['Nome Risco'].apply(normalizar_texto)
        return df
    except:
        return None

def carregar_matriz_treinamentos(caminho):
    try:
        # skiprows=3 se a sua planilha começar na linha 4
        df = pd.read_excel(caminho, skiprows=3)
        regras = []
        for _, linha in df.iterrows():
            if pd.isna(linha.iloc[0]) or pd.isna(linha.iloc[2]): continue
            
            risco_norm = normalizar_texto(linha.iloc[0])
            exames_brutos = str(linha.iloc[2]).split('\n')
            exames_norm = [normalizar_texto(e) for e in exames_brutos if e.strip()]
            
            regras.append({
                "risco": risco_norm,
                "exames_necessarios": exames_norm,
                "treinamento": str(linha.iloc[3]).strip()
            })
        return regras
    except:
        return []
