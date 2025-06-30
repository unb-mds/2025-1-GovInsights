import streamlit as st
from pathlib import Path
import base64


def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

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
equipe_img_path = current_dir / "interface" / "views" / "assets" / "img" 

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

def landing_page():

    # Cabeçalho
    
    st.markdown(f"""
    <div class="navbar">
        <div class="nav-left">
            <img src="{logo_path}" class="logo-img">
        </div>
        <div class="nav-center">
            <a href="#como-funciona">Como Funciona</a>
            <a href="#sobre">Sobre o Projeto</a>
            <a href="#equipe">Equipe</a>
        </div>
        <div class="nav-right">
            <button class="nav-button Dashboard">Dashboard</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # col1, col2 = st.columns([1, 4])
    # with col1:
    #     if logo_path.exists():
    #         st.image(str(logo_path), width=60)
    # with col2:
    #     st.markdown("""
    #     <div style='display: flex; justify-content: space-between; align-items: center;'>
    #         <h2 style='margin-bottom: 0; color: white;'>Gov Insights</h2>
    #         <div style='display: flex; gap: 20px; font-size: 16px;'>
    #             <a href="#home" style='color: #00DFA2; text-decoration: underline;'>Home</a>
    #             <a href="#como-funciona" style='color: #00DFA2; text-decoration: none;'>Como Funciona</a>
    #             <a href="#sobre-o-projeto" style='color: #00DFA2; text-decoration: none;'>Sobre o Projeto</a>
    #             <a href="#equipe" style='color: #00DFA2; text-decoration: none;'>Equipe</a>
    #             <!-- <a href="#contato" style='color: #00DFA2; text-decoration: none;'>Contato</a> -->
    #         </div>
    #     </div>
    #     """, unsafe_allow_html=True)


    # st.markdown("<hr style='border: 1px solid #00DFA2;'>", unsafe_allow_html=True)


    with st.container():
        # Banner principal 
        col1, col2 = st.columns([1.1, 0.9]) 

        with col1:
            st.markdown("""
            <div id="home" class="content-area">
                <h1 class='title'>GOV INSIGHTS</h1>
                <h3 class='subtitle'>Relatórios inteligentes IPEA</h3>
                <p class='descricao'>Sistema Inteligente para Análise Automatizada de Notícias e Indicadores Públicos</p>
                <button class="report-button">Gerar Relatório</button>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            with col2:
                if ilustra_path.exists():
                    st.markdown("<div style='height:70px;'></div>", unsafe_allow_html=True)
                    st.image(str(ilustra_path), use_container_width=True, width=400)
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
                        Modelos NLP (Mistral-7B) geram resumos e relatórios automaticamente.
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Alertas Inteligentes</div>
                    <div class="card-text">
                        Notificações automáticas sobre mudanças e tendências relevantes.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Sobre o Projeto
        st.markdown(f"""
        <div id="sobre" class='sobre-projeto-section'>
            <div class='sobre-imagem'>
                <img src='data:image/png;base64,{base_img_path}' style='max-width: 400px; width: 100%;' />
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

        # texto white 
        st.markdown("""
        <div style="background-color: #F9FBFC; padding: 2rem 4rem; border-radius: 8px;">
            <p style="font-size: 1.2rem; line-height: 1.6; color: #1A1A1A; margin-bottom: 1rem;">
                Hoje, os dados do IPEA estão dispersos e exigem conhecimento técnico para análise.
                Isso afasta o cidadão comum e desacelera a gestão pública eficiente.
            </p>
            <p style="font-size: 1.3rem; font-weight: bold; line-height: 1.6; color: #1A1A1A; margin-bottom: 0.9rem;">
                O Gov Insights traduz grandes volumes de dados e notícias em insights claros, rápidos e visualmente acessíveis.
            </p>
            <a href="https://unb-mds.github.io/2025-1-GovInsights/" target="_blank"
            style="font-size: 1.1rem; color: #2BB17A; text-decoration: none; font-weight: 600;">
                Ver Exemplo de Relatório →
            </a>
        </div>
        """, unsafe_allow_html=True)

        # Equipe
        membros = [
            ("­", "­", "eric.png"),
            ("­", "­", "mayra.png"),
            ("­", "­", "brenda.png"),
            ("­", "­", "marjorie.png"),
            ("­", "­", "eduarda.png"),
            ("­", "­", "guilherme.png"),
            ("­", "­", "rodrigues.png"),
            ("­", "­", "gabriel.png")
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
        equipe_img_path = current_dir / "interface" / "views" / "assets" / "img" / "equipe"

        # encoded_images = [get_base64_of_bin_file(p) for p in membros]

        # Exibe os membros em linhas de 4
        for i in range(0, len(membros), 4):
            cols = st.columns(4)
            for col, (nome, funcao, img_file) in zip(cols, membros[i:i+4]):
                img_path = equipe_img_path / img_file
                with col:
                    if img_path.exists():
                        img_base64 = get_base64_image(img_path)
                        st.markdown(f"""
                            <div class="img-container">
                                <img src="data:image/png;base64,{img_base64}" class="membro-img" />
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning(f"Imagem não encontrada: {img_file}")
                    st.markdown(f"<h4 style='margin: 0.3rem 0 0; color: white;'>{nome}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin: 0; color: #00DFA2; font-size: 0.9rem;'>{funcao}</p>", unsafe_allow_html=True)



        
        # Primeiro cria as colunas
        # col_text, col_img = st.columns([3, 2])
        
        # Depois usa as colunas criadas
    #     with col_text:
    #         st.markdown("""
    #         <div style='margin-top: 200px; line-height: 1.6;'>
    #             <h1 style='color: white; font-size: 140px;'>GOV INSIGHTS</h1>
    #             <h1 style='color: #00DFA2; margin-bottom: 20px;'>Relatórios inteligentes IPEA</h1>
    #             <h1 style='color: #e0e0e0; font-size: 20px; max-width: 500px; margin-top: 0;'>
    #                 Sistema inteligente para Análise Automatizada de Notícias e Indicadores Públicos
    #             </h1>
    #             <br>
    #             <br>
    #                     <br>
                        
    #         </div>
    #         """, unsafe_allow_html=True)

    #         if st.button("Gerar Relatório", help="Clique para ir ao Dashboard", key="dashboard_btn"):
    #             st.session_state.page = "dashboard"
    #             st.rerun()

    #     with col_img:
    #         if ilustra_path.exists():
    #             st.image(str(ilustra_path), use_container_width=True)
    #         else:
    #             st.warning("Imagem de ilustração não encontrada")





    # # Seção: Como Funciona
    # st.markdown("""
    # <div style='margin-top: -50px;'>
    #     <h1 style='text-align: center; color: white;'>COMO FUNCIONA</h1>
    #             <br>
    #     <p style="text-align: center; color: #00DFA2; font-size: 30px;">
    #         Como a plataforma transforma dados em decisões
    #     </p>
    # </div>
    # """, unsafe_allow_html=True)

    # st.markdown("""

    # <div class="container">
    #     <div class="card">
    #         <h3>📡</h3>
    #         <h3> Coleta de Dados</h3>
    #         <p>Integração direta com a API do IPEA garante atualização constante.</p>
    #     </div>
    #     <div class="card">
    #         <h3>📊</h3>
    #         <h3>Visualização Intuitiva</h3>
    #         <p>Dashboards interativos com filtros por setor e período.</p>
    #     </div>
    #     <div class="card">
    #         <h3>🧠</h3>
    #         <h3> Análise com IA</h3>
    #         <p>Modelos NLP (Mistral-7B) geram resumos e relatórios automaticamente.</p>
    #     </div>
    #     <div class="card">
    #         <h3>🚨</h3>
    #         <h3> Alertas Inteligentes</h3>
    #         <p>Notificações automáticas sobre mudanças e tendências relevantes.</p>
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)


    # # Seção: Sobre o Projeto
    # st.markdown("<br><br>", unsafe_allow_html=True)

    # col_img, col_text = st.columns([1, 2])

    # with col_img:
    #     if base_img_path.exists():
    #         st.image(str(base_img_path), use_container_width=True)
    #     else:
    #         st.warning(f"Imagem de ilustração do projeto não encontrada: {base_img_path}")

    # with col_text:
    #     st.markdown("""
    #     <div style='margin-top: 100px; line-height: 1.6;'>
    #         <h1 style='color: white; font-size: 140px;'>Sobre o projeto</h1>
    #         <p style='color: #00DFA2;font-size: 40px'>Democratizar o acesso à análise econômica e de dados públicos.</p>
    #         <p style='color: #00DFA2; max-width: 900px; font-size: 40px'>
    #             Unimos inteligência artificial e design acessível para que qualquer pessoa possa entender e utilizar informações financeiras de forma prática e eficiente.
    #         </p>
    #         <a href='#' style='background-color: #0F3D3E; padding: 10px 20px; color: white; border-radius: 5px;
    #     </div>
    #     <br>
    #     <br>
    #     <br>           
    #     """, unsafe_allow_html=True)
    #     with st.container():
    #         with st.container():
    #             col1, _ = st.columns([1, 5])
    #             with col1:
    #                 with st.container():
    #                     if st.button("Como contribuir", key="btn_contribuir", help="Clique para saber como contribuir"):
    #                         st.session_state.page = "contribuir"  #depois ajeito ####################################################
        
    # st.markdown("""<div id='equipe'></div>
    # <h2 style='text-align: center; color: white; font-size: 2.5rem;'>NOSSA EQUIPE</h2>
    # <p style='text-align: center; color: #00DFA2; font-size: 1.2rem;'>Quem está por trás do projeto?</p>
    # """, unsafe_allow_html=True)

if st.session_state.page == "landing":
    landing_page()
