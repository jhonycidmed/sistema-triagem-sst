import streamlit as st
import pandas as pd
import unicodedata
import re
from motores.processador_dados import carregar_planilha_exames, carregar_matriz_treinamentos
from motores.regras_negocio import descobrir_treinamentos

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(texto):
    if not texto: return ""
    texto = str(texto).strip().upper()
    # Remove acentos
    texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Remove números iniciais (Ex: "1. CLINICO" -> "CLINICO")
    texto = re.sub(r'^\d+\.\s*', '', texto)
    return texto

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Triagem CIDMED", layout="centered")

def limpar_tudo():
    st.session_state.campo_exames = []
    st.session_state.campo_riscos = []

# --- ESTILIZAÇÃO CSS (FOCO EM NÃO CORTAR TEXTO E CORES CIDMED) ---
st.markdown("""
    <style>
    /* Ajuste para as Tags (caixinhas azuis) aparecerem completas no Safari/iPhone */
    [data-baseweb="tag"] {
        background-color: #285f9f !important;
        height: auto !important;
        max-width: 100% !important;
        padding: 5px 10px !important;
        margin: 2px !important;
    }
    [data-baseweb="tag"] span {
        color: white !important;
        font-size: 14px !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    
    /* Personalização das Caixas e Títulos */
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
    # Para facilitar a busca (ex: digitar "ruido" e achar "RUIDO"),
    # as listas de seleção agora usam os nomes normalizados.
    lista_riscos = sorted([normalizar(n) for n in df_bruto['Nome Risco'].dropna().unique()])
    lista_exames = sorted([normalizar(n) for n in df_bruto['Nome Exame'].dropna().unique()])

    # Interface Visual
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("assets/logo.png", use_container_width=True)
        except: pass

    st.markdown("<h2 style='text-align: center; color: #285f9f;'>Triagem Inteligente</h2>", unsafe_allow_html=True)
    st.divider()

    if st.session_state.get('campo_exames') or st.session_state.get('campo_riscos'):
        st.button("Limpar Tudo e Nova Consulta", on_click=limpar_tudo, use_container_width=True)

    # --- ORDEM INVERTIDA CONFORME SOLICITADO ---
    
    # 1. PRIMEIRO O RISCO
    riscos_sel = st.multiselect(
        "1. Selecione os Riscos:", 
        options=lista_riscos, 
        key="campo_riscos",
        placeholder="Ex: RUIDO, ALTURA, CALOR..."
    )

    # 2. SEGUNDO O EXAME
    exames_sel = st.multiselect(
        "2. Selecione os Exames:", 
        options=lista_exames, 
        key="campo_exames",
        placeholder="Ex: CLINICO, AUDIOMETRIA..."
    )

    if exames_sel and riscos_sel:
        st.divider()
        # O motor de regras usa a lógica de interseção (Gatilho Rápido)
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
            st.warning("Nenhum treinamento vinculado a esta combinação.")
            
    elif riscos_sel or exames_sel:
        st.info("💡 Continue a seleção: o sistema cruza o Risco com os Exames realizados.")
else:
    st.error("Erro Crítico: Arquivos de base de dados não encontrados.")
