#!/usr/bin/env python3
"""
Script para corrigir encoding do arquivo test_ia_api_integration.py
"""

def fix_encoding():
    try:
        # Ler com substituição de caracteres problemáticos
        with open('tests/integration/test_ia_api_integration.py', 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Escrever de volta com encoding limpo
        with open('tests/integration/test_ia_api_integration.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Encoding corrigido com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir encoding: {e}")

if __name__ == "__main__":
    fix_encoding()
