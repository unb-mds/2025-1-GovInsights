
# 🛠️ Documentação Técnica  
**Projeto: Relatórios do IPEA**
 
Este documento detalha a arquitetura técnica, ferramentas utilizadas, organização do código e práticas recomendadas para desenvolvimento, manutenção e contribuição no projeto.

---

## **Arquitetura**:
A arquitetura monolítica foi escolhida para facilitar a integração entre o backend e o frontend. A solução utiliza **Python** no backend para servir os dados financeiros, com **Streamlit** como interface interativa. A comunicação com a **API do IPEA** é feita via **requests**, e os dados financeiros são manipulados usando **pandas**.

### **Fluxo de Dados**:
1. O sistema consome dados da **API do IPEA**.
2. O backend processa os dados utilizando **pandas**.
3. O frontend, construído com **Streamlit**, exibe os dados em **gráficos interativos** utilizando **Plotly**.
4. O modelo **Deepseek** é utilizado para gerar relatórios automáticos a partir dos dados financeiros processados.

## **Deploy**:
- **Streamlit Deploy** será usado para hospedar a aplicação web.
- **Git Pages** será utilizado para hospedar a documentação do projeto.

## **Tecnologias**:
- **Python 3.x**, **Streamlit**
- **Deepseek** para geração de relatórios automáticos
- **pandas**, **plotly**, **requests**

## 🧪 Testes e Validação
---

## 💬 Boas Práticas

- Uso de Git Flow para organização de branches
- Commits padronizados (ex: `feat:`, `fix:`, `docs:`)
- Revisões de código via Pull Requests
- Automação de tarefas recorrentes com scripts e CI (opcional)
