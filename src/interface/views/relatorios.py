import streamlit as st
import pandas as pd # Adicionado para manipulação de dados
import requests # Adicionado para buscar dados do IPEA
import io # Adicionado para leitura de arquivos de upload

# Importa a função de geração de relatório do novo arquivo
from mistral_report_generator import generate_intelligent_report

# --- Funções para Carregar Dados do IPEA (copiadas do app.py original) ---
# É importante que essas funções estejam disponíveis onde a página de relatórios precisa delas
@st.cache_data
def carregar_metadados_ipea():
    url = "http://www.ipeadata.gov.br/api/odata4/Metadados"
    try:
        response = requests.get(url)
        dados = response.json()["value"]
        return pd.DataFrame(dados)
    except Exception as e:
        st.error(f"Não foi possível carregar metadados do IPEA: {e}. Verifique sua conexão.")
        return pd.DataFrame()

def get_dados_ipea_relatorio(codigo_serie):
    url = f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{codigo_serie}')"
    try:
        response = requests.get(url)
        response.raise_for_status() # Lança um erro para respostas HTTP ruins (4xx ou 5xx)
        dados = response.json()["value"]
        df = pd.DataFrame(dados)
        df = df.rename(columns={"VALDATA": "Data", "VALVALOR": "Valor"})
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados da série {codigo_serie} do IPEA: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar dados da série {codigo_serie}: {e}")
        return pd.DataFrame()

# --- Página de Relatórios ---
def relatorios_page():
    # Header existente
    st.markdown("""
    <div class="header-ipea">
        <h3 class="titulo-ipea">Relatórios inteligentes IPEA</h3>
        <a href="#" class="login-icon"><i class="fas fa-user-circle"></i></a>
    </div>
    """, unsafe_allow_html=True)

    # Título para a seção de exportação (existente)
    st.markdown("<h2 class='titulo-secao'><i class='fas fa-file-export'></i> Exportar relatórios</h2>", unsafe_allow_html=True)

    # Seu código existente para Período e Tipos de Dados...
    st.markdown("""
    <div class="secao">
        <label class="label">Período</label>
        <div class="filtros-periodo">
            <select class="custom-select" id="periodo-inicio">
                <option>Maio 2023</option>
                <option>Junho 2023</option>
                <option>Julho 2023</option>
            </select>
            <span class="ate">até</span>
            <select class="custom-select" id="periodo-fim">
                <option>Maio 2023</option>
                <option>Junho 2023</option>
                <option>Julho 2023</option>
            </select>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="secao">
        <label class="label">Tipos de dados</label>
        <div class="checkbox-container">
            <label class="checkbox-item">
                <input type="checkbox" name="tipo_dado" value="receitas"> Receitas
            </label>
            <label class="checkbox-item">
                <input type="checkbox" name="tipo_dado" value="despesas"> Despesas
            </label>
            <label class="checkbox-item">
                <input type="checkbox" name="tipo_dado" value="alertas"> Alertas
            </label>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Nova Seção: Geração de Relatório Inteligente com Mistral 7B ---
    st.markdown("---") # Separador visual
    st.markdown("<h2 class='titulo-secao'><i class='fas fa-robot'></i> Gerar Relatório Inteligente com IA</h2>", unsafe_allow_html=True)
    st.markdown("""
        Utilize o modelo Mistral 7B para gerar um relatório inteligente a partir de uma série de dados do IPEA
        ou de um arquivo enviado por você.
    """)

    # Opção de Entrada de Dados para o Mistral
    data_source = st.radio(
        "Escolha a fonte dos dados para o relatório inteligente:",
        ("Série do IPEA", "Upload de Arquivo (CSV/TXT)"),
        key="mistral_data_source" # Chave única para evitar conflitos com outros radios
    )

    series_data_text = ""
    series_name_for_report = ""

    if data_source == "Série do IPEA":
        # Componentes de busca e seleção de série do IPEA para o relatório inteligente
        metadados = carregar_metadados_ipea()
        if not metadados.empty:
            termo_busca_ia = st.text_input("🔍 Busque uma série IPEA por nome ou código para IA:", placeholder="Ex: PIB, IPCA", key="search_ia")

            if termo_busca_ia:
                filtro_series_ia = metadados[
                    metadados["SERNOME"].str.lower().str.contains(termo_busca_ia.lower()) |
                    metadados["SERCODIGO"].str.lower().str.contains(termo_busca_ia.lower())
                ].head(10)

                if not filtro_series_ia.empty:
                    options_dict_ia = {f"{row['SERNOME']} ({row['SERCODIGO']})": row['SERCODIGO'] for index, row in filtro_series_ia.iterrows()}
                    selected_option_ia = st.selectbox(
                        "Selecione uma série para análise de IA:",
                        options=list(options_dict_ia.keys()),
                        key="select_series_ia"
                    )

                    if selected_option_ia:
                        codigo_serie_selecionada_ia = options_dict_ia[selected_option_ia]
                        series_name_for_report = selected_option_ia

                        df_ipea_ia = get_dados_ipea_relatorio(codigo_serie_selecionada_ia)
                        if not df_ipea_ia.empty:
                            df_ipea_ia["Data"] = pd.to_datetime(df_ipea_ia["Data"], utc=True, errors="coerce")
                            df_ipea_ia = df_ipea_ia.dropna(subset=["Data", "Valor"])
                            df_ipea_ia = df_ipea_ia.sort_values("Data")
                            series_data_text = df_ipea_ia.to_csv(index=False)

                            st.success(f"Série selecionada para IA: **{series_name_for_report}**. Dados prontos para análise.")
                            with st.expander("Ver dados brutos (para IA)"):
                                st.text(series_data_text)
                        else:
                            st.warning("Não foi possível carregar os dados para a série IPEA selecionada.")
                    else:
                        st.info("Digite um termo de busca e selecione uma série para a IA.")
                else:
                    st.info("Nenhuma série IPEA encontrada com o termo de busca para IA.")
            else:
                st.info("Digite um termo para buscar séries do IPEA para o relatório inteligente.")
        else:
            st.warning("Não foi possível carregar os metadados do IPEA. Verifique sua conexão.")

    else: # Upload de Arquivo para o Mistral
        uploaded_file_ia = st.file_uploader("Faça upload do seu arquivo CSV ou TXT para a IA:", type=["csv", "txt"], key="upload_ia")
        if uploaded_file_ia is not None:
            series_name_for_report = uploaded_file_ia.name
            try:
                series_data_text = io.StringIO(uploaded_file_ia.getvalue().decode("utf-8")).read()
                st.success(f"Arquivo '{uploaded_file_ia.name}' carregado com sucesso para IA!")
                with st.expander("Ver conteúdo do arquivo (para IA)"):
                    st.text(series_data_text)
            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}. Certifique-se de que é um CSV/TXT válido.")
                series_data_text = ""
        else:
            st.info("Nenhum arquivo carregado para a IA.")

    # Prompt Adicional para o Mistral 7B
    user_additional_prompt = st.text_area(
        "Adicione um prompt extra para guiar o relatório inteligente (opcional):",
        placeholder="Ex: 'Foque nas tendências de crescimento e possíveis causas.'",
        height=100,
        key="ai_prompt"
    )

    # Botão para Gerar o Relatório Inteligente
    if st.button("Gerar Relatório Inteligente com Mistral 7B", key="generate_ai_report"):
        if series_data_text:
            report_output = generate_intelligent_report(series_name_for_report, series_data_text, user_additional_prompt)
            st.subheader("📊 Relatório Gerado pelo Mistral 7B:")
            st.markdown(report_output) # Renderiza o Markdown do relatório
        else:
            st.warning("Por favor, selecione ou carregue os dados da série para gerar o relatório inteligente.")

    # --- Seção: Visualização prévia (existente) ---
    st.markdown("---") # Separador visual
    st.markdown("""
    <div class="secao">
        <label class="label">Visualização prévia</label>
        <select class="custom-select">
            <option>PDF</option>
            <option>Excel</option>
            <option>HTML</option>
        </select>
    </div>
    """, unsafe_allow_html=True)

    # Botão exportar (existente)
    st.markdown("""
    <div class="botao-container">
        <button class="btn-exportar">
            Exportar Relatório <span class="seta-baixo">↓</span>
        </button>
    </div>
    """, unsafe_allow_html=True)