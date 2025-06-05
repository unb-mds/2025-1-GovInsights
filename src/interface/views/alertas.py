import streamlit as st
import pandas as pd
import os

def carregar_css():
    caminho_css = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'assets', 'stylealertas.css')
    )
    if os.path.exists(caminho_css):
        with open(caminho_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error(f"Arquivo CSS não encontrado em: {caminho_css}")

carregar_css()

fontes_fake = ["IBGE", "IPEA", "Bacen", "Receita Federal"]
temas_fake = [
    {"ID": 1, "NAME": "Comércio e Vendas"},
    {"ID": 2, "NAME": "Finanças Públicas"},
    {"ID": 3, "NAME": "Educação"},
    {"ID": 4, "NAME": "Saúde"},
]
df_temas = pd.DataFrame(temas_fake)

séries_fake = pd.DataFrame([
    {"CODE": "S001", "NAME": "Inflação Mensal", "FREQ": "Mensal", "ORG": "IBGE", "TEMA": 1},
    {"CODE": "S002", "NAME": "Taxa de Juros", "FREQ": "Anual", "ORG": "Bacen", "TEMA": 2},
    {"CODE": "S003", "NAME": "Gastos em Educação", "FREQ": "Trimestral", "ORG": "IPEA", "TEMA": 3},
    {"CODE": "S004", "NAME": "Leitos por Estado", "FREQ": "Anual", "ORG": "Ministério da Saúde", "TEMA": 4},
])

def search(orgaos, temas, frequencias):
    df = séries_fake.copy()
    if orgaos:
        df = df[df["ORG"].isin(orgaos)]
    if temas:
        df = df[df["TEMA"].isin(temas)]
    if frequencias:
        df = df[df["FREQ"].isin(frequencias)]
    return df

st.title("Alertas")

email = st.text_input("Digite seu e-mail para receber alertas")

porcentagem = st.slider("Porcentagem de variação para alerta", min_value=0, max_value=100, value=10, step=1)

st.markdown("## Filtros de pesquisa")

filtrar_por_frequencia = st.checkbox("Filtrar por periodicidade")
frequencia = st.multiselect(
    "Selecione a frequência",
    ["Diária", "Mensal", "Trimestral", "Anual", "Decenal"],
    disabled=not filtrar_por_frequencia
)

filtrar_por_orgao = st.checkbox("Filtrar por órgão responsável")
orgaos = st.multiselect(
    "Selecione os órgãos",
    fontes_fake,
    disabled=not filtrar_por_orgao
)

filtrar_por_tema = st.checkbox("Filtrar por tema")
temas = st.multiselect(
    "Selecione os temas",
    df_temas["ID"],
    disabled=not filtrar_por_tema,
    format_func=lambda x: df_temas.loc[df_temas["ID"] == x, "NAME"].values[0]
)

orgaos_selecionados = orgaos if filtrar_por_orgao else []
temas_selecionados = temas if filtrar_por_tema else []
frequencia_selecionada = frequencia if filtrar_por_frequencia else []

resultado_pesquisa = search(orgaos_selecionados, temas_selecionados, frequencia_selecionada)

st.markdown("## Selecione uma série estatística")
serie_selecionada = st.selectbox(
    "Série estatística",
    options=resultado_pesquisa["CODE"] if not resultado_pesquisa.empty else [],
    format_func=lambda x: resultado_pesquisa.loc[resultado_pesquisa["CODE"] == x, "NAME"].values[0] if not resultado_pesquisa.empty else "",
    index=None,
    placeholder="Pesquise ou selecione uma série..."
)

if st.button("Enviar alerta"):
    if not email:
        st.warning("Preencha o campo de e-mail.")
    elif not serie_selecionada:
        st.warning("Selecione uma série estatística.")
    else:
        nome_serie = resultado_pesquisa.loc[resultado_pesquisa["CODE"] == serie_selecionada, "NAME"].values[0]
        st.success("Alerta configurado com sucesso!")

        detalhes_alerta = f"""
        <div class="custom-popup">
            <h3>Detalhes do alerta</h3>
            <p><strong>E-mail:</strong> {email}</p>
            <p><strong>Porcentagem:</strong> {porcentagem}%</p>
            <p><strong>Série Estatística:</strong> {nome_serie}</p>
            <p><strong>Frequência:</strong> {', '.join(frequencia_selecionada) or 'Não selecionado'}</p>
            <p><strong>Órgãos:</strong> {', '.join(orgaos_selecionados) or 'Não selecionado'}</p>
            <p><strong>Temas:</strong> {', '.join([df_temas.loc[df_temas['ID'] == x, 'NAME'].values[0] for x in temas_selecionados]) or 'Não selecionado'}</p>
        </div>
        """

        st.markdown(detalhes_alerta, unsafe_allow_html=True)