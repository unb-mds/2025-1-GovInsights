# --- 1. Importações de bibliotecas básicas ---
import streamlit as st
from pathlib import Path
import sys
import os

# --- 2. Definições de caminhos e configurações que NÃO usam st. ---
# Correção de diretórios (esta parte NÃO DEVE ter st.comandos)
current_dir = Path(__file__).parent
img_path = current_dir / "assets" / "img" / "Icon.png"

# Adiciona diretório pai ao PATH do sistema para importações de serviços
# Esta linha DEVE vir antes das importações de seus serviços se eles estiverem em diretórios "superiores"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# --- 3. Configuração da página Streamlit (DEVE SER O PRIMEIRO st.comando) ---
st.set_page_config(
    page_title="GovInsights",
    layout="wide",
    page_icon=str(img_path)
)

# --- 4. Carregamento de CSS (AGORA PODE USAR st.markdown) ---
css_path = current_dir / "assets" / "stylesheets" / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("Arquivo CSS não encontrado em: " + str(css_path))

# --- 5. Importações de módulos e funções do Back-end/Outros módulos (APÓS st.set_page_config) ---
# Importação de tela de alerta
from alertas import alertas_page

# Importação de funções do backEnd
from services.search import SearchService
from services.graph import timeSeries
from services.ia import gerar_relatorio
from services.pdf import gerar_pdf

# --- 6. Inicialização dos estados da sessão ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

if 'orgaos' not in st.session_state:
    st.session_state['orgaos'] = []
if 'temas' not in st.session_state:
    st.session_state['temas'] = []
if 'frequencia' not in st.session_state:
    st.session_state['frequencia'] = "Diária"  # Frequência padrão
if 'resultado_pesquisa' not in st.session_state:
    st.session_state['resultado_pesquisa'] = []
if 'search_service' not in st.session_state:
    st.session_state['search_service'] = SearchService()
    
pesquisa = st.session_state['search_service']

# --- 7. Funções Auxiliares ---
def change_page(page_name):
    st.session_state.current_page = page_name

@st.cache_data(ttl="2h") # Cache para a função de obter a série
def obter_obj_serie(serie_selecionada: str, frequencia: str):
    # A lógica de cache para 'serie_obj' e 'last_serie_selecionada' foi movida para main_page
    return timeSeries(serie_selecionada, frequencia)

def criar_pills_periodo_analise(frequencia):
    freq_options = {
        "Diária": ['Última semana', 'Último mês', 'Últimos 6 meses', 'Último ano', 'Últimos 3 anos', 'Últimos 5 anos'],
        "Mensal": ['Últimos 6 meses', 'Último ano', 'Últimos 2 anos', 'Últimos 3 anos', 'Últimos 5 anos', 'Últimos 10 anos'],
        "Trimestral": ['Últimos 6 meses', 'Último ano', 'Últimos 2 anos', 'Últimos 3 anos', 'Últimos 5 anos', 'Últimos 10 anos'],
        "Anual": ['Últimos 5 anos', 'Últimos 10 anos', 'Últimos 20 anos']
    }
    options_to_use = freq_options.get(frequencia, [])
    st.pills(
        label="Período de análise",
        options=options_to_use,
        key="periodo_analise",
        default=options_to_use[0] if options_to_use else None,
    )

# --- 8. Sidebar de Navegação e Filtros ---
# Não use st.cache_data diretamente em um 'with st.sidebar', o cache deve ser em funções
with st.sidebar:
    st.title("Filtros")
    with st.expander(label="Filtros de pesquisa", expanded=False):
        st.pills(
            label="Selecione a frequência da série",
            options=["Diária", "Mensal", "Trimestral", "Anual"],
            key="frequencia",
            default=st.session_state.get('frequencia')
        )

        filtrar_por_orgao = st.checkbox(label="Filtrar por órgão responsável")
        orgaos = st.multiselect(
            label="Selecione os órgãos",
            options=pesquisa.get_available_sources(st.session_state['frequencia']),
            disabled=not filtrar_por_orgao,
            placeholder="Ex.: Bacen, IBGE, IPEA, etc...",
            key="orgaos",
            label_visibility="collapsed",
        )

        filtrar_por_tema = st.checkbox(label="Filtrar por tema")
        temas = st.multiselect(
            label="Selecione os temas",
            options=pesquisa.get_available_themes(st.session_state['frequencia']),
            disabled=not filtrar_por_tema,
            format_func=lambda x: x['THEME NAME'],
            placeholder="Ex.: Comércio e Vendas, Finanças Públicas, etc...",
            key="temas",
            label_visibility="collapsed",
        )

    # Atualiza o resultado da pesquisa sempre que filtros mudam
    orgaos_selecionados = st.session_state['orgaos'] if filtrar_por_orgao else []
    temas_selecionados = st.session_state['temas'] if filtrar_por_tema else []

    st.session_state['resultado_pesquisa'] = pesquisa.search(
        frequency=st.session_state['frequencia'],
        fonte_list=orgaos_selecionados,
        tema_list=temas_selecionados
    )
    
    # Exibe o número de séries encontradas
    if st.session_state['resultado_pesquisa']:
        placeholder_selectbox = f"{len(st.session_state['resultado_pesquisa'])} séries estatísticas encontradas."
    else:
        placeholder_selectbox = "Nenhuma série estatística encontrada."

    st.markdown("#### Selecione ou pesquise uma série estatística")
    serie_selecionada = st.selectbox(
        label="Selecionar série",
        options=st.session_state['resultado_pesquisa'],
        key="serie_estatistica",
        label_visibility="collapsed",
        placeholder=placeholder_selectbox,
        format_func=lambda x: f"{x['NAME']} ({x['CODE']})",
        index=None
    )

    # Botões de navegação (chaves renomeadas para evitar conflitos)
    if st.button("Alertas", key="btn_alertas_sidebar"):
        change_page("Alertas")

    if st.button("Dashboard", key="btn_dashboard_sidebar"):
        change_page("Dashboard")



# --- 9. Definição da Página Principal (main_page) ---
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
        local_serie_selecionada = None
        if serie_selecionada:
            local_serie_selecionada = st.session_state.get('serie_estatistica')['CODE']
            if 'serie_obj' not in st.session_state or st.session_state.get('last_serie_selecionada') != local_serie_selecionada:
                st.session_state['serie_obj'] = obter_obj_serie(local_serie_selecionada, st.session_state['frequencia'])
                st.session_state['last_serie_selecionada'] = local_serie_selecionada
            serie = st.session_state['serie_obj']

            info_serie = serie.descricao
            criar_pills_periodo_analise(st.session_state['frequencia'])

            periodo_atual = st.session_state.get('periodo_analise')
            if periodo_atual and periodo_atual in serie.percentuais and serie.percentuais[periodo_atual] is not None:
                color_indicator = "#2BB17A" if serie.percentuais[periodo_atual] >= 0 else "#f0423c"
                text_indicator = ("↑ " if serie.percentuais[periodo_atual] >= 0 else "↓ ") + str(serie.percentuais[periodo_atual]) + "%"
            else:
                color_indicator = "#CCCCCC"
                text_indicator = "N/A"

            st.html(
                f"""
                <div style="display: flex; flex-direction: row; align-items: baseline; row-gap: 1px; column-gap: 10px; flex-wrap: wrap; max-width: 1000px;">
                    <h1 style="font-size: 24px; font-weight: 900; margin: 0 0 12px 0; line-height: 22px; word-break: break-word; max-width: 1000px; text-align: justify; letter-spacing: 0.8px;">
                        {info_serie.iloc[0,0] if not info_serie.empty else 'Informação não disponível'}
                    </h1>
                    <span style="font-size: 24px; color: {color_indicator}; font-weight: 900; margin: -16px 0 0 0; letter-spacing: 0.5px;">
                        {text_indicator}
                    </span>
                </div>
                <div style="font-size: 16px; color: #cfcfcf; display: block; line-height: 18px; margin: -8px 0 0 0; max-width: 1000px; text-align: justify; letter-spacing: 0.4px;">
                    <b>{info_serie.iloc[1,0] if not info_serie.empty else 'Órgão não disponível'}</b> · {info_serie.iloc[2,0] if not info_serie.empty else 'Tema não disponível'} · {info_serie.iloc[4,0] if not info_serie.empty else 'Unidade não disponível'} · {info_serie.iloc[8,0] if not info_serie.empty else 'Fonte não disponível'}
                </div>
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 18px 0 0 0;"/>
                """
            )
            if periodo_atual and periodo_atual in serie.graficos:
                st.plotly_chart(
                    serie.graficos[periodo_atual],
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
        pdf_bytes = None
        if local_serie_selecionada:
            if st.button("Gerar Relatório Inteligente", key="btn_relatorio_ia"):
                try:
                    if 'serie_obj' not in st.session_state or st.session_state.get('last_serie_selecionada') != local_serie_selecionada:
                        st.session_state['serie_obj'] = obter_obj_serie(local_serie_selecionada, st.session_state['frequencia'])
                        st.session_state['last_serie_selecionada'] = local_serie_selecionada
                    serie = st.session_state['serie_obj']

                    periodo_analise_ia = st.session_state.get('periodo_analise')
                    dfSerie = serie.dados_periodos.get(periodo_analise_ia)

                    if dfSerie is None or dfSerie.empty:
                        st.error("Nenhum dado encontrado para a série ou período informado para análise de IA.")
                    else:
                        st.subheader("Análise inteligente")
                        with st.spinner("Gerando análise..."):
                            response = gerar_relatorio(local_serie_selecionada, dfSerie)

                        if response:
                            with open(gerar_pdf(codSerie=local_serie_selecionada, dfSerie=dfSerie, iaText=response), "rb") as file:
                                pdf_bytes = file.read()

                    with st.container(height=600):
                        if response:
                            st.markdown(response)
                        elif local_serie_selecionada and (dfSerie is None or dfSerie.empty):
                            st.info("Não foi possível gerar a análise de IA. Verifique os dados da série ou o período selecionado.")
                        elif local_serie_selecionada:
                            st.warning("Análise de IA não gerada. Verifique as configurações da API ou os dados.")
                except Exception as e:
                    st.error(f"Erro na análise de IA: {e}")
        else:
            st.markdown('''#### ''')

    if pdf_bytes:
        st.download_button(
            label="Exportar Relatório",
            data=pdf_bytes,
            file_name="relatorio.pdf",
            mime="application/pdf"
        )

# --- 10. Controle de Páginas (Último bloco no script principal) ---
if st.session_state.current_page == "Dashboard":
    main_page()
    
elif st.session_state.current_page == "Alertas":
    st.markdown("""
    <script>
        const body = window.parent.document.querySelector('body');
        body.classList.add('sidebar-hidden');
    </script>
""", unsafe_allow_html=True)
    css_path = current_dir / "assets" / "stylesheets" / "style2.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Arquivo CSS não encontrado em: " + str(css_path))
    alertas_page()
