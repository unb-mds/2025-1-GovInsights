# Visão do Produto

## GovInsights  
**Sistema Inteligente para Análise Automatizada de Notícias e Indicadores Públicos**

---
## Objetivos 
Este projeto tem como objetivo fornecer uma plataforma interativa e acessível para a visualização de dados financeiros do IPEA (Instituto de Pesquisa Econômica Aplicada), utilizando **Streamlit** e **modelos de Processamento de Linguagem Natural (NLP)** para gerar relatórios automáticos e análises detalhadas. A solução visa democratizar o acesso a dados financeiros, oferecendo relatórios interativos, automáticos e dinâmicos, facilitando a tomada de decisões.

Através da **API do IPEA**, o projeto consome dados financeiros atualizados, enquanto o uso do **Deepseek** permite gerar resumos automáticos e previsões financeiras. A plataforma será hospedada utilizando **Streamlit Deploy** e **Git Pages**, proporcionando fácil acesso a partir de qualquer dispositivo conectado à internet.

### **Objetivos principais:**
1. **Acesso Interativo aos Dados**: Exibição de dados financeiros do IPEA por meio de gráficos interativos.
2. **Geração Automática de Relatórios**: Utilizando **Deepseek** para geração de relatórios automáticos.
3. **Sistema de Alertas**: Notificação de mudanças ou tendências financeiras importantes.
4. **Visibilidade e Transparência**: Informações de fácil acesso para cidadãos, pesquisadores e gestores públicos.

## Missão

Democratizar o acesso à análise econômica e de dados públicos, transformando dados e textos de fontes oficiais em informações claras, acessíveis e acionáveis, utilizando ferramentas digitais modernas, identidades visuais consistentes e tecnologias de Inteligência Artificial.

---

## Problemática

Atualmente, dados econômicos e notícias públicas, como as do IPEA, estão dispersos e pouco acessíveis para a maioria dos cidadãos. A análise ainda é manual, lenta e restrita a especialistas, dificultando a educação pública, a gestão informada e a participação cidadã.

---

## Solução Proposta

**GovInsights** é uma plataforma modular, baseada em **Streamlit**, que coleta, analisa e apresenta de maneira intuitiva:

- Séries temporais econômicas e indicadores públicos;
- Notícias recentes processadas com modelos de Processamento de Linguagem Natural (NLP);
- Relatórios automáticos em formatos PDF e HTML, combinando análise quantitativa e qualitativa.

Ela permitirá que qualquer usuário:

- **Explore** dados com filtros temporais, regionais e setoriais;
- **Visualize** tendências extraídos de notícias públicas;
- **Gere** relatórios de forma automática e exportável;
- **Navegue** com uma identidade visual moderna e acessível.

---

## Diferenciais

- Interface amigável, desenvolvida com Streamlit + HTML/CSS customizado;
- Identidade visual própria (marca, paleta de cores e design manual);
- Pipeline automatizado para coleta, processamento e exibição dos dados;
- Uso de modelos NLP ou LLM open-source (Deepseek);
- Integração direta com a API do IPEA para atualização contínua dos dados;
- Geração de relatórios em múltiplos formatos (PDF e HTML).

---

## Impacto Esperado

- Redução no tempo e esforço de análise de dados públicos;
- Facilitação do acesso cidadão a dados econômicos e sociais;
- Apoio à transparência pública e gestão baseada em evidências;
- Estímulo à educação econômica e política a partir de fontes abertas.

---
### **Tecnologias Utilizadas**:
- **Backend**: **Python**
- **Frontend**: **Streamlit**
- **NLP**: **LLM Deepseek**
- **Bibliotecas**: **pandas 2.2.3**, **plotly 6.0.1**, **requests 2.32.3**
- **Deploy**: **Streamlit Deploy**, **Git Pages**

---

## 👥 Participantes e Papéis

| Papel                   | Responsáveis                                      | Atividades Principais                                            |
|--------------------------|---------------------------------------------------|------------------------------------------------------------------|
| Stakeholders    | Eric, Brenda e Maria Eduarda                                      | Validação dos requisitos e avaliação dos resultados             |
| Product Owner            | Brenda                                     | Priorização de funcionalidades, gestão do backlog                |
| FrontEnd|   Eduarda e Mayra |  Desenvolvimento da identidade visual, telas (Login, Exportação, Landing Page), integração Streamlit + HTML/CSS |
| BackEnd | Marjorie, Guilherme e Gabriel| Integração da API IPEA, coleta de dados, implementação dos métodos GET e POST |
| Gestão de Projetos | Eric, Brenda e Maria Eduarda | Cronograma, controle de sprints, revisão de branches e suporte de gestão ágil |
| Usuário Final             | Público geral e servidores públicos              | Consumo dos relatórios gerados e análise dos indicadores         |

---

## 📋 Controle de Revisão do Documento

| Versão | Data da Modificação | Responsável          | Descrição da Alteração                   |
|--------|---------------------|----------------------|------------------------------------------|
| 1.0    | 13/04/2025           | Brenda       | Criação do Documento de Visão do Produto |
| 1.1    | 27/04/2025           | Brenda       | Atualização com base nas decisões tomadas nas Sprints   |
| 1.2    | 08/05/2025           | Eric       | Revisão   |

