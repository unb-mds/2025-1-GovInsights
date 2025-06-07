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
base_img_path = current_dir / "interface" / "new-views" / "assets" / "img" / "sobre_ilustracao.png"



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






# Seção: Como Funciona
st.markdown("""
<div style='margin-top: -50px;'>
    <h2 style='text-align: center; color: white;'>COMO FUNCIONA</h2>
    <p style='text-align: center; color: #00DFA2;'>Como a plataforma transforma dados em decisões</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""

<div class="container">
    <div class="card">
        <h3>📡</h3>
        <h3> Coleta de Dados</h3>
        <p>Integração direta com a API do IPEA garante atualização constante.</p>
    </div>
    <div class="card">
        <h3>📊</h3>
        <h3>Visualização Intuitiva</h3>
        <p>Dashboards interativos com filtros por setor e período.</p>
    </div>
    <div class="card">
        <h3>🧠</h3>
        <h3> Análise com IA</h3>
        <p>Modelos NLP (Mistral-7B) geram resumos e relatórios automaticamente.</p>
    </div>
    <div class="card">
        <h3>🚨</h3>
        <h3> Alertas Inteligentes</h3>
        <p>Notificações automáticas sobre mudanças e tendências relevantes.</p>
    </div>
</div>
""", unsafe_allow_html=True)


# Seção: Sobre o Projeto
st.markdown("<br><br>", unsafe_allow_html=True)

col_img, col_text = st.columns([1, 2])

with col_img:
    if base_img_path.exists():
        st.image(str(base_img_path), use_container_width=True)
    else:
        st.warning(f"Imagem de ilustração do projeto não encontrada: {base_img_path}")

with col_text:
    st.markdown("""
    <div style='margin-top: 100px; line-height: 1.6;'>
        <h1 style='color: white; font-size: 140px;'>Sobre o projeto</h1>
        <p style='color: #00DFA2;font-size: 40px'>Democratizar o acesso à análise econômica e de dados públicos.</p>
        <p style='color: #00DFA2; max-width: 900px; font-size: 40px'>
            Unimos inteligência artificial e design acessível para que qualquer pessoa possa entender e utilizar informações financeiras de forma prática e eficiente.
        </p>
        <a href='#' style='background-color: #0F3D3E; padding: 10px 20px; color: white; border-radius: 5px;
    </div>
    <br>
    <br>
    <br>           
    """, unsafe_allow_html=True)
    with st.container():
        with st.container():
            col1, _ = st.columns([1, 5])
            with col1:
                with st.container():
                    if st.button("Como contribuir", key="btn_contribuir", help="Clique para saber como contribuir"):
                        st.session_state.page = "contribuir"  #depois ajeito ####################################################
    