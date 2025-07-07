import streamlit as st
from pathlib import Path
import base64


def get_img_as_base64(path):
    with open(path, "rb") as img_file:
        return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    

def get_base64_of_bin_file(bin_file_path):
    with open(bin_file_path, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Caminhos
current_dir = Path(__file__).parent
logo_path = current_dir / "interface" / "views" / "assets" / "img" / "Icon.png"
ilustra_path = current_dir / "interface" / "views" / "assets" / "img" / "home_ilustracao.png"
main_style_path = current_dir / "interface" / "views" / "assets" /"stylesheets" / "mainStyle.css"
base_img_path = current_dir / "interface" / "views" / "assets" / "img" / "sobre_ilustracao.png"
equipe_img_path = current_dir / "interface" / "views" / "assets" / "img" / "equipe"

st.set_page_config(
    page_title="Gov Insights",
    page_icon=logo_path,
    layout="wide")


if 'page' not in st.session_state:
    st.session_state.page = "landing"

# Estilo principal
if main_style_path.exists():
    with open(main_style_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("Arquivo mainStyle.css não encontrado.")

st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

logo_base64 = get_img_as_base64(logo_path)


def landing_page():
    # Cabeçalho
    st.markdown(f"""
    <div class="navbar">
        <div class="nav-left">
            <img src="{logo_base64}" class="logo-img">
        </div>
        <div class="nav-center">
            <a href="#como-funciona">Como Funciona</a>
            <a href="#sobre">Sobre o Projeto</a>
            <a href="#ipeadatapy">API</a>
            <a href="#equipe">Equipe</a>
        </div>
        <div class="nav-right">
            <a href="https://2025-1-govinsights.streamlit.app/" target="_self">
                <button class="nav-button Dashboard">Dashboard</button>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        # Banner principal 
        col1, col2 = st.columns([1.1, 0.9]) 

        with col1:
            st.markdown("""
            <div id="home" class="content-area">
                <h1 class='title'>GOV INSIGHTS</h1>
                <h3 class='subtitle'>Relatórios inteligentes IPEA</h3>
                <p class='descricao'>Sistema Inteligente para Análise Automatizada de Notícias e Indicadores Públicos</p>
                <a href="https://2025-1-govinsights.streamlit.app/" target="_self">
                    <button class="report-button">Gerar Relatório</button>
                </a>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            with col2:
                if ilustra_path.exists():
                    st.markdown("<div style='height:70px;'></div>", unsafe_allow_html=True)
                    st.image(str(ilustra_path), width=400)
                    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

                else:
                    st.warning("Imagem de ilustração não encontrada")

        # Seção Como Funciona
        st.markdown("""
        <div id="como-funciona" class="como-funciona-section">
            <h2 class="como-titulo">COMO FUNCIONA</h2>
            <p class="como-subtitulo">Como a plataforma transforma dados em decisões</p>
        </div>
        """, unsafe_allow_html=True)

        # Cards Como Funciona
        st.markdown("""
        <div class="cards-section">
            <div class="cards-container">
                <div class="card">
                    <div class="card-title">Coleta de Dados</div>
                    <div class="card-text">
                        Integração direta com a API do IPEA garante atualização constante.
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Visualização Intuitiva</div>
                    <div class="card-text">
                        Dashboards interativos com filtros por setor e período.
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Análise com IA</div>
                    <div class="card-text">
                        Modelos LLM geram resumos e relatórios automaticamente.
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Alertas Inteligentes</div>
                    <div class="card-text">
                        Notificações automatizadas sobre mudanças e tendências relevantes.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Sobre o Projeto
        st.markdown(f"""
        <div id="sobre" class='sobre-projeto-section'>
            <div class='sobre-imagem'>
                <img src='data:image/png;base64,{get_base64_of_bin_file(base_img_path)}' style='max-width: 400px; width: 100%;' />
            </div>
            <div class='sobre-texto'>
                <h1 class='title'>SOBRE O PROJETO</h1>
                <h3 class='subtitle'>
                    Democratizar o acesso à análise econômica e de dados públicos.<br>
                    Unimos inteligência artificial e design acessível para que qualquer pessoa<br>possa entender e utilizar informações financeiras de forma prática e eficiente.
                </h3>
                <a href="https://unb-mds.github.io/2025-1-GovInsights/" target="_blank">
                    <button class='report-button'>Como contribuir</button>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Documetação IPEADATAPY 
        st.markdown("""
            <div id="ipeadatapy" style="background-color: #F9FBFC; padding: 2rem 4rem; border-radius: 8px;">
                    <h3 id="IPEA" style="color: #1A1A1A;">IPEADATAPY</h3>
                <p style="font-size: 1.2rem; line-height: 1.6; color: #1A1A1A; margin-bottom: 1rem;">
                    Hoje, os dados do IPEA estão dispersos e exigem conhecimento técnico para análise.
                    Isso afasta o cidadão comum e desacelera a gestão pública eficiente.
                </p>
                <p style="font-size: 1.3rem; font-weight: bold; line-height: 1.6; color: #1A1A1A; margin-bottom: 0.9rem;">
                    O Gov Insights traduz grandes volumes de dados e notícias em insights claros, rápidos e visualmente acessíveis.
                </p>
                <p style="font-size: 1.1rem; line-height: 1.6; color: #1A1A1A; margin-bottom: 1rem;">
                    Para isso, utilizamos a API <strong>ipeadatapy</strong>, uma biblioteca que permite acesso programático aos dados públicos do <strong>Instituto de Pesquisa Econômica Aplicada (IPEA)</strong>.
                    Essa integração possibilita a consulta, atualização e visualização de séries históricas econômicas e sociais de forma automatizada, permitindo que relatórios sejam gerados com dados sempre atualizados e confiáveis.
                </p>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <a href="https://drive.google.com/file/d/1jE-Z9-whcvg3NkXryME-2nUC6YzT4aIc/view?usp=drive_link" target="_blank"
                    style="font-size: 1.1rem; color: #2BB17A; text-decoration: none; font-weight: 600; margin-right: 1.5rem;">
                        Ver Exemplo de Relatório →
                    </a>
                    <a href="http://ipeadatapyresume.streamlit.app/" target="_blank">
                        <button class="report-button">Explorar ipeadatapy</button>
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Equipe
        image_paths = [
            equipe_img_path / "eric.png",
            equipe_img_path / "mayra.png",
            equipe_img_path / "brenda.png",
            equipe_img_path / "marjorie.png",
            equipe_img_path / "maria.png",
            equipe_img_path / "guilherme.png",
            equipe_img_path / "eduarda.png",
            equipe_img_path / "gabriel.png",
        ]

        profile_links = [
            "https://github.com/EricAraujoBsB", 
            "https://github.com/Lithuania0",   
            "https://github.com/Brwnds",  
            "https://github.com/Marjoriemitzi", 
            "https://github.com/mariadenis",    
            "https://github.com/GFlyan",
            "https://github.com/eduardar0",  
            "https://github.com/gabegmbr",    
        ]

        # Caminho das imagens
        encoded_images = [get_base64_of_bin_file(p) for p in image_paths]

        image_html = ''.join(
            f'<a href="{link}" target="_blank"><img src="data:image/png;base64,{img}" /></a>'
            for img, link in zip(encoded_images, profile_links)
        )

        st.markdown(f"""
        <div id="equipe" class="equipe-section">
            <h2>NOSSA EQUIPE</h2>
            <p>Quem está por trás do projeto?</p>
            <div class="equipe-grid">
                {image_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

if st.session_state.page == "landing":
    landing_page()
