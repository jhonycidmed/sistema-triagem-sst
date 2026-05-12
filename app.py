import streamlit as st
import pandas as pd
import unicodedata
import re
from motores.processador_dados import carregar_planilha_exames, carregar_matriz_treinamentos
from motores.regras_negocio import descobrir_treinamentos

# --- NORMALIZAÇÃO ---
def normalizar(texto):
    if not texto: return ""
    texto = str(texto).strip().upper()
    texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'^\d+\.\s*', '', texto)
    return texto

st.set_page_config(page_title="Triagem CIDMED", layout="centered")

def limpar_tudo():
    st.session_state.campo_exames = []
    st.session_state.campo_riscos = []

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
    [data-baseweb="tag"] { background-color: #285f9f !important; height: auto !important; max-width: 100% !important; }
    [data-baseweb="tag"] span { color: white !important; font-size: 14px !important; white-space: normal !important; }
    div[data-baseweb="select"] > div { border: 2px solid #285f9f !important; border-radius: 6px !important; }
    .stMultiSelect label p { font-size: 22px !important; font-weight: bold !important; color: #285f9f !important; }
    .titulo-results { font-size: 26px !important; font-weight: bold !important; color: #285f9f !important; text-decoration: underline; margin-top: 25px; }
    .lista-treinamentos li { font-size: 20px !important; color: #1e4675 !important; margin-bottom: 12px; line-height: 1.4; }
    .marca-agua { position: fixed; bottom: 15px; left: 15px; font-size: 11px; color: rgba(79, 79, 79, 0.4); pointer-events: none; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="marca-agua">Criado por: João V. G</div>', unsafe_allow_html=True)

# --- CARREGAMENTO ---
caminho_bruto = "bases_de_dados/base_bruta.xls"
caminho_matriz = "bases_de_dados/matriz_ajustada.xlsx"

df_bruto = carregar_planilha_exames(caminho_bruto)
matriz_regras = carregar_matriz_treinamentos(caminho_matriz)

if df_bruto is not None:
    lista_riscos_completa = sorted([normalizar(n) for n in df_bruto['Nome Risco'].dropna().unique()])
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("assets/logo.png", use_container_width=True)
        except: pass

    st.markdown("<h2 style='text-align: center; color: #285f9f;'>Triagem Inteligente</h2>", unsafe_allow_html=True)
    st.divider()

    if st.session_state.get('campo_exames') or st.session_state.get('campo_riscos'):
        st.button("Limpar Tudo e Nova Consulta", on_click=limpar_tudo, use_container_width=True)

    # 1. SELECIONAR O RISCO
    riscos_sel = st.multiselect("1. Selecione o Risco:", options=lista_riscos_completa, key="campo_riscos")

    # 2. FILTRO DINÂMICO DE EXAMES
    lista_exames_filtrada = []
    placeholder_exame = "Selecione o risco primeiro..."
    
    if riscos_sel:
        exames_permitidos = set()
        # Busca na matriz quais exames estão ligados aos riscos escolhidos
        for regra in matriz_regras:
            if regra['risco'] in riscos_sel:
                for ex in regra['exames_necessarios']:
                    exames_permitidos.add(ex)
        
        if exames_permitidos:
            lista_exames_filtrada = sorted(list(exames_permitidos))
            placeholder_exame = "Selecione os exames realizados..."
        else:
            # Caso o risco não tenha regra na matriz, mostra todos da base bruta para não travar o uso
            lista_exames_filtrada = sorted([normalizar(n) for n in df_bruto['Nome Exame'].dropna().unique()])
            placeholder_exame = "Risco sem regra específica. Mostrando todos os exames."

    # 3. SELECIONAR O EXAME
    exames_sel = st.multiselect(
        "2. Selecione o Exame:", 
        options=lista_exames_filtrada, 
        key="campo_exames",
        placeholder=placeholder_exame,
        disabled=not riscos_sel
    )

    if exames_sel and riscos_sel:
        st.divider()
        resultados = descobrir_treinamentos(exames_sel, riscos_sel, matriz_regras)
        
        if resultados:
            st.markdown("<p class='titulo-results'>Treinamentos Recomendados:</p>", unsafe_allow_html=True)
            html_lista = "<ul class='lista-treinamentos'>"
            for r in resultados:
                if str(r).lower() != 'nan':
                    html_lista += f"<li>{r}</li>"
            html_lista += "</ul>"
            st.markdown(html_lista, unsafe_allow_html=True)
        else:
            st.warning("A combinação de exames não gera treinamentos para este risco.")
            
    elif riscos_sel:
        st.info("💡 Selecione o exame para validar a recomendação.")
else:
    st.error("Arquivos não encontrados.")
