<h1 align="center" style="font-weight: bold;">📊 GovInsights - Análise de Dados Públicos  </h1>

<p align="center">
 <a href="https://unb-mds.github.io/2025-1-Squad10/">Git Pages</a>
</p>

## 📚 Projeto

Desenvolvido para a disciplina **Métodos de Desenvolvimento de Software - 2025/1**.


---

O **GovInsights** é uma plataforma de análise e visualização de dados financeiros públicos, focada inicialmente nos dados do **IPEA**.  
O projeto busca democratizar o acesso às informações públicas através de relatórios inteligentes e dashboards interativos, utilizando **processamento de linguagem natural** e **visualizações dinâmicas** para facilitar a tomada de decisão e promover a transparência governamental.

---

<h2 id="objectives">📌 Objetivos</h2>

- Automatizar a coleta e análise de dados financeiros públicos.
- Facilitar o acesso à informação através de visualizações e relatórios interativos.
- Identificação de tópicos em notícias relacionadas.
- Estimular a transparência, a cidadania ativa e o uso de dados públicos.
- Promover boas práticas de desenvolvimento ágil e colaborativo utilizando GitHub e metodologias ágeis.
---
  
<h2 id="tech">⚙️ Tecnologias Utilizadas</h2>

- **Backend**: **Python 3.x**
- **Frontend**: **Streamlit**
- **Modelo de LLM**: **DeepSeek-R1-Distill-Llama-70B-free via API do Together AI**
- **Bibliotecas**: **pandas 2.2.3**, **plotly 6.0.1**, **requests 2.32.3**
- **Deploy**: **Streamlit Deploy**, **Git Pages**
---

## Collaborators

O projeto é desenvolvido pelos seguintes integrantes:

| Papel                   | Responsáveis                                      | Atividades Principais                                            |
|--------------------------|---------------------------------------------------|------------------------------------------------------------------|
| Stakeholders    | Eric, Brenda e Maria Eduarda                                      | Validação dos requisitos e avaliação dos resultados             |
| Product Owner            | Brenda                                     | Priorização de funcionalidades, gestão do backlog                |
| FrontEnd|   Eduarda e Mayra |  Desenvolvimento da identidade visual, telas (Login, Exportação, Landing Page), integração Streamlit + HTML/CSS |
| BackEnd | Marjorie, Guilherme e Gabriel| Integração da API IPEA, coleta de dados, implementação dos métodos GET e POST |
| Gestão de Projetos | Eric, Brenda e Maria Eduarda | Cronograma, controle de sprints, revisão de branches e suporte de gestão ágil |
| Usuário Final             | Público geral e servidores públicos              | Consumo dos relatórios gerados e análise dos indicadores         |

---


<table>
  <tr>
    <td align="center">
      <a href="https://github.com/EricAraujoBsB">
        <img src="assets/Colabs/Eric Gomes.jpeg" width=128px; height= 128px; style="width=128; height=128; object-fit: cover"; alt="Eric Gomes"/><br>
        <p><b>Eric Gomes de Araujo</b></p>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Lithuania0">
        <img src="assets/Colabs/Mayra Lithuania.jpeg" width=128px; height= 128px; style="width=128; height=128; object-fit: cover"; alt="Mayra Lithuania"/><br>
        <p><b>Mayra Lithuania</b></p>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Brwnds">
        <img src="assets/Colabs/Brenda.jpeg" width=128px; height=128px; style="width=128; height=128; object-fit: cover"; alt="Brenda Beatriz"/><br>
        <p><b>Brenda Beatriz</b></p>
      </a>
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://github.com/GFlyan">
        <img src="assets/Colabs/Guilherme Flyan.jpeg" width=128px; height=128px; style="width=128; height=128; object-fit: cover"; alt="Guilherme Flyan"/><br>
        <p><b>Guilherme Flyan</b></p>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/eduardar0">
        <img src="assets/Colabs/Eduarda Rodrigues.jpeg" width=128px; height=128px; style="width=128; height=128; object-fit: cover";;" alt="Eduarda Rodrigues"/><br>
        <p><b>Eduarda Rodrigues</b></p>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/mariadenis">
        <img src="assets/Colabs/Maria Eduarda.jpeg" width=128px; height=128px; style="width=128; height=128; object-fit: cover";;" alt="Maria Eduarda"/><br>
        <p><b>Maria Eduarda</b></p>
      </a>
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://github.com/gabegmbr">
        <img src="assets/Colabs/Gabriel Maciel.jpeg" width=128px; height=128px; style="width=128; height=128; object-fit: cover"; alt="Gabriel Maciel"/><br>
        <p><b>Gabriel Maciel</b></p>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Marjoriemitzi">
        <img src="assets/Colabs/Marjorie.jpeg" width=128px; height=128px; style="width=128; height=128; object-fit: cover"; alt="Marjorie Mitzi"/><br>
        <p><b>Marjorie Mitzi</b></p>
      </a>
    </td>
  </tr>
</table>

- Eric Gomes de Araujo – Desenvolvedor / Planejamento
- Mayra Lithuania – Frontend / Design
- Brenda Beatriz – Gestão de Projetos / Documentação
- Guilherme Flyan – Backend
- Eduarda Rodrigues – Frontend / Identidade Visual
- Maria Eduarda – Gestão de Projetos
- Gabriel Maciel – Backend
- Marjorie Mitzi – Backend / Análise de Dados


---

<h2 id="contrib">🤝 Como Contribuir</h2>

Quer contribuir? Siga os passos:

1. Leia a documentação disponível.
2. Crie uma issue para reportar problemas ou sugerir melhorias.
3. Faça um fork e crie uma branch específica:

```bash
git checkout -b feature/nome-da-sua-feature
```

4. Realize o desenvolvimento seguindo o padrão do projeto.
5. Envie seu Pull Request para revisão.

**Regras:**
- Siga o padrão de commits.
- Atualize a documentação sempre que necessário.
- Seja colaborativo e respeitoso.
---

# Como começar

## Instalando Python 3
### No Windows

- Baixe e instale o [Python 3]([Download Python | Python.org](https://www.python.org/getit/)).
### No Linux

- No Linux, é necessário instalar os pacotes de desenvolvimento do Python. Utilize o seguinte comando:
```
sudo apt install python3-dev python3-pip python3-venv
```
## Clonando repositório

- Clone o repositório utilizando o comando:

```
git clone https://github.com/unb-mds/2025-1-Squad10.git
```

## Criando e ativando um ambiente virtual do Python

- Vá a pasta do repositório

```
cd 2025-1-Squad10
```

-  Crie um ambiente virtual do Python

```
python -m venv venv
```

-  Ative o ambiente virtual

```
# No Windows
venv\Scripts\activate.bat
# No Linux
source ./venv/bin/activate
```
## Instalando pré-requisitos

- Atualize a versão do pip
```
# No Windows
python -m pip install -U pip
# No Linux
python3 -m pip install --upgrade pip
```

- Instale as dependências do projeto com o comando:
```
 pip install -r requirements.txt 
```
---

<h2 id="data">📈 Dados Utilizados</h2>

Os dados utilizados no projeto **GovInsights** serão extraídos de fontes públicas confiáveis, como o portal oficial do **IPEA** e outras fontes governamentais de transparência.

---

<h2 id="access">🌐 Acesso ao Projeto</h2>

- A documentação será hospedada no GitHub Pages. (Em construção)
- O site de visualização será hospedado futuramente na ferramenta de deploy do Streamlit.

---

<h2 id="tools">🔨 Ferramentas e Recursos</h2>

- 🎨 Protótipos no [Figma](https://www.figma.com/team_invite/redeem/JtjJg0xfYUI6RE1FBSzOlM)
- 🧠 Planejamento no [Notion](https://www.notion.so/invite/6e431a0cfdbcdfadde473e1e02023c52e89070ee)
- 📋 Backlog de Desenvolvimento [GitHub Projects](https://github.com/unb-mds/2025-1-Squad10/projects?query=is%3Aopen)
- 🏧 Arquitetura Técnica (em documentação)

---

<h2 id="contact">📞 Contato</h2>

Dúvidas ou sugestões?  
Entre em contato pelo e-mail: 📩 **govinsights.project@gmail.com**

---

<h2 id="history">📜 Histórico de Versões</h2>

| Versão | Data | Descrição | Autor | Revisor |
|:------:|:----:|:---------|:-----:|:-------:|
| 0.1.0  | 20/04/2025 | Estrutura inicial do README | Eric Gomes | Eric Gomes |
| 0.1.1  | 27/04/2025 | Adição de seções e padronização |Brenda | Brenda|
| 0.1.2  | 08/05/2025 | Adição de "Como contribuir" |Eric | Maria Eduarda |

---
