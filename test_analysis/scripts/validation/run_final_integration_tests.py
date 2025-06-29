"""
Script final para testar todos os arquivos de integração e gerar relatório completo.
"""
import subprocess
import sys
import json
import time
from pathlib import Path

def run_pytest_on_file(file_path):
    """Executa pytest em um arquivo específico e retorna resultado"""
    try:
        cmd = [sys.executable, "-m", "pytest", str(file_path), "-v", "--tb=short", "--maxfail=5"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        
        # Parse simples do resultado
        output = result.stdout + result.stderr
        
        # Extrair estatísticas
        lines = output.split('\n')
        stats_line = ""
        for line in lines:
            if "passed" in line or "failed" in line or "error" in line:
                if "=" in line and any(word in line for word in ["passed", "failed", "error", "skipped"]):
                    stats_line = line
                    break
        
        return {
            'return_code': result.returncode,
            'output': output,
            'stats': stats_line,
            'success': result.returncode == 0
        }
    except Exception as e:
        return {
            'return_code': -1,
            'output': str(e),
            'stats': 'ERROR',
            'success': False
        }

def main():
    """Executa todos os testes de integração e gera relatório final"""
    print("🚀 EXECUÇÃO FINAL DOS TESTES DE INTEGRAÇÃO")
    print("=" * 60)
    
    integration_files = [
        "tests/integration/test_end_to_end_workflow.py",
        "tests/integration/test_ia_api_integration.py",
        "tests/integration/test_pdf_generation_integration.py", 
        "tests/integration/test_ipea_search_integration.py",
        "tests/integration/test_search_graph_ia_pipeline.py",
        "tests/integration/test_streamlit_backend_integration.py",
        "tests/integration/test_database_integration.py"
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    total_errors = 0
    
    for file_path in integration_files:
        file_name = Path(file_path).name
        print(f"\n🧪 Executando {file_name}...")
        
        start_time = time.time()
        result = run_pytest_on_file(file_path)
        end_time = time.time()
        
        duration = end_time - start_time
        
        print(f"   ⏱️  Duração: {duration:.2f}s")
        
        if result['success']:
            print(f"   ✅ SUCESSO")
        else:
            print(f"   ❌ FALHOU (código: {result['return_code']})")
        
        print(f"   📊 {result['stats']}")
        
        # Extrair números de passed/failed do stats
        stats = result['stats']
        if 'passed' in stats:
            import re
            passed_match = re.search(r'(\d+) passed', stats)
            failed_match = re.search(r'(\d+) failed', stats)
            error_match = re.search(r'(\d+) error', stats)
            
            if passed_match:
                total_passed += int(passed_match.group(1))
            if failed_match:
                total_failed += int(failed_match.group(1))
            if error_match:
                total_errors += int(error_match.group(1))
        
        results[file_name] = {
            'success': result['success'],
            'duration': duration,
            'stats': result['stats'],
            'return_code': result['return_code']
        }
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL")
    print("=" * 60)
    
    print(f"📁 Arquivos testados: {len(integration_files)}")
    print(f"✅ Sucessos: {len([r for r in results.values() if r['success']])}")
    print(f"❌ Falhas: {len([r for r in results.values() if not r['success']])}")
    print(f"🧪 Total de testes passando: {total_passed}")
    print(f"💥 Total de testes falhando: {total_failed}")
    print(f"⚠️  Total de erros: {total_errors}")
    
    # Arquivos com problemas
    failed_files = [name for name, result in results.items() if not result['success']]
    if failed_files:
        print(f"\n⚠️  ARQUIVOS COM PROBLEMAS:")
        for file_name in failed_files:
            print(f"   - {file_name}: {results[file_name]['stats']}")
    
    # Status final
    all_success = all(result['success'] for result in results.values())
    if all_success:
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"✨ Suíte de integração está 100% funcional!")
    else:
        print(f"\n⚠️  Alguns testes precisam de atenção")
        success_rate = len([r for r in results.values() if r['success']]) / len(results) * 100
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    
    # Salvar relatório
    with open('final_integration_test_report.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_files': len(integration_files),
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_errors': total_errors,
            'results': results,
            'success_rate': len([r for r in results.values() if r['success']]) / len(results) * 100
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório detalhado salvo em: final_integration_test_report.json")

if __name__ == "__main__":
    main()
