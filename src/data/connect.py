import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Busca a URL e a Chave a partir das variáveis de ambiente
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# Verifica se as credenciais foram carregadas antes de usá-las
if not url or not key:
    raise ValueError("As credenciais do Supabase (SUPABASE_URL e SUPABASE_KEY) não foram encontradas. Verifique seu arquivo .env.")

# Realiza a conexão com o Supabase de forma segura
supabase: Client = create_client(url, key)

print("✅ Conexão com o Supabase estabelecida com sucesso!")
