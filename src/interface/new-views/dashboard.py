import streamlit as st 
import ipeadatapy as ipea
import plotly.graph_objects as go
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from services.search import search
from services.graph import plotar_grafico_periodo, calcular_percentual_aumento_por_periodo

current_dir = Path(__file__).parent
img_path = current_dir / "assets" / "img" / "Icon.png"

# Configuração da página
st.set_page_config(
    page_title="GovInsights",
    layout="wide",
    page_icon= img_path
)

# # Importa o CSS customizado
try:
    with open("src/interface/new-views/assets/stylesheets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("O arquivo de estilo style.css não foi encontrado. Verifique o caminho.")

# Estado da sessão para controlar a página atual
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Inicialização dos estados
if 'orgaos' not in st.session_state:
    st.session_state['orgaos'] = []
if 'temas' not in st.session_state:
    st.session_state['temas'] = []
if 'frequencia' not in st.session_state:
    st.session_state['frequencia'] = None
if 'resultado_pesquisa' not in st.session_state:
    st.session_state['resultado_pesquisa'] = []


# Função para mudar de página
def change_page(page_name):
    st.session_state.current_page = page_name


# Popover para pesquisa de séries estatísticas
st.cache_data(ttl="2h")
with st.sidebar:
    st.title("Filtros")
    with st.expander(label="Filtros de pesquisa", expanded=False, icon=":material/filter_list:"):
        filtrar_por_frequencia = st.checkbox(label="Filtrar por periodicidade")
        frequencia = st.pills(
            label="Selecione a frequência da série",
            options=["Diária", "Mensal", "Trimestral", "Anual", "Decenal"],
            disabled=not filtrar_por_frequencia,
            key="frequencia",
            label_visibility="collapsed",
            default = None
        )
        
        filtrar_por_orgao = st.checkbox(label="Filtrar por órgão responsável")
        orgaos = st.multiselect(
            label="Selecione os órgãos",
            options=ipea.sources(),
            disabled=not filtrar_por_orgao,
            placeholder="Ex.: Bacen, IBGE, IPEA, etc...",
            key="orgaos",
            label_visibility="collapsed",
        )

        filtrar_por_tema = st.checkbox(label="Filtrar por tema")
        df_temas = ipea.themes()
        temas = st.multiselect(
            label="Selecione os temas",
            options=df_temas['ID'],
            disabled=not filtrar_por_tema,
            format_func=lambda x: df_temas.loc[df_temas['ID'] == x, 'NAME'].values[0],
            placeholder="Ex.: Comércio e Vendas, Finanças Públicas, etc...",
            key="temas",
            label_visibility="collapsed",
        )

    # Atualiza o resultado da pesquisa sempre que filtros mudam
    orgaos_selecionados = st.session_state['orgaos'] if filtrar_por_orgao else []
    temas_selecionados = st.session_state['temas'] if filtrar_por_tema else []
    frequencia_selecionada = st.session_state['frequencia'] if filtrar_por_frequencia else []
    st.session_state['resultado_pesquisa'] = search(orgaos_selecionados, temas_selecionados, frequencia_selecionada)
    
    st.markdown("#### Selecione ou pesquise uma série estatística")
    serie_selecionada = st.selectbox(
        label="Selecionar série",
        options=st.session_state['resultado_pesquisa'],
        key="serie_estatistica",
        label_visibility="collapsed",
        placeholder="Selecione ou pesquise uma série estatística...",
        format_func=lambda x: st.session_state['resultado_pesquisa'].loc[st.session_state['resultado_pesquisa']['CODE'] == x, 'NAME'].values[0],
        index=None
    )
    if st.button("Alertas"):
        change_page("Alertas")
    

def main_page():
    # cabeçalho
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(str(img_path), width=80)
    with col2:
        st.markdown("""
        <div class="header-ipea">
            <h3 class="titulo-ipea">Gov Insights - Relatórios inteligentes IPEA</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## ")


    col3, col4 = st.columns([3, 2])
    with col3:
        if serie_selecionada:
            info_serie = ipea.describe(serie_selecionada) # Obtém informações da série estatística selecionada
            percentage = calcular_percentual_aumento_por_periodo(serie_selecionada) # Calcula o percentual de aumento para cada período definido
            # Define o índice do período selecionado com base na session_state['periodo_analise']
            periodos = ['Última semana', 'Último mês', 'Últimos 6 meses', 'Último ano', 'Últimos 3 anos', 'Últimos 5 anos']
            periodo_selecionado = st.session_state.get('periodo_analise', periodos[0])
            try:
                idx = periodos.index(periodo_selecionado)
            except ValueError:
                idx = 0  # fallback para o primeiro período se não encontrado

            color_indicator = "#2BB17A" if percentage[idx] >= 0 else "#f0423c" # Define a cor do indicador com base no percentual
            text_indicator = ("↑ " if percentage[idx] >= 0 else "↓ ") + str(percentage[idx]) + "%"# Define o texto do indicador com base no percentual
            st.html(
                f"""
                <style>
                    .custom-header {{
                        display: flex;
                        flex-direction: row;
                        align-items: baseline;
                        row-gap: 1px;
                        column-gap: 10px;
                        flex-wrap: wrap;
                        max-width: 1000px;
                    }}
                    .custom-header h1 {{
                        font-family: 'Inter Black', sans-serif;
                        font-size: 24px; 
                        font-weight: 900;
                        margin: 0 0 12px 0;
                        line-height: 22px;
                        word-break: break-word;
                        max-width: 1000px;
                        text-align: justify;
                    }}
                    .indicator {{
                        font-family: 'Inter', sans-serif;
                        font-size: 24px;
                        color: {color_indicator};
                        font-weight: 900;
                        margin: -16px 0 0 0;
                    }}
                    .subtitle {{
                        font-family: 'Inter', sans-serif;
                        font-size: 16px;
                        color: #cfcfcf;
                        display: block;
                        line-height: 18px;
                        margin: -8px 0 0 0;
                        max-width: 1000px;
                        text-align: justify;
                    }}
                    .custom-divider {{
                        border: none;
                        border-top: 1px solid #e0e0e0;
                        margin: 18px 0 0 0;
                    }}
                </style>
                <div class="custom-header">
                    <h1>{info_serie.iloc[0,0]}</h1>
                    <span class="indicator">{text_indicator}</span>
                </div>
                <div class="subtitle">
                    <b>{info_serie.iloc[1,0]}</b> · {info_serie.iloc[2,0]} · {info_serie.iloc[4,0]} · {info_serie.iloc[8,0]}
                </div>
                <hr class="custom-divider"/>
                """
            )
            if info_serie.iloc[8,0] == "Diária":
                periodo_selecionado = st.pills(
                    label="Período de análise",
                    options=['Última semana', 'Último mês', 'Últimos 6 meses', 'Último ano', 'Últimos 3 anos', 'Últimos 5 anos'],
                    key="periodo_analise",
                    default=periodos[0],
                )
                st.plotly_chart(
                    plotar_grafico_periodo(serie_selecionada, periodo_selecionado),
                    use_container_width=True,
                )
            else:
                st.markdown('''#### Lógica ainda não implementada para séries com periodicidade diferente de diária.''')

        else:
            st.markdown('''#### Nenhuma série estatística selecionada
                        Por favor, utilize a pesquisa acima para encontrar uma série estatística.
                        ''')
    with col4:
        if serie_selecionada:
            texto_LLM = f"""
                <div class='painel'>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque urna mi, varius nec tincidunt sed.</p>
                <h2 class='valor-indicador'></h2>
                </div>
                """
            st.markdown(texto_LLM, unsafe_allow_html=True)
        else:
            st.markdown(''' #### Selecione uma série para gerar o relatório''')
    if serie_selecionada:
        if st.button("Exportar Relatório"):
            change_page("exportacao")

if st.session_state.current_page == "Dashboard":
    main_page()