# importação de dependências
import streamlit as st
import ipeadatapy as ipea
import plotly.graph_objects as go
from pathlib import Path
import sys
import os

# --- Configuração de Caminhos e Ambiente (Antes de qualquer st.command) ---
# correção de diretorios
current_dir = Path(__file__).parent

# Caminho para o ícone da página
img_path = current_dir / "assets" / "img" / "Icon.png"

# Adiciona diretório pai ao PATH do sistema para importações de serviços
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# --- Configuração da Página do Streamlit (PRIMEIRO COMANDO st.) ---
st.set_page_config(
    page_title="GovInsights",
    layout="wide",
    page_icon=str(img_path) # Converte o Path para string para page_icon
)

# --- Carregamento e Aplicação do CSS (Depois de st.set_page_config) ---
css_path = current_dir / "assets" / "stylesheets" / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("Arquivo CSS não encontrado em: " + str(css_path))

# --- Importação de funções e telas do Back-end/Outros módulos (Depois de st.set_page_config e setup inicial) ---
# Importação de tela de alerta
from alertas import alertas_page

# importação de funções do backEnd
from services.search import search
from services.graph import timeSeries
from services.ia import gerar_relatorio
from services.pdf import gerar_pdf


# --- Inicialização dos Estados da Sessão ---
# Estado da sessão para controlar a página atual
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Inicialização dos estados dos filtros e resultados
if 'orgaos' not in st.session_state:
    st.session_state['orgaos'] = []
if 'temas' not in st.session_state:
    st.session_state['temas'] = []
if 'frequencia' not in st.session_state:
    st.session_state['frequencia'] = None
if 'resultado_pesquisa' not in st.session_state:
    st.session_state['resultado_pesquisa'] = []


# --- Funções Auxiliares ---
def change_page(page_name):
    st.session_state.current_page = page_name

@st.cache_data(ttl="2h")
def obter_obj_serie(serie_selecionada: str, frequencia: str):
    # A lógica de cache já está sendo gerenciada fora desta função
    # st.session_state['serie_obj'] e 'last_serie_selecionada'
    # precisam ser gerenciadas no chamador se for para usar st.cache_data
    # Recomendo passar st.cache_data para a função timeSeries, se apropriado,
    # ou gerenciar o cache da série fora desta função.
    # Por simplicidade, vou manter a lógica original que parecia estar no main_page
    return timeSeries(serie_selecionada, frequencia)


def criar_pills_periodo_analise(frequencia):
    freq_options = {
        "Diária": ['Última semana', 'Último mês', 'Últimos 6 meses', 'Último ano', 'Últimos 3 anos', 'Últimos 5 anos'],
        "Mensal": ['Últimos 6 meses', 'Último ano', 'Últimos 2 anos', 'Últimos 3 anos', 'Últimos 5 anos', 'Últimos 10 anos'],
        "Trimestral": ['Últimos 6 meses', 'Último ano', 'Últimos 2 anos', 'Últimos 3 anos', 'Últimos 5 anos', 'Últimos 10 anos'],
        "Anual": ['Últimos 5 anos', 'Últimos 10 anos', 'Últimos 20 anos']
    }
    st.pills(
        label="Período de análise",
        options=freq_options.get(frequencia),
        key="periodo_analise",
        default=freq_options.get(frequencia)[0], # Define um padrão para evitar erro se nenhum for selecionado
    )


# --- Sidebar de Navegação e Filtros ---
with st.sidebar:
    st.title("Filtros")
    with st.expander(label="Filtros de pesquisa", expanded=False):
        filtrar_por_frequencia = st.checkbox(label="Filtrar por periodicidade")
        frequencia = st.pills(
            label="Selecione a frequência da série",
            options=["Diária", "Mensal", "Trimestral", "Anual"],
            disabled=not filtrar_por_frequencia,
            key="frequencia",
            label_visibility="collapsed",
            default=None
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
    # Correção: `frequencia_selecionada` deve ser uma string ou None, não uma lista.
    # Se 'frequencia' é None, use uma string vazia ou None para a função search
    frequencia_selecionada = st.session_state['frequencia'] if filtrar_por_frequencia and st.session_state['frequencia'] else None

    # st.cache_data pode ser aplicado aqui para 'search'
    # @st.cache_data(ttl="2h")
    # def cached_search(orgaos, temas, frequencia):
    #    return search(orgaos, temas, frequencia)
    # st.session_state['resultado_pesquisa'] = cached_search(orgaos_selecionados, temas_selecionados, frequencia_selecionada)
    # Mantendo a lógica original para evitar quebras
    st.session_state['resultado_pesquisa'] = search(orgaos_selecionados, temas_selecionados, frequencia_selecionada)


    st.markdown("#### Selecione ou pesquise uma série estatística")
    # Tratamento para quando resultado_pesquisa é um DataFrame e selectbox espera lista de strings
    # ou para evitar KeyError se 'CODE' não existir
    if not st.session_state['resultado_pesquisa'].empty:
        options_codes = st.session_state['resultado_pesquisa']['CODE'].tolist()
        options_names = st.session_state['resultado_pesquisa']['NAME'].tolist()
        # Mapeia código para nome para o format_func
        code_to_name_map = dict(zip(options_codes, options_names))

        serie_selecionada = st.selectbox(
            label="Selecionar série",
            options=options_codes, # Passa apenas os códigos
            key="serie_estatistica",
            label_visibility="collapsed",
            placeholder="Selecione ou pesquise uma série estatística...",
            format_func=lambda x: code_to_name_map.get(x, x), # Usa o mapa
            index=None
        )
    else:
        serie_selecionada = st.selectbox(
            label="Selecionar série",
            options=[],
            key="serie_estatistica",
            label_visibility="collapsed",
            placeholder="Nenhum resultado para os filtros selecionados.",
            index=None
        )


    # Botões de navegação
    # Usar key para cada botão para evitar conflitos de widget
    if st.button("Alertas", key="btn_alertas"):
        change_page("Alertas")

    if st.button("Dashboard", key="btn_dashboard"):
        change_page("Dashboard")

    if st.button("Home", key="btn_home"): # Geralmente "Home" e "Dashboard" são a mesma coisa aqui
        change_page("Dashboard")


# --- Páginas da Aplicação ---
def main_page():
    # cabeçalho
    col1, col2 = st.columns([1, 14])
    with col1:
        st.image(str(img_path), width=80)
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: left; height: 100%; justify-content: flex-start;">
            <h3 style="margin-left: 10px;">
                Gov Insights <br>
                <p>Relatórios inteligentes IPEA</p>
            </h3>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns([4, 2])
    with col3:
        if serie_selecionada:
            # Gerenciamento de cache para serie_obj
            if 'serie_obj' not in st.session_state or st.session_state.get('last_serie_selecionada') != serie_selecionada:
                st.session_state['serie_obj'] = obter_obj_serie(serie_selecionada, st.session_state['frequencia'])
                st.session_state['last_serie_selecionada'] = serie_selecionada
            serie = st.session_state['serie_obj']

            info_serie = serie.descricao
            criar_pills_periodo_analise(st.session_state['frequencia'])

            # Verificação para 'periodo_analise' para evitar erro se não houver seleção padrão
            periodo_atual = st.session_state.get('periodo_analise')
            if periodo_atual and periodo_atual in serie.percentuais:
                color_indicator = "#2BB17A" if serie.percentuais[periodo_atual] >= 0 else "#f0423c"
                text_indicator = ("↑ " if serie.percentuais[periodo_atual] >= 0 else "↓ ") + str(serie.percentuais[periodo_atual]) + "%"
            else:
                color_indicator = "#CCCCCC"
                text_indicator = "N/A"

            st.html(
                f"""
                <div style="display: flex; flex-direction: row; align-items: baseline; row-gap: 1px; column-gap: 10px; flex-wrap: wrap; max-width: 1000px;">
                    <h1 style="font-size: 24px; font-weight: 900; margin: 0 0 12px 0; line-height: 22px; word-break: break-word; max-width: 1000px; text-align: justify; letter-spacing: 0.8px;">
                        {info_serie.iloc[0,0]}
                    </h1>
                    <span style="font-size: 24px; color: {color_indicator}; font-weight: 900; margin: -16px 0 0 0; letter-spacing: 0.5px;">
                        {text_indicator}
                    </span>
                </div>
                <div style="font-size: 16px; color: #cfcfcf; display: block; line-height: 18px; margin: -8px 0 0 0; max-width: 1000px; text-align: justify; letter-spacing: 0.4px;">
                    <b>{info_serie.iloc[1,0]}</b> · {info_serie.iloc[2,0]} · {info_serie.iloc[4,0]} · {info_serie.iloc[8,0]}
                </div>
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 18px 0 0 0;"/>
                """
            )
            if periodo_atual and periodo_atual in serie.graficos:
                st.plotly_chart(
                    serie.graficos[periodo_atual], # Use o periodo_atual do state
                    use_container_width=True,
                )
            else:
                st.warning("Gráfico não disponível para o período selecionado ou dados insuficientes.")
        else:
            st.markdown("""
                <div class="painel" style="border: 1px solid #2BB17A; background-color: #101120; padding: 16px; border-radius: 8px;">
                    <h4 style="color: white; margin-bottom: 8px;">Selecione uma série para gerar o relatório</h4>
                    <h4 style="color: white; margin-bottom: 8px;">Nenhuma série estatística selecionada</h4>
                    <p style="color: #b0b0b0; font-size: 14px;">
                        Por favor, utilize os filtros da barra lateral para encontrar uma série estatística.
                    </p>
                </div>
            """, unsafe_allow_html=True)
    with col4:
        response = None
        pdf_bytes = None # Inicializa pdf_bytes
        if serie_selecionada:
            try:
                # Garante que serie_obj existe antes de tentar acessá-lo
                if 'serie_obj' not in st.session_state or st.session_state.get('last_serie_selecionada') != serie_selecionada:
                    st.session_state['serie_obj'] = obter_obj_serie(serie_selecionada, st.session_state['frequencia'])
                    st.session_state['last_serie_selecionada'] = serie_selecionada
                serie = st.session_state['serie_obj']

                dfSerie = serie.dados_periodos.get(st.session_state.get('periodo_analise')) # Use .get para segurança
                if dfSerie is None or dfSerie.empty:
                    st.error("Nenhum dado encontrado para a série ou período informado.")
                else:
                    st.subheader("Dados da série")
                    with st.spinner("Gerando análise..."):
                        response = gerar_relatorio(serie_selecionada, dfSerie)

                    # Garante que response não é None antes de gerar PDF
                    if response:
                        with open(gerar_pdf(codSerie=serie_selecionada, dfSerie=dfSerie, iaText=response), "rb") as file:
                            pdf_bytes = file.read()

                with st.container(height=600):
                    if response:
                        st.markdown(response)
                    elif not dfSerie.empty: # Mostra mensagem de erro apenas se dados existirem, mas IA falhou
                        st.warning("Análise de IA não gerada. Verifique as configurações da API ou os dados.")

            except Exception as e:
                st.error(f"Erro ao buscar série para análise: {e}")
        else:
            st.markdown('''#### ''') #MUDANÇA AQUI!

    # Botão de download de PDF fora do try/except para ser sempre visível se pdf_bytes existir
    if pdf_bytes: # Verifica se pdf_bytes foi gerado com sucesso
        st.download_button(
            label="Exportar Relatório",
            data=pdf_bytes,
            file_name="relatorio.pdf",
            mime="application/pdf"
        )


# --- Controle de Páginas ---
if st.session_state.current_page == "Dashboard":
    main_page()
elif st.session_state.current_page == "Alertas":
    alertas_page()
