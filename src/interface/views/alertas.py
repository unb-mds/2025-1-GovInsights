import streamlit as st 
import ipeadatapy as ipea
import plotly.graph_objects as go
from pathlib import Path
import sys
import os
import re

current_dir = Path(__file__).parent
img_path = current_dir / "assets" / "img" / "Icon.png"
css_path = current_dir / "assets" / "stylesheets" / "style2.css"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("Arquivo CSS não encontrado em: " + str(css_path))

from services.search import search
# from data.operacoes_bd import inserir_nova_serie


if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

if 'orgaos' not in st.session_state:
    st.session_state['orgaos'] = []
if 'temas' not in st.session_state:
    st.session_state['temas'] = []
if 'frequencia' not in st.session_state:
    st.session_state['frequencia'] = None
if 'resultado_pesquisa' not in st.session_state:
    st.session_state['resultado_pesquisa'] = []

def change_page(page_name):
    st.session_state.current_page = page_name

def inserir_nova_serie(codigo_serie: str, email_usuario: str, margem: str, ultima_atualizacao:str):
    st.success("Alerta configurado com sucesso!")
    detalhes_alerta = f"""
            <div class="custom-popup">
                <h3>Detalhes do alerta</h3>
                <p><strong>E-mail:</strong> {email_usuario}</p>
                <p><strong>Porcentagem:</strong> {margem}%</p>
                <p><strong>Série Estatística:</strong> {codigo_serie}</p>
                <p><strong>Ultima atualização em:</strong> {ultima_atualizacao}</p>
            </div>
            """
    st.markdown(detalhes_alerta, unsafe_allow_html=True)

def alertas_page():
    st.title("Alertas")
    email = st.text_input("Endereço de email para receber alertas")
    
    filtrar_por_orgao = st.checkbox(label="Filtrar por órgão responsável", key="checkbox-orgao")
    orgaos = st.multiselect(
        label="Selecione os órgãos",
        options=ipea.sources(),
        placeholder="Ex.: Bacen, IBGE, IPEA, etc...",
        key="orgaos_multiselect",
        label_visibility="visible",
    )

    df_temas = ipea.themes()

    filtrar_por_tema = st.checkbox(label="Filtrar por tema", key="checkbox-tema")
    temas = st.multiselect(
        label="Selecione os temas",
        options=df_temas['ID'],
        format_func=lambda x: df_temas.loc[df_temas['ID'] == x, 'NAME'].values[0],
        placeholder="Ex.: Comércio e Vendas, Finanças Públicas, etc...",
        key="temas_multiselect",
        label_visibility="visible",
    )
    
    filtrar_por_frequencia = st.checkbox(label="Filtrar por periodicidade", key="checkbox-frequencia")
    frequencia = st.pills(
        label="Selecione a frequência da série",
        options=["Diária", "Mensal", "Trimestral", "Anual"],
        key="frequencia_pills",
        label_visibility="visible",
        default=None
    )

    porcentagem = st.slider("Porcentagem de variação para alerta", min_value=0, max_value=100, value=10, step=1)

    orgaos_selecionados = st.session_state['orgaos'] if filtrar_por_orgao else []
    temas_selecionados = st.session_state['temas'] if filtrar_por_tema else []
    frequencia_selecionada = st.session_state['frequencia'] if filtrar_por_frequencia else []
    st.session_state['resultado_pesquisa'] = search(orgaos_selecionados, temas_selecionados, frequencia_selecionada)


    st.markdown("####Selecione ou pesquise uma série estatística")

    resultado_df = st.session_state['resultado_pesquisa']
    serie_selecionada = st.selectbox(
        label="Selecionar série",
        options=resultado_df['CODE'] if not resultado_df.empty else [],
        key="serie_estatistica_alertas",
        label_visibility="collapsed",
        placeholder="Selecione ou pesquise uma série estatística...",
        format_func=lambda x: resultado_df.loc[resultado_df['CODE'] == x, 'NAME'].values[0] if not resultado_df.empty else '',
        index=None
    )

    df = ipea.timeseries(serie_selecionada)
    ultima_atualizacao = df.iloc[0]["RAW DATE"]
    ultima_atualizacao = re.sub(r"[a-zA-Z].*", "", ultima_atualizacao)
    
    porcentagem = str(porcentagem)
    if st.button("Enviar alerta", key="enviar_alerta_button"):
        if not email:
            st.warning("Preencha o campo de e-mail.")
        elif not serie_selecionada:
            st.warning("Selecione uma série estatística.")
        else:
            
            inserir_nova_serie(serie_selecionada, email, porcentagem, ultima_atualizacao)
            