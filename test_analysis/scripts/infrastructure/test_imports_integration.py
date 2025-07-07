#!/usr/bin/env python3
"""
Testes para verificar se os módulos de integração podem ser importados
"""
import os
import sys
import subprocess
import importlib.util
import pytest

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_file_import():
    """Testa se os principais arquivos de integração podem ser importados"""
    integration_files = [
        'test_analysis/integration_tests/test_end_to_end_workflow.py',
        'test_analysis/integration_tests/test_ia_api_integration.py', 
        'test_analysis/integration_tests/test_pdf_generation_integration.py',
        'test_analysis/integration_tests/test_ipea_search_integration.py',
        'test_analysis/integration_tests/test_search_graph_ia_pipeline.py',
        'test_analysis/integration_tests/test_streamlit_backend_integration.py',
        'test_analysis/integration_tests/test_database_integration.py'
    ]
    
    success_count = 0
    
    for filepath in integration_files:
        try:
            if not os.path.exists(filepath):
                continue
                
            spec = importlib.util.spec_from_file_location("test_module", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            success_count += 1
        except Exception as e:
            print(f"Erro ao importar {filepath}: {e}")
    
    # Verificar se pelo menos metade dos arquivos foi importada com sucesso
    assert success_count >= len(integration_files) // 2, f"Muitos arquivos falharam na importação: {success_count}/{len(integration_files)}"

def run_individual_tests(filepath):
    """Executa testes individuais de um arquivo"""
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
