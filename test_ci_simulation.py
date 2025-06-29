#!/usr/bin/env python3
"""
Script para simular ambiente CI e testar se os testes passarão
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_ci_environment():
    """Configura ambiente similar ao CI"""
    print("🔧 Configurando ambiente CI...")
    
    # Configurar matplotlib para headless
    os.environ['MPLBACKEND'] = 'Agg'
    os.environ['DISPLAY'] = ''
    
    # Configurar Python path
    project_root = Path(__file__).parent
    os.environ['PYTHONPATH'] = str(project_root / 'src')
    
    print("✅ Ambiente configurado")

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("📦 Verificando dependências...")
    
    try:
        import pytest
        import matplotlib
        import pandas
        import numpy
        print(f"✅ pytest: {pytest.__version__}")
        print(f"✅ matplotlib: {matplotlib.__version__}")
        print(f"✅ pandas: {pandas.__version__}")
        print(f"✅ numpy: {numpy.__version__}")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False
    
    return True

def test_imports():
    """Testa se todos os imports funcionam"""
    print("🔍 Testando imports...")
    
    try:
        from src.services import pdf, graph, ia, search
        from tests.fixtures import mock_data
        print("✅ Todos os imports funcionando")
        return True
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def run_test_suite(test_path, name, timeout=300):
    """Executa uma suíte de testes com timeout"""
    print(f"\n🧪 Executando {name}...")
    
    cmd = [
        sys.executable, '-m', 'pytest', 
        str(test_path), 
        '-v', '--tb=short', '--no-header'
    ]
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=Path(__file__).parent
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {name} - PASSOU ({duration:.1f}s)")
            return True, duration
        else:
            print(f"❌ {name} - FALHOU ({duration:.1f}s)")
            print("STDOUT:", result.stdout[-500:])  # Últimas 500 chars
            print("STDERR:", result.stderr[-500:])
            return False, duration
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {name} - TIMEOUT após {timeout}s")
        return False, timeout
    except Exception as e:
        print(f"💥 {name} - ERRO: {e}")
        return False, 0

def main():
    """Função principal"""
    print("🚀 SIMULAÇÃO CI/CD - GovInsights")
    print("=" * 50)
    
    # Setup
    setup_ci_environment()
    
    if not check_dependencies():
        print("❌ Dependências faltando - instale requirements.txt")
        return 1
    
    if not test_imports():
        print("❌ Problemas nos imports")
        return 1
    
    # Executar testes
    results = []
    total_time = 0
    
    # 1. Testes unitários (rápidos)
    success, duration = run_test_suite('tests/unit/', 'Testes Unitários', 60)
    results.append(('Unit Tests', success, duration))
    total_time += duration
    
    # 2. Testes de integração novos (organizados)
    success, duration = run_test_suite('test_analysis/integration_tests/', 'Integração (Nova)', 120)
    results.append(('Integration (New)', success, duration))
    total_time += duration
    
    # 3. Testes de integração legados (podem falhar)
    success, duration = run_test_suite('tests/integration/', 'Integração (Legado)', 180)
    results.append(('Integration (Legacy)', success, duration))
    total_time += duration
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO FINAL")
    print("=" * 50)
    
    passed = 0
    for name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:20} {status:8} ({duration:5.1f}s)")
        if success:
            passed += 1
    
    print(f"\nResumo: {passed}/{len(results)} suítes passaram")
    print(f"Tempo total: {total_time:.1f}s")
    
    # Determinar se o CI passaria
    critical_tests = ['Unit Tests', 'Integration (New)']
    critical_passed = all(
        success for name, success, _ in results 
        if name in critical_tests
    )
    
    if critical_passed:
        print("\n🎉 CI PASSARIA! Projeto pronto para deploy")
        return 0
    else:
        print("\n⚠️  CI FALHARIA - Corrigir testes críticos")
        return 1

if __name__ == "__main__":
    exit(main())
