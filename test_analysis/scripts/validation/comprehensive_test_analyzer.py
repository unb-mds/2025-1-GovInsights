#!/usr/bin/env python3
"""
Script completo para testar todos os arquivos de integração e analisar cobertura.
Executa validação completa, coleta métricas e gera relatório de depuração.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import re

# Adicionar src ao path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root / "src"))

class IntegrationTestAnalyzer:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.integration_dir = self.workspace_root / "tests" / "integration"
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': [],
            'test_results': {},
            'coverage_data': {},
            'errors_found': [],
            'performance_metrics': {},
            'summary': {}
        }
        
    def discover_test_files(self):
        """Descobre todos os arquivos de teste de integração."""
        test_files = list(self.integration_dir.glob("test_*.py"))
        
        print(f"🔍 Descobertos {len(test_files)} arquivos de teste:")
        for file in test_files:
            print(f"  📄 {file.name}")
            self.results['files_analyzed'].append(str(file.relative_to(self.workspace_root)))
            
        return test_files
    
    def validate_syntax(self, test_files):
        """Valida sintaxe Python de todos os arquivos."""
        print("\n🔧 Validando sintaxe dos arquivos...")
        
        syntax_errors = []
        for file_path in test_files:
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'py_compile', str(file_path)
                ], capture_output=True, text=True, cwd=self.workspace_root)
                
                if result.returncode != 0:
                    error_info = {
                        'file': file_path.name,
                        'error': result.stderr.strip(),
                        'type': 'syntax_error'
                    }
                    syntax_errors.append(error_info)
                    print(f"  ❌ {file_path.name}: {result.stderr.strip()}")
                else:
                    print(f"  ✅ {file_path.name}: OK")
                    
            except Exception as e:
                error_info = {
                    'file': file_path.name,
                    'error': str(e),
                    'type': 'validation_exception'
                }
                syntax_errors.append(error_info)
                print(f"  ⚠️ {file_path.name}: {e}")
        
        self.results['errors_found'].extend(syntax_errors)
        return len(syntax_errors) == 0
    
    def run_collection_test(self):
        """Testa se todos os arquivos podem ser coletados pelo pytest."""
        print("\n📋 Testando coleta de testes...")
        
        try:
            start_time = time.time()
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/integration/', '--collect-only', '-q'
            ], capture_output=True, text=True, cwd=self.workspace_root)
            
            collection_time = time.time() - start_time
            
            if result.returncode == 0:
                # Extrair número de testes coletados
                output_lines = result.stdout.strip().split('\n')
                collected_line = [line for line in output_lines if 'collected' in line]
                
                if collected_line:
                    collected_match = re.search(r'(\d+) tests? collected', collected_line[0])
                    tests_count = int(collected_match.group(1)) if collected_match else 0
                else:
                    tests_count = 0
                    
                print(f"  ✅ Coleta bem-sucedida: {tests_count} testes encontrados")
                print(f"  ⏱️ Tempo de coleta: {collection_time:.2f}s")
                
                self.results['test_results']['collection'] = {
                    'success': True,
                    'tests_count': tests_count,
                    'time': collection_time
                }
                
                return True, tests_count
            else:
                print(f"  ❌ Erro na coleta: {result.stderr}")
                self.results['errors_found'].append({
                    'type': 'collection_error',
                    'error': result.stderr.strip()
                })
                return False, 0
                
        except Exception as e:
            print(f"  ⚠️ Exceção na coleta: {e}")
            self.results['errors_found'].append({
                'type': 'collection_exception', 
                'error': str(e)
            })
            return False, 0
    
    def run_individual_test_files(self, test_files):
        """Executa testes individualmente para identificar problemas específicos."""
        print("\n🧪 Executando testes individuais...")
        
        individual_results = {}
        
        for file_path in test_files:
            print(f"\n  📄 Testando {file_path.name}...")
            
            try:
                start_time = time.time()
                result = subprocess.run([
                    sys.executable, '-m', 'pytest', 
                    str(file_path), '-v', '--tb=short'
                ], capture_output=True, text=True, cwd=self.workspace_root)
                
                execution_time = time.time() - start_time
                
                # Analisar resultado
                passed = result.stdout.count(' PASSED')
                failed = result.stdout.count(' FAILED')
                skipped = result.stdout.count(' SKIPPED')
                errors = result.stdout.count(' ERROR')
                
                file_result = {
                    'file': file_path.name,
                    'passed': passed,
                    'failed': failed,
                    'skipped': skipped,
                    'errors': errors,
                    'time': execution_time,
                    'return_code': result.returncode,
                    'success': result.returncode == 0 and failed == 0 and errors == 0
                }
                
                if result.returncode != 0 and failed == 0 and errors == 0:
                    # Possível erro de coleta
                    file_result['collection_error'] = True
                    self.results['errors_found'].append({
                        'file': file_path.name,
                        'type': 'individual_collection_error',
                        'error': result.stderr.strip()
                    })
                
                individual_results[file_path.name] = file_result
                
                # Exibir resultado resumido
                status = "✅" if file_result['success'] else "❌"
                print(f"    {status} P:{passed} F:{failed} S:{skipped} E:{errors} T:{execution_time:.1f}s")
                
                if failed > 0 or errors > 0:
                    print(f"    🔍 Falhas detectadas em {file_path.name}")
                    
            except Exception as e:
                print(f"    ⚠️ Exceção: {e}")
                individual_results[file_path.name] = {
                    'file': file_path.name,
                    'exception': str(e),
                    'success': False
                }
        
        self.results['test_results']['individual'] = individual_results
        return individual_results
    
    def run_coverage_analysis(self):
        """Executa análise de cobertura de código."""
        print("\n📊 Analisando cobertura de código...")
        
        try:
            # Verificar se pytest-cov está disponível
            import pytest_cov
            print("  ✅ pytest-cov disponível")
        except ImportError:
            print("  ⚠️ pytest-cov não encontrado, instalando...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'pytest-cov'
                ], check=True, capture_output=True)
                print("  ✅ pytest-cov instalado")
            except Exception as e:
                print(f"  ❌ Erro ao instalar pytest-cov: {e}")
                return None
        
        try:
            # Executar cobertura
            start_time = time.time()
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                'tests/integration/',
                '--cov=src',
                '--cov-report=term-missing',
                '--cov-report=json:test_analysis/data/coverage/coverage.json',
                '-q'
            ], capture_output=True, text=True, cwd=self.workspace_root)
            
            coverage_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"  ✅ Análise de cobertura concluída em {coverage_time:.2f}s")
                
                # Tentar carregar dados de cobertura
                coverage_file = self.workspace_root / "test_analysis/data/coverage/coverage.json"
                if coverage_file.exists():
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                    print(f"  📈 Cobertura total: {total_coverage:.1f}%")
                    
                    self.results['coverage_data'] = {
                        'total_coverage': total_coverage,
                        'analysis_time': coverage_time,
                        'success': True,
                        'detailed_file': str(coverage_file.relative_to(self.workspace_root))
                    }
                    
                    return coverage_data
                else:
                    print("  ⚠️ Arquivo de cobertura não gerado")
                    
            else:
                print(f"  ❌ Erro na análise de cobertura: {result.stderr}")
                self.results['errors_found'].append({
                    'type': 'coverage_error',
                    'error': result.stderr.strip()
                })
                
        except Exception as e:
            print(f"  ⚠️ Exceção na cobertura: {e}")
            self.results['errors_found'].append({
                'type': 'coverage_exception',
                'error': str(e)
            })
            
        return None
    
    def analyze_skip_patterns(self, test_files):
        """Analisa padrões de SKIPs nos arquivos."""
        print("\n⏭️ Analisando padrões de SKIPs...")
        
        skip_analysis = {}
        total_skips = 0
        
        for file_path in test_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Contar diferentes tipos de SKIPs
                pytest_skips = len(re.findall(r'pytest\.skip\(', content))
                skip_decorators = len(re.findall(r'@pytest\.mark\.skip', content))
                skipif_decorators = len(re.findall(r'@pytest\.mark\.skipif', content))
                
                file_skips = pytest_skips + skip_decorators + skipif_decorators
                total_skips += file_skips
                
                if file_skips > 0:
                    skip_analysis[file_path.name] = {
                        'pytest_skip_calls': pytest_skips,
                        'skip_decorators': skip_decorators,
                        'skipif_decorators': skipif_decorators,
                        'total': file_skips
                    }
                    
                    print(f"  📄 {file_path.name}: {file_skips} SKIPs")
                    
            except Exception as e:
                print(f"  ⚠️ Erro ao analisar {file_path.name}: {e}")
        
        print(f"  📊 Total de SKIPs encontrados: {total_skips}")
        
        self.results['test_results']['skip_analysis'] = {
            'total_skips': total_skips,
            'files_with_skips': len(skip_analysis),
            'detailed': skip_analysis
        }
        
        return skip_analysis
    
    def check_import_dependencies(self, test_files):
        """Verifica dependências de import nos arquivos de teste."""
        print("\n📦 Verificando dependências de import...")
        
        import_analysis = {}
        missing_imports = []
        
        for file_path in test_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrair imports
                import_lines = re.findall(r'^(?:from|import)\s+([^\s]+)', content, re.MULTILINE)
                
                file_imports = []
                file_missing = []
                
                for imp in import_lines:
                    # Limpar import (remover 'import' no final se existir)
                    clean_imp = imp.split('.')[0]
                    
                    # Verificar se é import local ou externo
                    if clean_imp.startswith('src') or clean_imp.startswith('tests'):
                        continue  # Pular imports locais
                    
                    try:
                        __import__(clean_imp)
                        file_imports.append(clean_imp)
                    except ImportError:
                        file_missing.append(clean_imp)
                        missing_imports.append({
                            'file': file_path.name,
                            'import': clean_imp
                        })
                
                if file_missing:
                    import_analysis[file_path.name] = {
                        'available': file_imports,
                        'missing': file_missing
                    }
                    print(f"  📄 {file_path.name}: {len(file_missing)} imports faltando")
                else:
                    print(f"  ✅ {file_path.name}: Todos imports OK")
                    
            except Exception as e:
                print(f"  ⚠️ Erro ao verificar imports em {file_path.name}: {e}")
        
        self.results['test_results']['import_analysis'] = {
            'total_missing': len(missing_imports),
            'files_with_missing': len(import_analysis),
            'detailed': import_analysis
        }
        
        return import_analysis
    
    def generate_comprehensive_report(self):
        """Gera relatório abrangente da análise."""
        print("\n📋 Gerando relatório abrangente...")
        
        # Calcular métricas de resumo
        total_files = len(self.results['files_analyzed'])
        total_errors = len(self.results['errors_found'])
        
        individual_results = self.results['test_results'].get('individual', {})
        total_tests = sum(r.get('passed', 0) + r.get('failed', 0) + r.get('skipped', 0) + r.get('errors', 0) 
                         for r in individual_results.values())
        total_passed = sum(r.get('passed', 0) for r in individual_results.values())
        total_failed = sum(r.get('failed', 0) for r in individual_results.values())
        total_skipped = sum(r.get('skipped', 0) for r in individual_results.values())
        total_errors_in_tests = sum(r.get('errors', 0) for r in individual_results.values())
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        self.results['summary'] = {
            'total_files_analyzed': total_files,
            'total_errors_found': total_errors,
            'total_tests': total_tests,
            'passed_tests': total_passed,
            'failed_tests': total_failed,
            'skipped_tests': total_skipped,
            'error_tests': total_errors_in_tests,
            'success_rate': success_rate,
            'overall_health': 'EXCELLENT' if success_rate >= 95 and total_errors == 0 else
                             'GOOD' if success_rate >= 85 and total_errors <= 2 else
                             'NEEDS_ATTENTION' if success_rate >= 70 else 'CRITICAL'
        }
        
        # Salvar resultados detalhados
        report_file = self.workspace_root / "test_analysis/data/json_reports/comprehensive_test_analysis.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Relatório salvo em: {report_file.relative_to(self.workspace_root)}")
        
        # Gerar relatório markdown
        self.generate_markdown_report()
        
        return self.results
    
    def generate_markdown_report(self):
        """Gera relatório em markdown."""
        summary = self.results['summary']
        coverage_data = self.results.get('coverage_data', {})
        
        # Determinar ícone de saúde
        health_icons = {
            'EXCELLENT': '🟢',
            'GOOD': '🟡', 
            'NEEDS_ATTENTION': '🟠',
            'CRITICAL': '🔴'
        }
        
        health_icon = health_icons.get(summary['overall_health'], '⚪')
        
        report_content = f"""# 🧪 Relatório Completo de Testes de Integração

**Data:** {self.results['timestamp']}  
**Status:** {health_icon} **{summary['overall_health']}**

## 📊 Resumo Executivo

### 🎯 Métricas Principais
| Métrica | Valor | Status |
|---------|-------|--------|
| **Arquivos Analisados** | {summary['total_files_analyzed']} | ✅ |
| **Testes Executados** | {summary['total_tests']} | ✅ |
| **Taxa de Sucesso** | {summary['success_rate']:.1f}% | {health_icon} |
| **Cobertura de Código** | {coverage_data.get('total_coverage', 'N/A')}% | 📈 |
| **Erros Encontrados** | {summary['total_errors_found']} | {'✅' if summary['total_errors_found'] == 0 else '⚠️'} |

### 🧪 Resultados dos Testes
- ✅ **Passou**: {summary['passed_tests']} testes
- ❌ **Falhou**: {summary['failed_tests']} testes  
- ⏭️ **Pulado**: {summary['skipped_tests']} testes
- 🚫 **Erro**: {summary['error_tests']} testes

## 📁 Arquivos Analisados

{chr(10).join(f"- `{file}`" for file in self.results['files_analyzed'])}

## 🔍 Detalhes por Arquivo

"""
        
        # Adicionar resultados individuais
        individual_results = self.results['test_results'].get('individual', {})
        for filename, result in individual_results.items():
            status_icon = "✅" if result.get('success', False) else "❌"
            report_content += f"""### {status_icon} `{filename}`
- **Passou**: {result.get('passed', 0)} | **Falhou**: {result.get('failed', 0)} | **Pulado**: {result.get('skipped', 0)} | **Erro**: {result.get('errors', 0)}
- **Tempo**: {result.get('time', 0):.2f}s
- **Status**: {'Sucesso' if result.get('success', False) else 'Falha'}

"""

        # Adicionar análise de SKIPs
        skip_analysis = self.results['test_results'].get('skip_analysis', {})
        if skip_analysis.get('total_skips', 0) > 0:
            report_content += f"""## ⏭️ Análise de SKIPs

**Total de SKIPs**: {skip_analysis['total_skips']}  
**Arquivos com SKIPs**: {skip_analysis['files_with_skips']}

### Detalhes por Arquivo:
"""
            for filename, details in skip_analysis.get('detailed', {}).items():
                report_content += f"- `{filename}`: {details['total']} SKIPs\n"

        # Adicionar erros se houver
        if self.results['errors_found']:
            report_content += f"""## ⚠️ Erros Encontrados

**Total**: {len(self.results['errors_found'])} erros

"""
            for i, error in enumerate(self.results['errors_found'], 1):
                report_content += f"""### Erro {i}
- **Tipo**: {error.get('type', 'Desconhecido')}
- **Arquivo**: {error.get('file', 'N/A')}
- **Descrição**: {error.get('error', 'N/A')}

"""

        # Adicionar recomendações
        report_content += f"""## 💡 Recomendações

### 🎯 Baseado na Análise:
"""
        
        if summary['overall_health'] == 'EXCELLENT':
            report_content += "- ✅ **Excelente estado!** Continue mantendo a qualidade dos testes\n"
        elif summary['overall_health'] == 'GOOD':
            report_content += "- 🟡 **Bom estado** - Considere corrigir erros menores encontrados\n"
        elif summary['overall_health'] == 'NEEDS_ATTENTION':
            report_content += "- 🟠 **Atenção necessária** - Priorize correção de falhas de teste\n"
        else:
            report_content += "- 🔴 **Estado crítico** - Correções urgentes necessárias\n"

        if summary['failed_tests'] > 0:
            report_content += f"- 🔧 Corrigir {summary['failed_tests']} testes falhando\n"
            
        if summary['skipped_tests'] > 10:
            report_content += f"- ⏭️ Revisar {summary['skipped_tests']} testes pulados (muito alto)\n"
            
        if coverage_data.get('total_coverage', 0) < 80:
            report_content += "- 📈 Melhorar cobertura de código (< 80%)\n"

        report_content += f"""
## 📈 Próximos Passos

1. **Corrigir falhas críticas** identificadas
2. **Melhorar cobertura** de código se necessário  
3. **Revisar SKIPs** excessivos
4. **Manter qualidade** através de execução regular

---

*Relatório gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Salvar relatório markdown
        markdown_file = self.workspace_root / "test_analysis/reports/detailed/COMPREHENSIVE_TEST_REPORT.md"
        markdown_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"  📄 Relatório markdown salvo em: {markdown_file.relative_to(self.workspace_root)}")
    
    def display_summary(self):
        """Exibe resumo final da análise."""
        summary = self.results['summary']
        
        print(f"\n{'='*60}")
        print("🎯 RESUMO FINAL DA ANÁLISE")
        print(f"{'='*60}")
        
        print(f"📊 **MÉTRICAS GERAIS**")
        print(f"   📁 Arquivos: {summary['total_files_analyzed']}")
        print(f"   🧪 Testes: {summary['total_tests']}")
        print(f"   ✅ Passou: {summary['passed_tests']}")
        print(f"   ❌ Falhou: {summary['failed_tests']}")
        print(f"   ⏭️ Pulado: {summary['skipped_tests']}")
        print(f"   💯 Taxa: {summary['success_rate']:.1f}%")
        
        coverage = self.results.get('coverage_data', {}).get('total_coverage')
        if coverage:
            print(f"   📈 Cobertura: {coverage:.1f}%")
        
        print(f"\n🏆 **STATUS GERAL**: {summary['overall_health']}")
        
        if summary['total_errors_found'] > 0:
            print(f"⚠️ **ATENÇÃO**: {summary['total_errors_found']} erros encontrados")
        
        print(f"\n📋 Relatórios detalhados salvos em:")
        print(f"   📄 test_analysis/reports/detailed/COMPREHENSIVE_TEST_REPORT.md")
        print(f"   💾 test_analysis/data/json_reports/comprehensive_test_analysis.json")
    
    def run_complete_analysis(self):
        """Executa análise completa."""
        print("🚀 INICIANDO ANÁLISE COMPLETA DE TESTES DE INTEGRAÇÃO")
        print("="*60)
        
        start_time = time.time()
        
        # 1. Descobrir arquivos
        test_files = self.discover_test_files()
        
        # 2. Validar sintaxe
        syntax_ok = self.validate_syntax(test_files)
        
        # 3. Testar coleta
        collection_ok, tests_count = self.run_collection_test()
        
        # 4. Executar testes individuais
        individual_results = self.run_individual_test_files(test_files)
        
        # 5. Analisar cobertura
        coverage_data = self.run_coverage_analysis()
        
        # 6. Analisar SKIPs
        skip_analysis = self.analyze_skip_patterns(test_files)
        
        # 7. Verificar imports
        import_analysis = self.check_import_dependencies(test_files)
        
        # 8. Gerar relatórios
        self.generate_comprehensive_report()
        
        # 9. Salvar métricas de performance
        total_time = time.time() - start_time
        self.results['performance_metrics'] = {
            'total_analysis_time': total_time,
            'average_time_per_file': total_time / len(test_files) if test_files else 0
        }
        
        # 10. Exibir resumo
        self.display_summary()
        
        print(f"\n⏱️ **ANÁLISE CONCLUÍDA** em {total_time:.2f} segundos")
        
        return self.results

def main():
    """Função principal."""
    print("🔍 ANALISADOR COMPLETO DE TESTES DE INTEGRAÇÃO")
    print("=" * 50)
    
    workspace_root = Path(__file__).parent.parent.parent
    analyzer = IntegrationTestAnalyzer(workspace_root)
    
    results = analyzer.run_complete_analysis()
    
    return results

if __name__ == "__main__":
    main()
