#!/usr/bin/env python3
"""
Script para testar individualmente cada arquivo de integração
"""
import os
import sys
import subprocess
import importlib.util

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_file_import(filepath):
    """Testa se um arquivo pode ser importado sem erros"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def main():
    integration_files = [
        'tests/integration/test_end_to_end_workflow.py',
        'tests/integration/test_ia_api_integration.py', 
        'tests/integration/test_pdf_generation_integration.py',
        'tests/integration/test_ipea_search_integration.py',
        'tests/integration/test_search_graph_ia_pipeline.py',
        'tests/integration/test_streamlit_backend_integration.py',
        'tests/integration/test_database_integration.py'
    ]
    
    print("🧪 Testando importação de arquivos de integração...\n")
    
    success_count = 0
    
    for filepath in integration_files:
        filename = os.path.basename(filepath)
        print(f"📝 {filename}:")
        
        if not os.path.exists(filepath):
            print(f"  ❌ Arquivo não encontrado")
            continue
            
        success, message = test_file_import(filepath)
        
        if success:
            print(f"  ✅ Import OK")
            success_count += 1
        else:
            print(f"  ❌ Erro: {message}")
        
        print()
    
    print(f"\n📊 Resumo: {success_count}/{len(integration_files)} arquivos importados com sucesso")
    
    if success_count == len(integration_files):
        print("🎉 Todos os arquivos de integração estão funcionais!")
    else:
        print("⚠️  Alguns arquivos precisam de correção")

if __name__ == "__main__":
    main()
