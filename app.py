import streamlit as st
import pandas as pd
import unicodedata
import re
from motores.processador_dados import carregar_planilha_exames, carregar_matriz_treinamentos
from motores.regras_negocio import descobrir_treinamentos

# --- FUNÇÃO AUXILIAR DE NORMALIZAÇÃO ---
def normalizar(texto):
    if not texto: return ""
    texto = str(texto).strip().upper()
    # Remove acentos (Ex: Á -> A)
    texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Remove números iniciais (Ex: "1. CLINICO" -> "CLINICO")
    texto = re.sub(r'^\d+\.\s*', '', texto)
    return texto

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Triagem CIDMED", layout="centered")

# --- LÓGICA DE LIMPEZA ---
def limpar_tudo():
    st.session_state.campo_exames = []
    st.session_state.campo_riscos = []

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    div[data-baseweb="select"] > div { border: 2px solid #285f9f !important; border-radius: 6px !important; }
    [data-baseweb="tag"] { background-color: #285f9f !important; padding: 6px 12px !important; max-width: none !important; }
    [data-baseweb="tag"] span { color: white !important; font-size: 15px !important; white-space: normal !important; }
    .stMultiSelect label p { font-size: 24px !important; font-weight: bold !important; color: #285f9f !important; }
    .texto-instrucao { font-size: 20px !important; color: #4F4F4F; margin-bottom: 20px; }
    .titulo-results { font-size: 26px !important; font-weight: bold !important; color: #285f9f !important; text-decoration: underline; margin-top: 25px; }
    .lista-treinamentos { list-style-type: disc; margin-top: 10px; padding-left: 25px; }
    .lista-treinamentos li { font-size: 22px !important; color: #1e4675 !important; margin-bottom: 15px; line-height: 1.4; }
    .marca-agua { position: fixed; bottom: 15px; left: 15px; font-size: 11px; color: rgba(79, 79, 79, 0.4); pointer-events: none; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="marca-agua">Criado por: João V. G</div>', unsafe_allow_html=True)

# --- CARREGAMENTO ---
caminho_bruto = "bases_de_dados/base_bruta.xls"
caminho_matriz = "bases_de_dados/matriz_ajustada.xlsx"

df_bruto = carregar_planilha_exames(caminho_bruto)
matriz_regras = carregar_matriz_treinamentos(caminho_matriz)

# --- INTERFACE ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try: st.image("assets/logo.png", use_container_width=True)
    except: pass

st.markdown("<h2 style='text-align: center; color: #285f9f;'>Triagem Inteligente de Treinamentos</h2>", unsafe_allow_html=True)
st.markdown("<p class='texto-instrucao'>Combine os Riscos e Exames para identificar as obrigatoriedades.</p>", unsafe_allow_html=True)
st.divider()

if df_bruto is not None:
    # CRIANDO DICIONÁRIOS DE TRADUÇÃO (PARA IGNORAR ACENTOS NO CÁLCULO)
    # Mostra o nome original, mas o sistema "pensa" no nome limpo
    mapa_exames = {nome: normalizar(nome) for nome in df_bruto['Nome Exame'].dropna().unique()}
    mapa_riscos = {nome: normalizar(nome) for nome in df_bruto['Nome Risco'].dropna().unique()}

    lista_exames_display = sorted(mapa_exames.keys())
    lista_riscos_display = sorted(mapa_riscos.keys())
    
    if st.session_state.get('campo_exames') or st.session_state.get('campo_riscos'):
        st.button("Limpar campos e Nova Consulta", on_click=limpar_tudo, use_container_width=True)

    # SELEÇÃO NA TELA
    exames_sel = st.multiselect("1. Selecione os Exames:", options=lista_exames_display, key="campo_exames", placeholder="Ex: Clínico, Ruído...")
    riscos_sel = st.multiselect("2. Selecione os Riscos:", options=lista_riscos_display, key="campo_riscos", placeholder="Ex: Ruído, Poeira...")

    if exames_sel and riscos_sel:
        # TRADUÇÃO: Converte o que foi selecionado para a versão "Sem Acento" antes de mandar para o motor
        exames_processar = [mapa_exames[e] for e in exames_sel]
        riscos_processar = [mapa_riscos[r] for r in riscos_sel]
        
        st.divider()
        # Chama o motor passando as versões limpas
        resultados = descobrir_treinamentos(exames_processar, riscos_processar, matriz_regras)
        
        if resultados:
            st.markdown("<p class='titulo-results'>Treinamentos Obrigatórios:</p>", unsafe_allow_html=True)
            html_lista = "<ul class='lista-treinamentos'>"
            for r in resultados:
                if str(r).lower() != 'nan':
                    html_lista += f"<li>{r}</li>"
            html_lista += "</ul>"
            st.markdown(html_lista, unsafe_allow_html=True)
        else:
            st.warning("Nenhum treinamento vinculado a esta combinação específica.")
            
    elif exames_sel or riscos_sel:
        st.info("💡 Continue selecionando: o sistema precisa do Exame e do Risco correspondente.")
else:
    st.error("Erro ao carregar arquivos. Verifique se estão na pasta 'bases_de_dados'.")
