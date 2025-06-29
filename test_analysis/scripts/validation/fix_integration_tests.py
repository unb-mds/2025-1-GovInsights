#!/usr/bin/env python3
"""
Script para corrigir e validar os testes de integração problemas identificados
"""

import subprocess
import sys
import ast
from pathlib import Path

def test_syntax(file_path):
    """Testa sintaxe de um arquivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print(f"✅ {file_path} - Sintaxe válida")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path} - Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {file_path} - Erro: {e}")
        return False

def run_test(test_file, test_method=None):
    """Executa um teste específico"""
    if test_method:
        test_path = f"{test_file}::{test_method}"
    else:
        test_path = test_file
    
    try:
        cmd = [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ {test_path} - PASSOU")
            return True
        else:
            print(f"❌ {test_path} - FALHOU")
            if result.stdout:
                print(f"   Saída: {result.stdout[-200:]}")  # últimas 200 chars
            if result.stderr:
                print(f"   Erro: {result.stderr[-200:]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {test_path} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {test_path} - Erro na execução: {e}")
        return False

def main():
    """Função principal de validação"""
    print("🔧 VALIDAÇÃO E CORREÇÃO DOS TESTES DE INTEGRAÇÃO")
    print("=" * 60)
    
    test_files = [
        "tests/integration/test_database_integration.py",
        "tests/integration/test_search_graph_ia_pipeline.py"
    ]
    
    # 1. Validar sintaxe
    print("\n1️⃣  VALIDAÇÃO DE SINTAXE")
    syntax_ok = True
    for file_path in test_files:
        if not test_syntax(file_path):
            syntax_ok = False
    
    if not syntax_ok:
        print("❌ Problemas de sintaxe encontrados. Corrigir antes de continuar.")
        return 1
    
    # 2. Testar métodos específicos que foram corrigidos
    print("\n2️⃣  TESTE DOS MÉTODOS CORRIGIDOS")
    
    corrected_tests = [
        ("tests/integration/test_database_integration.py", "TestDatabaseIntegration::test_supabase_connection_mock"),
        ("tests/integration/test_database_integration.py", "TestDatabaseIntegration::test_insert_new_series_mock"),
        ("tests/integration/test_search_graph_ia_pipeline.py", "TestSearchGraphIAPipeline::test_basic_search_functionality"),
        ("tests/integration/test_search_graph_ia_pipeline.py", "TestSearchGraphIAPipeline::test_graph_service_integration"),
    ]
    
    passed_tests = 0
    total_tests = len(corrected_tests)
    
    for test_file, test_method in corrected_tests:
        if run_test(test_file, test_method):
            passed_tests += 1
    
    # 3. Resultado final
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO FINAL: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 TODOS OS TESTES CORRIGIDOS PASSARAM!")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} testes ainda precisam de correção")
        return 1

if __name__ == "__main__":
    sys.exit(main())
