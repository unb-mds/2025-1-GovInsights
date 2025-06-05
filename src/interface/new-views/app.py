import streamlit as st
from pathlib import Path
import base64
from streamlit_extras.switch_page_button import switch_page




st.set_page_config(page_title="Gov Insights", layout="wide")



if 'current_page' not in st.session_state:
    st.session_state.current_page = "Inicio"

def change_page(page_name):
    st.session_state.current_page = page_name



def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

def landing_page():
    # Configurações iniciais




    # Caminhos
    current_dir = Path(__file__).parent
    logo_path = current_dir / "assets" / "img" / "Icon.png"
    ilustra_path = current_dir / "assets" / "img" / "home_ilustracao.png"
    style_path = current_dir / "styles.css"

    # --- Navbar Simples ---
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

    # --- Hero Section ---
    col_text, col_img = st.columns([3, 2])
    with col_text:
        st.markdown("""
        <div style='margin-top: 60px;'>
            <h1 style='color: white; font-size: 48px;'>GOV INSIGHTS</h1>
            <h3 style='color: #00DFA2;'>Relatórios inteligentes IPEA</h3>
            <p style='color: #e0e0e0; font-size: 18px; max-width: 500px;'>
                Sistema inteligente para Análise Automatizada de Notícias e Indicadores Públicos
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Gerar Relatório"):
            switch_page("dashboard")

            

    with col_img:
        if ilustra_path.exists():
            st.image(str(ilustra_path), use_container_width=True)
        else:
            st.warning(f"Imagem de ilustração não encontrada: {ilustra_path}")

    # --- Estilo Externo ---
    style_path = current_dir / "assets" / "stylesheets" / "style.css"
    if style_path.exists():
        with open(style_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Arquivo styles.css não encontrado: {}".format(style_path))

