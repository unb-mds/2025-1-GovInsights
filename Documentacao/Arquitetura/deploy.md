🚀 #Deploy do GovInsights no Streamlit Community Cloud

Este README.md detalha o processo de deploy da aplicação GovInsights no Streamlit Community Cloud. Ele serve como um guia rápido para entender como o aplicativo está rodando em produção, como o DeepSeek é configurado e o que foi feito para o deploy inicial.

#1. Visão Geral do Deploy#
Plataforma Principal: Streamlit Community Cloud
Ambiente: Produção (deploy inicial para testes e feedback).
URL de Acesso: https://<nome_do_seu_app_no_github>-<hash_aleatorio>.streamlit.app/ (Atenção: Preencha o URL final após o deploy bem-sucedido.)
Tecnologias: Python, Streamlit, Plotly, Pandas, integração com DeepSeek AI (via Together.ai).
#2. Preparação do Código para o Deploy#
Para que o GovInsights funcione corretamente no Streamlit Community Cloud, algumas configurações foram aplicadas ao código e ao repositório:

#2.1. Dependências (requirements.txt)#
O que é: Um arquivo que lista todas as bibliotecas Python que o aplicativo precisa para funcionar. O Streamlit Cloud o lê e instala tudo automaticamente.
Ação: O requirements.txt foi gerado/atualizado na raiz do projeto (pip freeze > requirements.txt).
Verificação: Garante que bibliotecas como streamlit, plotly, pandas, together, e outras bibliotecas de IA (ex: transformers, torch) estejam listadas.
#2.2. Chave de API do DeepSeek (src/services/ia.py)#
O que foi feito: Para proteger a chave de API do DeepSeek (usada via Together.ai), ela foi removida do código diretamente e configurada para ser lida de uma variável de ambiente.

Arquivo Modificado: src/services/ia.py

Detalhe da Modificação:

Adicionado import os no início do arquivo.
A linha que usava a chave fixa foi substituída para carregar a chave da variável de ambiente DEEPSEEK_API_KEY:
<!-- end list -->

Python

import os
# ... outras importações ...

def gerar_relatorio(...):
    # ...
    try:
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")

        if not deepseek_api_key:
            raise Exception("Erro: A chave de API do DeepSeek (DEEPSEEK_API_KEY) não foi configurada. Adicione-a nas 'Secrets' do Streamlit Cloud.")

        client = Together(api_key=deepseek_api_key)
        # ... restante do código da função
    except Exception as e:
        raise Exception(f"Conexão com IA falhou: {e}")
#2.3. Autenticação de Usuário (Temporariamente Desativada)#
Situação Atual: A lógica de login/logout baseada em st.user.is_logged_in foi temporariamente desativada/comentada no app.py para facilitar o deploy inicial e o acesso público.
Implicação: O aplicativo está acessível para qualquer pessoa sem a necessidade de login.
Futuro: Se o login for necessário, essa lógica será reativada e credenciais OAuth (ex: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET) serão configuradas como Secrets no Streamlit Cloud.
#2.4. Estrutura de Pastas#
Verificação: A estrutura de pastas foi revisada para garantir que o Streamlit Cloud encontre todos os arquivos importados (como alertas.py, analises.py, src/interface/views/styles/style.css, etc.) em seus caminhos corretos em relação ao app.py.
#2.5. Commit e Push para o GitHub#
Ação: Todas as modificações de código e no requirements.txt foram enviadas para a branch principal (main ou master) do repositório GitHub.
#3. Processo de Deploy (Passo a Passo)#
Para replicar o deploy, siga estes passos:

Acesse o Streamlit Community Cloud: Vá para share.streamlit.io e faça login com sua conta GitHub.
Crie um Novo Aplicativo: No painel, clique em "New app".
Configure o Repositório:
Repository: Selecione o repositório do seu GovInsights.
Branch: Escolha a branch main (ou master).
Main file path: app.py (ou o caminho completo se seu app.py não estiver na raiz, ex: src/interface/views/app.py).
Adicione os Segredos (Secrets):
Expanda "Advanced settings".
Na área "Secrets", adicione a chave do DeepSeek (e outras, se necessário):
DEEPSEEK_API_KEY="SUA_CHAVE_COMPLETA_DO_DEEPSEEK_AQUI"
(Substitua pela chave real)
Inicie o Deploy: Clique no botão "Deploy!".
Monitore: Acompanhe os logs na tela até a mensagem de sucesso.
#4. Verificação Pós-Deploy#
Após o deploy, verifique os seguintes pontos para confirmar o sucesso:

Acessibilidade Pública: A aplicação deve estar acessível pelo URL fornecido pelo Streamlit Community Cloud (https://<nome_do_seu_app>-<hash_aleatorio>.streamlit.app/).
Funcionalidade da IA: Teste as seções do aplicativo que interagem com o DeepSeek para garantir que as respostas da IA estão sendo geradas corretamente.
Acesso a Logs: Em caso de problemas, os logs detalhados podem ser acessados diretamente no painel do Streamlit Community Cloud, na página do aplicativo deployado.
#5. Próximos Passos e Melhorias Futuras#
Este deploy é a versão inicial. Futuras melhorias podem incluir:

Automação CI/CD: Configurar deploys automáticos a cada push no GitHub.
Autenticação de Usuário: Reativar e configurar o sistema de login com credenciais OAuth.
Banco de Dados: Conectar a um banco de dados real e gerenciar suas credenciais.
Domínio Personalizado: Configurar um URL mais amigável (ex: www.govinsights.com.br).
Monitoramento Avançado: Implementar ferramentas de monitoramento mais detalhadas.
Este README está pronto para ser copiado e colado no seu repositório GitHub como README.md (o . final é importante).


