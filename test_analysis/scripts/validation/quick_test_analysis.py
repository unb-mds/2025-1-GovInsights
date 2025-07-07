"""
Script rápido para validação e verificação de cobertura dos testes de integração.
"""
import ast
import subprocess
import sys
from pathlib import Path
import json
import time

def quick_validation():
    """Validação rápida de todos os arquivos de teste."""
    print("🔍 VALIDAÇÃO RÁPIDA DOS TESTES")
    print("=" * 40)
    
    integration_dir = Path("tests/integration")
    test_files = list(integration_dir.glob("test_*.py"))
    
    results = {
        'total_files': len(test_files),
        'valid_files': 0,
        'total_methods': 0,
        'files_details': {}
    }
    
    for test_file in test_files:
        print(f"\n📁 {test_file.name}:")
        
        try:
            # Verificar sintaxe
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Contar elementos
            test_classes = 0
            test_methods = 0
            mocks = content.count('Mock') + content.count('patch')
            assertions = content.count('assert ')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    test_classes += 1
                elif isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    test_methods += 1
            
            print(f"   ✅ Sintaxe válida")
            print(f"   🧪 {test_classes} classes, {test_methods} métodos")
            print(f"   🎭 {mocks} mocks, {assertions} assertions")
            
            results['valid_files'] += 1
            results['total_methods'] += test_methods
            results['files_details'][test_file.name] = {
                'classes': test_classes,
                'methods': test_methods,
                'mocks': mocks,
                'assertions': assertions,
                'status': 'valid'
            }
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results['files_details'][test_file.name] = {
                'status': 'error',
                'error': str(e)
            }
    
    return results

def check_source_coverage():
    """Verifica quais arquivos fonte estão sendo testados."""
    print(f"\n🎯 COBERTURA DO CÓDIGO FONTE")
    print("=" * 40)
    
    src_dir = Path("src")
    test_dir = Path("tests/integration")
    
    src_files = list(src_dir.rglob("*.py"))
    test_files = list(test_dir.glob("test_*.py"))
    
    coverage_map = {}
    
    # Para cada arquivo fonte, verificar se está sendo testado
    for src_file in src_files:
        relative_path = str(src_file.relative_to(src_dir))
        module_path = relative_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        
        tested_by = []
        
        # Verificar em cada teste se importa este módulo
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Procurar imports
                if f"src.{module_path}" in content or module_path.split('.')[-1] in content:
                    tested_by.append(test_file.name)
                    
            except Exception:
                continue
        
        coverage_map[str(src_file)] = tested_by
    
    # Mostrar resultados
    tested_count = 0
    for src_file, tests in coverage_map.items():
        if tests:
            print(f"✅ {src_file}")
            for test in tests:
                print(f"   📝 {test}")
            tested_count += 1
        else:
            print(f"❌ {src_file} - Não testado")
    
    print(f"\n📊 Resumo: {tested_count}/{len(src_files)} arquivos fonte testados")
    return coverage_map

def run_quick_tests():
    """Executa testes rápidos nos arquivos que funcionam."""
    print(f"\n🧪 EXECUÇÃO RÁPIDA DE TESTES")
    print("=" * 40)
    
    working_tests = [
        "tests/integration/test_end_to_end_workflow.py",
        "tests/integration/test_ipea_search_integration.py"
    ]
    
    results = {}
    
    for test_file in working_tests:
        print(f"\n🔬 Executando {Path(test_file).name}...")
        
        try:
            cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short", "--maxfail=3"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ Sucesso")
                results[test_file] = "passed"
            else:
                print(f"   ⚠️  Problemas (código: {result.returncode})")
                results[test_file] = "failed"
                
            # Extrair estatísticas do output
            output = result.stdout + result.stderr
            lines = output.split('\n')
            for line in lines:
                if "passed" in line and "=" in line:
                    print(f"   📊 {line.strip()}")
                    break
                    
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout")
            results[test_file] = "timeout"
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results[test_file] = "error"
    
    return results

def generate_quick_report():
    """Gera relatório rápido."""
    print(f"\n📋 RELATÓRIO RÁPIDO DE VALIDAÇÃO E COBERTURA")
    print("=" * 60)
    
    # Executar análises
    validation_results = quick_validation()
    coverage_map = check_source_coverage()
    test_results = run_quick_tests()
    
    # Compilar relatório
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'validation': validation_results,
        'coverage_mapping': coverage_map,
        'test_execution': test_results,
        'summary': {
            'total_test_files': validation_results['total_files'],
            'valid_test_files': validation_results['valid_files'],
            'total_test_methods': validation_results['total_methods'],
            'source_files_tested': len([f for f, tests in coverage_map.items() if tests]),
            'total_source_files': len(coverage_map),
            'working_tests': len([t for t, status in test_results.items() if status == "passed"])
        }
    }
    
    # Salvar relatório
    with open('quick_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumo final
    summary = report['summary']
    print(f"\n🎯 RESUMO EXECUTIVO:")
    print(f"   📁 Arquivos de teste válidos: {summary['valid_test_files']}/{summary['total_test_files']}")
    print(f"   🧪 Total de métodos de teste: {summary['total_test_methods']}")
    print(f"   📊 Arquivos fonte testados: {summary['source_files_tested']}/{summary['total_source_files']}")
    print(f"   ✅ Testes funcionando: {summary['working_tests']}")
    
    coverage_percentage = (summary['source_files_tested'] / summary['total_source_files']) * 100
    print(f"   📈 Cobertura estimada: {coverage_percentage:.1f}%")
    
    if summary['valid_test_files'] == summary['total_test_files']:
        print(f"\n🎉 TODOS OS ARQUIVOS DE TESTE ESTÃO VÁLIDOS!")
    
    if coverage_percentage >= 70:
        print(f"🎯 COBERTURA EXCELENTE!")
    elif coverage_percentage >= 50:
        print(f"👍 COBERTURA BOA!")
    else:
        print(f"📈 COBERTURA PODE MELHORAR")
    
    print(f"\n📄 Relatório salvo em: quick_test_report.json")
    return report

if __name__ == "__main__":
    report = generate_quick_report()
