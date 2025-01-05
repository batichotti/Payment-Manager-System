import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

# Obter URL e chave do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Criar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
