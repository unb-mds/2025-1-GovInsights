# Backlog do Produto

| Prioridade | User Story                                                                                                          | Tipo de Requisito             |
| ---------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| 🚨 **Alta** | Como desenvolvedor, quero importar arquivos via API, para alimentar o pipeline com dados do IPEA.                   | Funcional                     |
| 🚨 **Alta** | Como desenvolvedor, quero que os dados sejam obtidos automaticamente (API ou scraping), para garantir atualizações. | Funcional                     |
| ⚠️ **Média** | Como desenvolvedor, quero aplicar um pipeline de pré-processamento textual, para alimentar os modelos de NLP.       | Funcional                     |
| 🚨 **Alta** | Como desenvolvedor, quero aplicar o BERTopic nos textos, para identificar tópicos relevantes.                       | Funcional                     |
| ⚠️ **Média** | Como analista público, quero visualizar tópicos e exemplos de textos, para entender melhor as áreas críticas.       | Funcional                     |
| 🚨 **Alta** | Como cientista de dados, quero normalizar datas, moedas e categorias, para garantir consistência na análise.        | Funcional                     |
| 🚨 **Alta** | Como gestor público, quero receber um resumo técnico mensal, para entender rapidamente os principais pontos.        | Funcional                     |
| ⚠️ **Média** | Como desenvolvedor, quero utilizar modelos generativos (T5, BART) para gerar resumos a partir dos dados.            | Funcional                     |
| 🚨 **Alta** | Como gestor, quero receber alertas automáticos sobre gastos anormais, para tomar decisões corretivas.               | Funcional                     |
| ⚠️ **Média** | Como desenvolvedor, quero configurar regras para alertas, para evitar falsos positivos.                             | Funcional                     |
| 🚨 **Alta** | Como gestor público, quero visualizar dados e relatórios em uma interface clara, para facilitar a análise.          | Funcional                     |
| ⚠️ **Média** | Como usuário, quero interagir com filtros e gráficos, para explorar períodos e categorias.                 | Funcional                     |
| ⚠️ **Média** | Como analista, quero exportar relatórios em PDF ou HTML, para enviar ou arquivar.                                   | Funcional                     |
| ⚠️ **Média** | Como gestor, quero salvar relatórios anteriores, para acompanhar a evolução dos indicadores.                        | Funcional                     |
| 🚨 **Alta** | Como desenvolvedor, quero criar endpoints REST com FastAPI, para a interface acessar dados dinamicamente.           | Funcional                     |
| 🚨 **Alta** | Como desenvolvedor, quero escrever testes unitários e de integração, para garantir que o sistema funcione.          | Não funcional (qualidade)     |
| 🚨 **Alta** | Como colaborador, quero ter uma documentação clara do pipeline, para facilitar o onboarding.                        | Não funcional (documentação)  |
| ⚠️ **Média** | Como gestor, quero disponibilizar o projeto como código aberto, para outras instituições públicas replicarem.       | Não funcional (licenciamento) |

---
## **Tecnologias Principais**:
- **API do IPEA**: Integração para acessar dados financeiros atualizados.
- **Python 3.x**: Ambiente de desenvolvimento.
- **Streamlit**: Interface do usuário interativa.
- **LLM**: Utilizado para geração de relatórios automáticos.
- **Pandas**: Manipulação de dados financeiros.
- **Plotly**: Visualização gráfica interativa.
- **Requests**: Requisições para consumir dados da API.
---

# 🗺️ Story Map - Projeto Relatórios do IPEA

<table style="width: 100%; background-color:white; border: 1px solid black; border-collapse: collapse;">
  <thead>
    <tr style="height: 43px; background-color: #f2f2f2; border: 1px solid black;">
      <th style="width: 15%; text-align: center; font-weight: bold; height: 43px; border: 1px solid black;">Epics</th>
      <th style="width: 15%; text-align: center; font-weight: bold; height: 43px; border: 1px solid black;">Features</th>
      <th style="width: 35%; text-align: center; font-weight: bold; height: 43px; border: 1px solid black;">User Stories</th>
      <th style="width: 35%; text-align: center; font-weight: bold; height: 43px; border: 1px solid black;">Descrição</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="4" style="text-align: center; writing-mode: vertical-lr; border: 1px solid black;">Ingestão e Pré-processamento dos Dados Financeiros</td>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 1.1: Obtenção de dados financeiros do IPEA</td>
      <td style="border: 1px solid black;">Como desenvolvedor, quero importar arquivos através da API, para poder alimentar o pipeline com dados financeiros do IPEA.</td>
      <td style="border: 1px solid black;">Permite que o pipeline seja alimentado com dados financeiros em tempo real através da API.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como analista, quero que os dados sejam obtidos automaticamente (de fontes como API ou scraping), para garantir atualizações frequentes.</td>
      <td style="border: 1px solid black;">Automatiza a coleta de dados financeiros, garantindo que a base de dados esteja sempre atualizada.</td>
    </tr>
    <tr>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 1.2: Limpeza e preparação dos dados</td>
      <td style="border: 1px solid black;">Como cientista de dados, quero normalizar datas, moedas e categorias, para garantir consistência na análise.</td>
      <td style="border: 1px solid black;">Normaliza dados para garantir a consistência nas análises financeiras.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como desenvolvedor, quero aplicar um pipeline de pré-processamento textual (com remoção de stopwords, normalização e tokenização), para alimentar os modelos de NLP com dados limpos.</td>
      <td style="border: 1px solid black;">Aplique pré-processamento nos dados textuais para alimentar o modelo de NLP com dados limpos e de qualidade.</td>
    </tr>
    <tr>
      <td rowspan="6" style="text-align: center; writing-mode: vertical-lr; border: 1px solid black;">Análise Semântica e Geração de Insights com NLP</td>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 2.1: Extração de tópicos relevantes</td>
      <td style="border: 1px solid black;">Como cientista de dados, quero aplicar o BERTopic nos textos financeiros, para identificar automaticamente os principais tópicos abordados.</td>
      <td style="border: 1px solid black;">Aplica técnicas de NLP para identificar automaticamente os tópicos relevantes nos dados financeiros.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como analista público, quero visualizar os tópicos e exemplos de textos relacionados, para entender melhor as áreas críticas.</td>
      <td style="border: 1px solid black;">Fornece uma visualização dos tópicos financeiros, facilitando a análise de áreas críticas.</td>
    </tr>
    <tr>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 2.2: Geração de resumos automatizados</td>
      <td style="border: 1px solid black;">Como gestor público, quero receber um resumo técnico sobre os dados do mês, para entender rapidamente os principais pontos financeiros.</td>
      <td style="border: 1px solid black;">Gera resumos automatizados para facilitar a compreensão dos dados financeiros pelos gestores.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como desenvolvedor, quero utilizar modelos generativos open-source (ex: T5 ou BART), para gerar resumos a partir dos dados analisados.</td>
      <td style="border: 1px solid black;">Usa modelos de NLP avançados para criar resumos de fácil compreensão a partir dos dados financeiros.</td>
    </tr>
    <tr>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 2.3: Emissão de alertas com base em anomalias</td>
      <td style="border: 1px solid black;">Como gestor, quero receber um alerta automático quando houver aumento anormal em um gasto específico, para tomar decisões corretivas.</td>
      <td style="border: 1px solid black;">Notifica os gestores sobre variações significativas em gastos, ajudando na tomada de decisões corretivas.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como desenvolvedor, quero configurar regras e condições para geração de alertas, para evitar falsos positivos.</td>
      <td style="border: 1px solid black;">Permite a personalização das regras de alerta, evitando notificações desnecessárias.</td>
    </tr>
    <tr>
      <td rowspan="4" style="text-align: center; writing-mode: vertical-lr; border: 1px solid black;">Visualização dos Dados e Relatórios</td>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 3.1: Painel interativo com dados e textos</td>
      <td style="border: 1px solid black;">Como gestor público, quero visualizar os dados e relatórios em uma interface clara, para facilitar a análise e tomada de decisão.</td>
      <td style="border: 1px solid black;">Proporciona uma interface clara e intuitiva para a visualização de dados financeiros.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como usuário, quero interagir com filtros e gráficos no dashboard, para explorar diferentes períodos e categorias.</td>
      <td style="border: 1px solid black;">Permite a interação com gráficos e filtros para uma análise detalhada dos dados financeiros.</td>
    </tr>
    <tr>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 3.2: Exportação e compartilhamento dos relatórios</td>
      <td style="border: 1px solid black;">Como analista, quero exportar os relatórios gerados em formato PDF ou HTML, para enviar por e-mail ou arquivar.</td>
      <td style="border: 1px solid black;">Facilita a exportação dos relatórios para formatos populares, permitindo fácil compartilhamento e arquivamento.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como gestor, quero salvar os relatórios anteriores, para poder acompanhar a evolução dos indicadores.</td>
      <td style="border: 1px solid black;">Permite salvar relatórios anteriores para comparação e análise de tendências ao longo do tempo.</td>
    </tr>
    <tr>
      <td rowspan="4" style="text-align: center; writing-mode: vertical-lr; border: 1px solid black;">Backend e Integração de Componentes</td>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 4.1: Servir dados via API</td>
      <td style="border: 1px solid black;">Como desenvolvedor, quero criar endpoints REST com FastAPI, para que a interface Streamlit acesse os dados e textos gerados dinamicamente.</td>
      <td style="border: 1px solid black;">Cria endpoints dinâmicos para que o Streamlit acesse dados financeiros em tempo real.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como analista, quero poder enviar novos arquivos via API, para manter a base sempre atualizada.</td>
      <td style="border: 1px solid black;">Permite o envio contínuo de dados via API, mantendo o sistema atualizado com novos arquivos financeiros.</td>
    </tr>
    <tr>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 4.2: Orquestração de pipelines</td>
      <td style="border: 1px solid black;">Como administrador do sistema, quero agendar a execução diária do pipeline, para garantir que os dados e relatórios estejam sempre atualizados.</td>
      <td style="border: 1px solid black;">Agendamentos diários para garantir que o pipeline esteja sempre executando e os relatórios atualizados.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como analista, quero ser notificado em caso de erro no processamento, para poder corrigir rapidamente.</td>
      <td style="border: 1px solid black;">Envia notificações para analistas em caso de falhas no processamento, permitindo correções rápidas.</td>
    </tr>
    <tr>
      <td rowspan="4" style="text-align: center; writing-mode: vertical-lr; border: 1px solid black;">Qualidade, Validação e Documentação</td>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 5.1: Testes e validação dos modelos e sistema</td>
      <td style="border: 1px solid black;">Como desenvolvedor, quero escrever testes unitários e de integração, para garantir que o sistema funcione corretamente.</td>
      <td style="border: 1px solid black;">Garantir que o sistema funcione corretamente através de testes automatizados.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como cientista de dados, quero validar a veracidade e qualidade dos relatórios gerados.</td>
      <td style="border: 1px solid black;">Valida a precisão e qualidade dos relatórios financeiros gerados pelo sistema.</td>
    </tr>
    <tr>
      <td rowspan="2" style="text-align: center; border: 1px solid black;">Feature 5.2: Documentação e código aberto</td>
      <td style="border: 1px solid black;">Como colaborador, quero ter uma documentação clara do pipeline e de como rodar o sistema, para facilitar o onboarding.</td>
      <td style="border: 1px solid black;">Cria uma documentação detalhada para novos colaboradores e facilita o onboarding.</td>
    </tr>
    <tr>
      <td style="border: 1px solid black;">Como gestor, quero disponibilizar o projeto como código aberto com licença livre, para que outras instituições públicas possam replicá-lo.</td>
      <td style="border: 1px solid black;">Permite que o código seja disponibilizado como open-source, facilitando a replicação por outras instituições.</td>
    </tr>
  </tbody>
</table>
---

## **Funcionalidades Prioritárias**:
- Integração da API do IPEA.
- Visualização de dados financeiros em gráficos dinâmicos.
- Geração de relatórios automáticos utilizando **LLM**.
- Sistema de alertas financeiros.
---

## 🗺️ Story Map
![Story Map](https://github.com/unb-mds/2025-1-Squad10/blob/main/Documentacao/assets/StoryMap.png?raw=true)

## Diagrama Backlog (Chuva de Ideias)
<a href="https://www.figma.com/team_invite/redeem/JtjJg0xfYUI6RE1FBSzOlM"><img src="../assets/backlog.png" width="100%;" alt="Backlog"/></a>
