
# **Requisitos do Sistema Gov Insights - Relatórios do IPEA**

## **Requisitos Funcionais**:
1. **Visualização de Dados**: O sistema deve ser capaz de exibir dados financeiros do IPEA em gráficos interativos utilizando **Plotly**.
2. **Geração de Relatórios**: O sistema deve gerar relatórios automáticos baseados em dados financeiros, utilizando o modelo **Deepseek**.
3. **Alertas Automáticos**: O sistema deve ser capaz de notificar os usuários sobre alterações importantes nos dados financeiros.
4. **Integração da API do IPEA**: O sistema deve consumir dados da **API do IPEA** para exibir informações financeiras atualizadas.

## **Requisitos Não Funcionais**:
1. **Escalabilidade**: O sistema deve ser escalável para suportar grandes volumes de dados financeiros.
2. **Desempenho**: O sistema deve carregar os gráficos e gerar os relatórios em tempo hábil para não prejudicar a experiência do usuário.
3. **Segurança**: O sistema deve garantir que as informações dos usuários e dados financeiros estejam protegidos.

## **Tecnologias**:
- **Backend**: **Python 3.x**, **FastAPI**
- **Frontend**: **Streamlit**
- **Modelo de NLP**: **Deepseek**
- **Bibliotecas**: **pandas 2.2.3**, **plotly 6.0.1**, **requests 2.32.3**
- **Deploy**: **Streamlit Deploy**, **Git Pages**
---

## Licenciamento

O projeto será disponibilizado sob a licença **MIT**, permitindo que outras instituições públicas possam replicá-lo, adaptar e distribuir o código conforme necessário.

---

Documento Validado @EricAraujoBsb
