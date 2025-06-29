#!/usr/bin/env python3
"""Script para obter resumo rápido dos testes"""

import subprocess
import sys

def run_tests():
    print("Executando testes de integração...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_analysis/integration_tests/", 
            "--tb=no", "--quiet", "--disable-warnings"
        ], capture_output=True, text=True, timeout=60)
        
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print(f"Return code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("Teste expirou após 60 segundos")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    run_tests()
