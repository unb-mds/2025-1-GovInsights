import streamlit as st
from pathlib import Path
import base64

st.set_page_config(page_title="Gov Insights", layout="wide")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

# Caminhos
current_dir = Path(__file__).parent
logo_path = current_dir / "interface" / "new-views" / "assets" / "img" / "Icon.png"
ilustra_path = current_dir / "interface" / "new-views" / "assets" / "img" / "home_ilustracao.png"
main_style_path = current_dir / "interface" / "new-views" / "assets" /"stylesheets" / "mainStyle.css"


# Estilo principal
if main_style_path.exists():
    with open(main_style_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("Arquivo mainStyle.css não encontrado.")



# Cabeçalho
col1, col2 = st.columns([1, 4])
with col1:
    if logo_path.exists():
        st.image(str(logo_path), width=60)
with col2:
    st.markdown("""
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <h2 style='margin-bottom: 0; color: white;'>Gov Insights</h2>
        <div style='display: flex; gap: 20px; font-size: 16px;'>
            <a href="#" style='color: #00DFA2; text-decoration: underline;'>Home</a>
            <a href="#" style='color: #00DFA2; text-decoration: none;'>Como Funciona</a>
            <a href="#" style='color: #00DFA2; text-decoration: none;'>Sobre o Projeto</a>
            <a href="#" style='color: #00DFA2; text-decoration: none;'>Equipe</a>
            <a href="#" style='color: #00DFA2; text-decoration: none;'>Contato</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #00DFA2;'>", unsafe_allow_html=True)

# Hero Section
col_text, col_img = st.columns([3, 2])
with col_text:
    st.markdown("""
    <div style='margin-top: 200px; line-height: 1.6;'>
        <h1 style='color: white; font-size: 140px;'>GOV INSIGHTS</h1>
        <h1 style='color: #00DFA2; margin-bottom: 20px;'>Relatórios inteligentes IPEA</h1>
        <h1 style='color: #e0e0e0; font-size: 20px; max-width: 500px; margin-top: 0;'>
            Sistema inteligente para Análise Automatizada de Notícias e Indicadores Públicos
        </h1>
    </div>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
    """, unsafe_allow_html=True)


    if st.button("Gerar Relatório", help="Clique para ir ao Dashboard"):
        st.session_state.page = "dashboard"

with col_img:
    if ilustra_path.exists():
        st.image(str(ilustra_path), use_container_width=True)
    else:
        st.warning(f"Imagem de ilustração não encontrada: {ilustra_path}")
