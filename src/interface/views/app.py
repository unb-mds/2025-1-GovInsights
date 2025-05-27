import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
import pathlib
import requests
import plotly.graph_objects as go
from alertas import alertas_page
from configuracoes import configuracoes_page
from relatorios import relatorios_page
from analises import analises_page
from dados import dados_page
from user import user_page


# Configuração da página
st.set_page_config(
    page_title="IPEA",
    layout="wide",
    page_icon="📊"
)

# Estilo CSS
with open("./src/interface/views/styles/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Estado da sessão para controlar a página atual
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Função para mudar de página
def change_page(page_name):
    st.session_state.current_page = page_name

# Sidebar
with st.sidebar:
    st.title("IPEA")
    st.text_input("🔍 Search for...")
    st.markdown("### Navegação")
    
    # Botões de navegação
    if st.button("Dashboard"):
        change_page("Dashboard")
    if st.button("Relatórios"):
        change_page("Relatórios")
    if st.button("Alertas"):
        change_page("Alertas")
    if st.button("Análises inteligentes"):
        change_page("Análises inteligentes")
    if st.button("Dados"):
        change_page("Dados")
    
    st.markdown("---")
    if st.button("User"):
        change_page("User")
    if st.button("Configurações"):
        change_page("Configurações")

# Funções simuladas
def get_total_receitas(): return 50800, 28.4
def get_total_despesas(): return 23600, -12.6
def get_alertas_ativos(): return 3, 3.1


def get_dados_ipea(codigo_serie):
    url = f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{codigo_serie}')"
    response = requests.get(url)
    dados = response.json()["value"]
    df = pd.DataFrame(dados)
    df = df.rename(columns={"VALDATA": "Data", "VALVALOR": "Valor"})
    return df

@st.cache_data
def carregar_metadados():
    url = "http://www.ipeadata.gov.br/api/odata4/Metadados"
    response = requests.get(url)
    dados = response.json()["value"]
    return pd.DataFrame(dados)

def get_valor_indicador(): return 23648
def get_gauge_value(): return 65

# Página principal
def main_page():
    # Cabeçalho
    st.markdown("""
    <div class="header-ipea">
        <h3 class="titulo-ipea">Relatórios inteligentes IPEA</h3>
    </div>
    """, unsafe_allow_html=True)

    # Métricas principais
    col1, col2, col3 = st.columns(3)
    receitas, receitas_var = get_total_receitas()
    despesas, despesas_var = get_total_despesas()
    alertas, alertas_var = get_alertas_ativos()

    # Card 1
    with col1:
        st.markdown(f"""
        <div class="card-metrica">
            <div class="card-topo"><span class="icon">👤</span><span class="titulo">Total de receitas</span></div>
            <div class="valor">{receitas:,}K</div>
            <div class="variacao {'positivo' if receitas_var >= 0 else 'negativo'}">{'▲' if receitas_var >= 0 else '▼'} {abs(receitas_var):.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 2
    with col2:
        st.markdown(f"""
        <div class="card-metrica">
            <div class="card-topo"><span class="icon">👁️</span><span class="titulo">Total de Despesas</span></div>
            <div class="valor">{despesas:,}K</div>
            <div class="variacao {'positivo' if despesas_var >= 0 else 'negativo'}">{'▲' if despesas_var >= 0 else '▼'} {abs(despesas_var):.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 3
    with col3:
        st.markdown(f"""
        <div class="card-metrica">
            <div class="card-topo"><span class="icon">➕</span><span class="titulo">Alertas Ativos</span></div>
            <div class="valor">{alertas}</div>
            <div class="variacao {'positivo' if alertas_var >= 0 else 'negativo'}">{'▲' if alertas_var >= 0 else '▼'} {abs(alertas_var):.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## ")

    # Gráfico e Indicadores
    col4, col5 = st.columns([3, 2])



    metadados = carregar_metadados()

    with col5:
        termo_busca = st.text_input("🔍 Busque uma série por nome, tema ou palavra-chave", placeholder="Ex: setor público consolidado")

    # Filtra as séries que contêm o termo digitado
    filtro = metadados[metadados["SERNOME"].str.lower().str.contains(termo_busca.lower())] if termo_busca else pd.DataFrame()

 
    if not filtro.empty:
        nome_serie = filtro.iloc[0]["SERNOME"]
        codigo_serie = filtro.iloc[0]["SERCODIGO"]
        st.success(f"Série selecionada: **{nome_serie}**")
        

        df = get_dados_ipea(codigo_serie)


        df["Data"] = pd.to_datetime(df["Data"], utc=True, errors="coerce")
        df = df.dropna(subset=["Data", "Valor"])
        df = df.sort_values("Data")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Data"], y=df["Valor"], name=nome_serie, line=dict(color="#00CFFF")))
        fig.update_layout(
            title=nome_serie,
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        col4.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Digite uma palavra-chave para encontrar uma série e visualizar o gráfico.")





# Outras páginas 


# Renderização condicional da página
if st.session_state.current_page == "Dashboard":
    main_page()
    
elif st.session_state.current_page == "Relatórios":
    relatorios_page()
elif st.session_state.current_page == "Alertas":
    alertas_page()
elif st.session_state.current_page == "Análises inteligentes":
    analises_page()
elif st.session_state.current_page == "Dados":
    dados_page()
elif st.session_state.current_page == "User":
    user_page()
elif st.session_state.current_page == "Configurações":
    configuracoes_page()