from supabase import create_client, Client

url: str = "https://hwsuespeplkwafkctmjm.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3c3Vlc3BlcGxrd2Fma2N0bWptIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODM3OTA3MiwiZXhwIjoyMDYzOTU1MDcyfQ.YBPGeqwTp32-NnAYcxFmqGPdrHG_juRfRyC04f-EYaQ"
supabase: Client = create_client(url, key) # Realiza a conexão com o Supabase