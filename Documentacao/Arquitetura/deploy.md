🚀 DEPLOY DO GOVINSIGHTS NO STREAMLIT COMMUNITY CLOUD
Este guia detalha o processo de deploy da aplicação GovInsights na plataforma Streamlit Community Cloud. Ele serve como um manual rápido para entender como o aplicativo está rodando em produção, como a integração com a DeepSeek AI é gerenciada e quais foram as etapas cruciais para o deploy inicial.

💡 Visão Geral
Plataforma de Deploy: Streamlit Community Cloud
Ambiente: Produção (configuração inicial para testes e feedback)
Tecnologias Envolvidas:
Python
Streamlit
Plotly
Pandas
Integração com DeepSeek AI (via Together.ai)
URL de Acesso: https://<nome_do_seu_app_no_github>-<hash_aleatorio>.streamlit.app/ (Atenção: Preencha este URL com o link real do seu aplicativo após o deploy.)
1. ⚙️ Preparação do Código para o Deploy
Para garantir que o GovInsights funcione corretamente na nuvem, algumas configurações essenciais foram aplicadas ao código e ao repositório GitHub.

1.1. Dependências Python (requirements.txt)
Função: Este arquivo lista todas as bibliotecas Python que o aplicativo precisa. O Streamlit Cloud lê essa lista e instala tudo automaticamente.
Ação Realizada: O arquivo requirements.txt foi gerado/atualizado na raiz do projeto (usando pip freeze > requirements.txt).
Conteúdo Verificado: Garante que bibliotecas cruciais como streamlit, plotly, pandas, together (para a API DeepSeek), e outras bibliotecas de IA (como transformers, torch) estão presentes.
1.2. Configuração Segura da Chave DeepSeek (src/services/ia.py)
A chave de API do DeepSeek é uma informação sensível e não deve ficar exposta diretamente no código. Para isso, ela é carregada de uma variável de ambiente.

Arquivo Alvo: src/services/ia.py

Alteração Feita:

Adicionada a importação de os: import os no início do arquivo.
A linha que continha a chave fixa foi substituída para carregar a chave de uma variável de ambiente chamada DEEPSEEK_API_KEY:
<!-- end list -->

Python

import os
# ... outras importações ...

def gerar_relatorio(...):
    # ...
    try:
        # Chave lida de forma segura
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")

        if not deepseek_api_key:
            raise Exception("Erro: A chave de API do DeepSeek (DEEPSEEK_API_KEY) não foi configurada. Por favor, adicione-a nas 'Secrets' do Streamlit Cloud.")

        # Usa a chave segura
        client = Together(api_key=deepseek_api_key)
        # ... restante do código da função
    except Exception as e:
        raise Exception(f"Conexão com IA falhou: {e}")
1.3. Lógica de Autenticação de Usuário (app.py)
Status: A lógica de login/logout baseada em st.user.is_logged_in foi temporariamente desativada/comentada no app.py.
Implicação: Para este deploy inicial, o aplicativo é acessível publicamente, sem a necessidade de um login.
Plano Futuro: Se a autenticação for necessária em próximas versões, essa lógica será reativada e credenciais OAuth (ex: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET) serão configuradas como "Secrets" no Streamlit Cloud.
1.4. Estrutura de Pastas e Caminhos
Verificação: A estrutura de pastas do repositório foi ajustada para garantir que todos os arquivos importados (como alertas.py, analises.py, e o arquivo CSS src/interface/views/styles/style.css) sejam encontrados corretamente pelo app.py no ambiente do Streamlit Cloud.
1.5. Commit e Push para o GitHub
Ação: Todas as modificações no código (src/services/ia.py, app.py se alterado) e no requirements.txt foram salvas e enviadas para a branch principal (main ou master) do repositório GitHub.

Comando Exemplo:

Bash

git add .
git commit -m "Prepara GovInsights para deploy no Streamlit Cloud"
git push origin main
2. 🚀 Processo de Deploy (Passo a Passo Guiado)
Para colocar o GovInsights online, siga estas etapas na plataforma Streamlit Community Cloud:

2.1. Acesso à Plataforma
Acesse: share.streamlit.io
Faça login usando sua conta do GitHub.
2.2. Criação do Aplicativo
No painel do Streamlit Community Cloud, clique no botão "New app" (Novo aplicativo) no canto superior direito.
Preencha os campos de configuração do deploy:
Repository: Selecione o repositório do seu projeto GovInsights no GitHub.
Branch: Escolha a branch principal (main ou master) onde o código está pronto.
Main file path: Indique o caminho para o seu arquivo Streamlit principal (provavelmente app.py, ou o caminho completo se estiver em uma subpasta como src/interface/views/app.py).
2.3. Configuração dos Segredos (Secrets)
Esta é uma etapa CRUCIAL para a segurança da chave DeepSeek.

Na mesma página de deploy, expanda a seção "Advanced settings".

Localize a área de "Secrets".

Clique em "Add a new secret" e adicione a chave do DeepSeek no formato:

DEEPSEEK_API_KEY="SUA_CHAVE_COMPLETA_DO_DEEPSEEK_AQUI"
(Importante: Cole sua chave real dentro das aspas.)

2.4. Iniciar o Deploy
Após preencher todas as informações, clique no botão "Deploy!".
Aguarde enquanto o Streamlit Cloud clona seu código, instala as dependências (do requirements.txt) e inicia seu aplicativo. Este processo será visível nos logs na tela.
3. ✅ Verificação Pós-Deploy
Após a conclusão bem-sucedida do deploy, é hora de verificar se tudo está funcionando como esperado:

3.1. Acessibilidade da Aplicação
Verificação: A aplicação GovInsights deve estar acessível publicamente através do URL fornecido pelo Streamlit Community Cloud.
Teste: Abra o URL em diferentes navegadores e dispositivos.
3.2. Funcionalidade da IA (DeepSeek)
Verificação: As funcionalidades que utilizam o DeepSeek (como as "Análises inteligentes") devem estar processando as informações e retornando as respostas da IA corretamente.
Teste: Interaja com essas seções do aplicativo.
3.3. Acesso aos Logs
Local: Em caso de problemas ou para monitoramento, os logs detalhados do aplicativo podem ser acessados diretamente no painel do Streamlit Community Cloud, na página específica do seu aplicativo deployado.
4. 🚀 Próximos Passos e Melhorias Futuras
Este é o deploy inicial do GovInsights. Melhorias e expansões futuras podem incluir:

Automação CI/CD: Configurar deploys automáticos a cada git push para a branch principal do repositório.
Autenticação de Usuário: Reativar e configurar o sistema de login com um provedor OAuth (ex: Google).
Banco de Dados: Implementar a integração com um banco de dados externo real para dados persistentes.
Domínio Personalizado: Configurar um URL mais amigável e personalizado (ex: www.govinsights.com.br).
Monitoramento Avançado: Implementar ferramentas de monitoramento e alertas mais robustos para o ambiente de produção.
