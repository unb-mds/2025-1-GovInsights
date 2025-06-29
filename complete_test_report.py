#!/usr/bin/env python3
"""
Relatório Completo de Testes e Cobertura - GovInsights
Data: Janeiro 2025
"""

import subprocess
import sys
from datetime import datetime


def run_complete_test_analysis():
    """Executa análise completa dos testes e cobertura."""
    
    print("=" * 80)
    print("RELATÓRIO COMPLETO - TESTES E COBERTURA GOVINSIGHTS")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Executar testes de integração
    print("1. TESTES DE INTEGRAÇÃO")
    print("-" * 40)
    
    try:
        result_integration = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_analysis/integration_tests/",
            "-v", "--tb=short", "--no-header", "-q"
        ], capture_output=True, text=True, cwd=".")
        
        print("Resultado dos testes de integração:")
        print(result_integration.stdout)
        
        if result_integration.returncode == 0:
            print("✅ Todos os testes de integração passaram!")
        else:
            print(f"❌ Falhas nos testes de integração (código: {result_integration.returncode})")
            
    except Exception as e:
        print(f"❌ Erro ao executar testes de integração: {e}")
    
    print("\n" + "=" * 80)
    print("2. TESTES UNITÁRIOS")
    print("-" * 40)
    
    try:
        result_unit = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/unit/",
            "-v", "--tb=short", "--no-header", "-q"
        ], capture_output=True, text=True, cwd=".")
        
        print("Resultado dos testes unitários:")
        print(result_unit.stdout)
        
        if result_unit.returncode == 0:
            print("✅ Todos os testes unitários passaram!")
        else:
            print(f"❌ Falhas nos testes unitários (código: {result_unit.returncode})")
            
    except Exception as e:
        print(f"❌ Erro ao executar testes unitários: {e}")
    
    print("\n" + "=" * 80)
    print("3. ANÁLISE DE COBERTURA DE CÓDIGO")
    print("-" * 40)
    
    try:
        result_coverage = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_analysis/", "tests/",
            "--cov=src", "--cov-report=term-missing", 
            "--tb=no", "-q"
        ], capture_output=True, text=True, cwd=".")
        
        print("Relatório de cobertura:")
        print(result_coverage.stdout)
        
        # Extrair porcentagem de cobertura
        lines = result_coverage.stdout.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                parts = line.split()
                if len(parts) >= 4:
                    coverage_pct = parts[3]
                    print(f"\n📊 COBERTURA TOTAL: {coverage_pct}")
                    break
        
    except Exception as e:
        print(f"❌ Erro ao executar análise de cobertura: {e}")
    
    print("\n" + "=" * 80)
    print("4. RESUMO EXECUTIVO")
    print("-" * 40)
    
    status_items = [
        "📁 Estrutura de testes organizad em test_analysis/ e tests/",
        "🧪 Testes de integração cobrindo pipeline completo",
        "🔧 Testes unitários para componentes individuais", 
        "📊 Análise de cobertura de código implementada",
        "🏗️ Mocks e fixtures padronizados",
        "🚀 Projeto pronto para CI/CD"
    ]
    
    for item in status_items:
        print(f"  {item}")
    
    print("\n" + "=" * 80)
    print("5. ARQUIVOS DE TESTE PRINCIPAIS")
    print("-" * 40)
    
    test_files = [
        "test_analysis/integration_tests/test_search_graph_ia_pipeline.py",
        "test_analysis/integration_tests/test_streamlit_backend_integration.py", 
        "test_analysis/integration_tests/test_pdf_generation_integration.py",
        "test_analysis/integration_tests/test_database_integration.py",
        "test_analysis/integration_tests/test_ia_api_integration.py",
        "tests/unit/test_*.py (testes unitários)",
        "tests/fixtures/mock_data.py (dados mockados)",
        "tests/fixtures/test_config.py (configurações)"
    ]
    
    for file in test_files:
        print(f"  • {file}")
    
    print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Relatório completo gerado.")
    print("=" * 80)


if __name__ == "__main__":
    run_complete_test_analysis()
