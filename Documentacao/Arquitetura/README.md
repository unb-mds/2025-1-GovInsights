# 📊 GovInsights - Projeto de Geração Automática de Relatórios de Series Financeiras do IPEA

Este projeto tem como objetivo gerar relatórios financeiros automatizados sobre séries financeiras do **IPEA** (**Instituto de Pesquisa Econômica Aplicada**) com base em dados de entrada fornecidos pelo usuário. A aplicação foi desenvolvida com foco prioritário em organização e manutenção fácil, utilizando o Streamlit como framework principal.

---

## 🧱 Arquitetura

### Modelo Arquitetural: Client-Server

O projeto segue o modelo arquitetural **Client-Server**, que é reativo e orientado ao backend, como recomendado pelo Streamlit. Nesse modelo, o cliente é o navegador (frontend), e a interface é gerada e controlada pelo servidor (backend) em Python. O Streamlit permite que a aplicação seja construída de forma fullstack, ou seja, com Python controlando tanto a lógica da aplicação quanto a geração da interface, o que facilita o desenvolvimento de aplicações interativas com uma única linguagem.

No contexto desse modelo, o **banco de dados (Supabase)** faz parte da **camada de backend**, sendo acessado exclusivamente pelo servidor. O cliente nunca interage diretamente com o banco — todas as requisições passam pelo servidor, que processa, consulta ou armazena os dados antes de responder ao cliente. Isso mantém a separação clara entre as camadas e reforça a segurança e a organização do sistema.

### Camadas da Arquitetura

#### Frontend
- **Frontend:** A interface do usuário é gerada e controlada **pelo servidor** utilizando **Streamlit**, garantindo uma experiência interativa e visualmente atraente. O navegador atua como o **cliente**, recebendo a interface e interagindo com o backend.

#### Backend
- **Backend:** A lógica de negócio, manipulação de dados de séries do IPEA e integração com IA para geração de relatórios são tratadas pela camada **services**, totalmente desenvolvida com **Python**. O **servidor** é responsável por processar as interações e gerar a interface que será enviada ao cliente. 

#### Database
- **Armazenamento de séries:** As séries a serem alertadas serão armazenadas em um banco de dados relacional **PostgreSQL** na **Supabase**, uma plataforma de backend como serviço que facilita o gerenciamento de bancos de dados, autenticação e APIs. A escolha do **Supabase** foi feita devido à sua facilidade de integração, soluções robustas para bancos de dados e seu plano gratuito, que se adequa perfeitamente ao escopo do projeto acadêmico.

* **Motivo para a escolha do Supabase:**
  - **Fácil integração:** O Supabase oferece uma solução prática e de fácil integração com o Streamlit, o que facilita a conexão entre o backend Python e o banco de dados PostgreSQL através de métodos nativos do próprio Supabase.
  - **Plano gratuito:** O plano gratuito do Supabase oferece **1 GB de armazenamento de banco de dados**, o que é suficiente para o armazenamento dos dados por parte deste projeto acadêmico.

  
### **Visualização da Arquitetura do Projeto**

![alt text](./diagramas/arquitetura.png)

---

## 🗂️ Estrutura do Projeto

├── `interface`/ 💎 camada de apresentação\
├── `services`/  🧑‍💻 lógica do projeto\
├── `data`/      📊 interação com o banco de dados\
└── `main.py`    🚀 ponto de entrada da aplicação

---

## 📂 Descrição dos Diretórios

### 🔷`interface/`
- **Função:** Camada de apresentação (UI).
- **Tecnologias:** Streamlit + Python.
- **Responsável por:** Renderizar a interface de usuário e coletar inputs.

### 🔷`services/`
- **Função:** Lógica de negócio.
- **Tecnologias:** Python, API IPEA, Pandas, DeepSeek R1 Distill Llama 70B Free, Plotly.
- **Responsável por:** Conectar-se à biblioteca `ipeadatapy` para obter séries financeiras, processando e gerando relatórios financeiros com o modelo gratuito de LLM DeepSeek R1 Distill Llama 70B Free através da biblioteca together fornecida pela empresa Together.ai.

### 🔷`data/`
- **Função:** Interação com o banco de dados.
- **Tecnologias:** Supabase, Python.
- **Responsável por:** Gerenciar a conexão com o banco de dados hospedado no Supabase baseado em PostgreSQL, realizando operações de busca e inserção de dados sobre séries financeiras escolhidas pelo usuário à serem alertadas de acordo com atualizações.

### 🔷`main.py`
- **Função:** Ponto de entrada da aplicação.
- **Tecnologias:** Python.
- **Responsável por:** Inicializar dependências e executar a aplicação.

---

## 🔁 Relações Entre Diretórios

| Diretório     | Pode chamar...                              | Pode ser chamado por...                   |
|---------------|----------------------------------------------|-------------------------------------------|
| `main.py`     | `interface/`                                        | —                                         |
| `interface/`  | `services/`                                  | `main.py`                                 |
| `services/`   | `data/`                                       | `interface/`                              |
| `data/`       | —                                            | `services/`                               |


---

## 🚀 Tecnologias Principais

- **Frontend:** Streamlit
- **Backend:** Python
- **Banco de Dados:** Supabase
- **IA:** DeepSeek R1 Distill Llama 70B Free (Together.ai)
- **Gráficos:** Plotly
- **Manipulação de Dados:** Pandas

---

## 📌 Requisitos

- Python 3.10+
- Streamlit
- pandas, plotly, together, etc.

---

## ▶️ Executando o Projeto

```bash
# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run main.py
```

---

## 🌐 Deploy

### Aplicação

O deploy será realizado utilizando o sistema de nuvem do **Streamlit Community Cloud**. A escolha do Streamlit para hospedagem se deve à sua integração simplificada com o próprio framework, além de fornecer recursos gratuitos de fácil acesso.

### Banco de Dados

Optou-se pelo **Supabase**, uma solução de banco de dados em nuvem que oferece **PostgreSQL** como serviço simplificado através métodos nativos em python da própria biblioteca `supabase`. A escolha foi motivada pela **escalabilidade** da plataforma, permitindo o crescimento do projeto conforme a quantidade de dados aumenta. Além disso, a **facilidade de integração** com o Streamlit torna simples o acesso ao banco de dados pela aplicação, sem a necessidade de configurações complexas. O Supabase também oferece um **plano gratuito**, ideal para fins acadêmicos e de prototipagem. Por fim, o uso do **PostgreSQL** garante uma solução robusta e confiável para armazenar históricos de relatórios e informações sensíveis.

* Com isso, o banco de dados será armazenado na nuvem **Supabase**, enquanto a aplicação estará hospedada no **Streamlit Community Cloud**, permitindo que o backend da aplicação interaja diretamente com o banco de dados na nuvem.



