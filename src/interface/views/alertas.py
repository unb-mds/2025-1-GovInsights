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


from services.search import SearchService
from data.operacoes_bd import inserir_nova_serie, deletar_serie

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
if 'search_service' not in st.session_state:
    st.session_state['search_service'] = SearchService()
    
pesquisa = st.session_state['search_service']

def change_page(page_name):
    st.session_state.current_page = page_name

# def inserir_nova_serie(codigo_serie: str, email_usuario: str, margem: str, ultima_atualizacao:str):
#     st.success("Alerta configurado com sucesso!")
#     detalhes_alerta = f"""
#             <div class="custom-popup">
#                 <h3>Detalhes do alerta</h3>
#                 <p><strong>E-mail:</strong> {email_usuario}</p>
#                 <p><strong>Porcentagem:</strong> {margem}%</p>
#                 <p><strong>Série Estatística:</strong> {codigo_serie}</p>
#                 <p><strong>Ultima atualização em:</strong> {ultima_atualizacao}</p>
#             </div>
#             """
#     st.markdown(detalhes_alerta, unsafe_allow_html=True)


def alertas_page():
#    st.markdown("""                SIDEBAR FECHADA
# <style>
# /* Esconder sidebar */
# section[data-testid="stSidebar"] {
#    display: none !important;
# }
#
# /* conteúdo ocupa a tela toda */
# div[class^="main"] {
#     margin-left: 0rem !important;
# }
# </style>
# """, unsafe_allow_html=True)

#    st.markdown("""
#    <script>
#    window.addEventListener('load', function () {
#        const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
#        if (sidebar) {
#            sidebar.style.transform = 'translateX(-100%)';
#            sidebar.style.visibility = 'hidden';
#            sidebar.style.width = '0px';
#            sidebar.style.padding = '0px';
#        }
#
#        const mainContent = window.parent.document.querySelector('.main');
#        if (mainContent) {
#            mainContent.style.marginLeft = '0px';
#        }
#    });
#    </script>
#""", unsafe_allow_html=True)


    st.title("Alertas")
    email = st.text_input("Digite seu e-mail para receber alertas")

    st.pills(
        label="Selecione a frequência da série",
        options=["Diária", "Mensal", "Trimestral", "Anual"],
        key="frequencia_pills",
        label_visibility="visible",
        default=st.session_state.get('frequencia')
    )
    
    filtrar_por_orgao = st.checkbox(label="Filtrar por órgão responsável", key="filtro_por_orgao")
    st.multiselect(
        label="Selecione os órgãos",
        options=pesquisa.get_available_sources(st.session_state['frequencia_pills']),
        placeholder="Ex.: Bacen, IBGE, IPEA, etc...",
        key="orgaos_multiselect",
        label_visibility="visible"
    )
    
    filtrar_por_tema = st.checkbox(label="Filtrar por tema", key="filtro_por_tema")
    st.multiselect(
        label="Selecione os temas",
        options=pesquisa.get_available_themes(st.session_state['frequencia_pills']),
        placeholder="Ex.: Comércio e Vendas, Finanças Públicas, etc...",
        key="temas_multiselect",
        label_visibility="visible",
        format_func=lambda x: x['THEME NAME']
        )


    porcentagem = st.slider("Porcentagem de variação para alerta", min_value=0, max_value=100, value=10, step=1)

    # Atualiza o resultado da pesquisa sempre que filtros mudam
    orgaos_selecionados = st.session_state['orgaos'] if filtrar_por_orgao else []
    temas_selecionados = st.session_state['temas'] if filtrar_por_tema else []

    st.session_state['resultado_pesquisa'] = pesquisa.search(
        st.session_state['frequencia_pills'],
        fonte_list=orgaos_selecionados,
        tema_list=temas_selecionados
    )
    
    st.markdown("#### Selecione ou pesquise uma série estatística")

    resultado_df = st.session_state['resultado_pesquisa']
    serie_selecionada = st.selectbox(
        label="Selecionar série",
        options=st.session_state['resultado_pesquisa'],
        key="serie_estatistica_alertas",
        label_visibility="collapsed",
        placeholder="Selecione ou pesquise uma série estatística...",
        format_func=lambda x: f"{x['NAME']} ({x['CODE']})",
        index=None
    )
    if serie_selecionada:
        df = ipea.timeseries(serie_selecionada['CODE'])
        ultima_atualizacao = df.iloc[0]["RAW DATE"]
        ultima_atualizacao = re.sub(r"[a-zA-Z].*", "", ultima_atualizacao)
        
        porcentagem = str(porcentagem)

        if st.button("Enviar alerta", key="enviar_alerta_button"):
            if not email:
                st.warning("Preencha o campo de e-mail.")
            elif not serie_selecionada:
                st.warning("Selecione uma série estatística.")
            else:
                try:
                    inserir_nova_serie(serie_selecionada['CODE'], email, porcentagem, ultima_atualizacao)
                    st.success("Alerta configurado com sucesso!")
                except Exception as error:
                    st.warning("Erro ao comunicar com BD")
                    

def del_alertas_page():
    st.title("Cancelar Inscrição de Alertas")
    email = st.text_input("Endereço de email:")
    serie = st.text_input("Código da Série:")

    st.markdown("""
        <div id="text_del">
            <p id="text_lam">Lamentamos que você esteja se desvinculando do nosso sistema. Esperamos ter sido úteis durante o período em que nos acompanhou.</p>
            <p id="exp">Ao continuar, você deixará de receber alertas relacionados a essa configuração. Se desejar, poderá ativá-los novamente a qualquer momento nas configurações.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Desativar Alerta"):
        try:
            deletar_serie(email, serie)
            st.success("Alerta deletado com sucesso!")
        except Exception as error:
            st.warning("Erro ao deletar serie no BD")
