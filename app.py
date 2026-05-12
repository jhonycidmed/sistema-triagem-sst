import streamlit as st
import pandas as pd
from motores.processador_dados import carregar_planilha_exames, carregar_matriz_treinamentos
from motores.regras_negocio import descobrir_treinamentos

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Triagem CIDMED", layout="centered")

# --- LÓGICA DE LIMPEZA ---
def limpar_tudo():
    st.session_state.campo_exames = []
    st.session_state.campo_riscos = []

# --- ESTILIZAÇÃO CSS (LISTA VERTICAL E FONTES) ---
st.markdown("""
    <style>
    /* 1. CAIXAS DE SELEÇÃO */
    div[data-baseweb="select"] > div { 
        border: 2px solid #285f9f !important; 
        border-radius: 6px !important; 
    }
    
    /* TAGS: Texto completo e sem abreviações */
    [data-baseweb="tag"] {
        max-width: none !important;
        height: auto !important;
        background-color: #285f9f !important;
        padding: 6px 12px !important;
    }
    [data-baseweb="tag"] span {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        color: white !important;
        font-size: 15px !important;
        line-height: 1.3 !important;
    }

    /* FONTES DOS RÓTULOS */
    .stMultiSelect label p {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #285f9f !important;
    }

    .texto-instrucao { font-size: 20px !important; color: #4F4F4F; margin-bottom: 20px; }
    
    .titulo-resultados {
        font-size: 26px !important;
        font-weight: bold !important;
        color: #285f9f !important;
        text-decoration: underline;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    /* ESTILO DA LISTA DE RESULTADOS (LIMPA E SEM NEGRITO) */
    .lista-treinamentos {
        list-style-type: disc;
        margin-top: 10px;
        padding-left: 25px;
    }
    .lista-treinamentos li {
        font-size: 22px !important;
        color: #1e4675 !important;
        font-weight: normal !important;
        margin-bottom: 15px;
        line-height: 1.4;
    }

    /* RODAPÉ */
    .marca-agua { 
        position: fixed; bottom: 15px; left: 15px; 
        font-size: 11px; color: rgba(79, 79, 79, 0.4); 
        pointer-events: none; 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="marca-agua">Criado por: João V. G</div>', unsafe_allow_html=True)

# --- CARREGAMENTO ---
# IMPORTANTE: Renomeie seus arquivos na pasta bases_de_dados para estes nomes abaixo
caminho_bruto = "bases_de_dados/base_bruta.xls"
caminho_matriz = "bases_de_dados/matriz_ajustada.xlsx"

df_bruto = carregar_planilha_exames(caminho_bruto)
matriz_regras = carregar_matriz_treinamentos(caminho_matriz)

# --- INTERFACE ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try: 
        st.image("assets/logo.png", use_container_width=True)
    except: 
        pass

st.markdown("<h2 style='text-align: center; color: #285f9f;'>Triagem Inteligente de Treinamentos</h2>", unsafe_allow_html=True)
st.markdown("<p class='texto-instrucao'>Combine os Riscos e Exames para identificar as obrigatoriedades.</p>", unsafe_allow_html=True)
st.divider()

if df_bruto is not None:
    lista_exames = sorted(df_bruto['Nome Exame'].dropna().unique())
    lista_riscos = sorted(df_bruto['Nome Risco'].dropna().unique())
    
    if st.session_state.get('campo_exames') or st.session_state.get('campo_riscos'):
        st.button("Limpar campos e Nova Consulta", on_click=limpar_tudo, use_container_width=True)

    exames_sel = st.multiselect("1. Selecione os Exames:", options=lista_exames, key="campo_exames", placeholder="Clique para selecionar")
    riscos_sel = st.multiselect("2. Selecione os Riscos:", options=lista_riscos, key="campo_riscos", placeholder="Clique para selecionar")

    if exames_sel and riscos_sel:
        st.divider()
        resultados = descobrir_treinamentos(exames_sel, riscos_sel, matriz_regras)
        
        if resultados:
            st.markdown("<p class='titulo-resultados'>Treinamentos Obrigatórios:</p>", unsafe_allow_html=True)
            
            html_lista = "<ul class='lista-treinamentos'>"
            for r in resultados:
                itens = str(r).split('\n')
                for i in itens:
                    i_limpo = i.strip()
                    if i_limpo and i_limpo.lower() != 'nan':
                        html_lista += f"<li>{i_limpo}</li>"
            html_lista += "</ul>"
            
            st.markdown(html_lista, unsafe_allow_html=True)
        else:
            st.warning("Nenhum treinamento vinculado a esta combinação específica.")
            
    elif exames_sel or riscos_sel:
        st.info("💡 Continue selecionando: o sistema precisa do Exame e do Risco correspondente.")
else:
    st.error("Arquivos não encontrados. Verifique a pasta 'bases_de_dados'.")