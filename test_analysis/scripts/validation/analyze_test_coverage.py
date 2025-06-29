"""
Script completo para análise de cobertura e validação dos testes de integração.
Verifica a cobertura de código, qualidade dos testes e relatórios detalhados.
"""
import subprocess
import sys
import ast
import json
import time
from pathlib import Path
from collections import defaultdict
import re

class TestCoverageAnalyzer:
    """Analisador de cobertura e validação de testes."""
    
    def __init__(self):
        self.integration_dir = Path("tests/integration")
        self.src_dir = Path("src")
        self.results = {}
        
    def install_coverage_if_needed(self):
        """Instala o coverage se não estiver disponível."""
        try:
            import coverage
            print("📊 Coverage já está instalado")
            return True
        except ImportError:
            print("📦 Instalando coverage...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], 
                             check=True, capture_output=True)
                print("✅ Coverage instalado com sucesso")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao instalar coverage: {e}")
                return False
    
    def analyze_test_coverage(self):
        """Analisa a cobertura dos testes usando coverage.py."""
        print("\n🔍 ANÁLISE DE COBERTURA DOS TESTES")
        print("=" * 50)
        
        if not self.install_coverage_if_needed():
            print("⚠️  Pulando análise de cobertura - coverage não disponível")
            return
        
        # Executar testes com coverage
        test_files = [
            "tests/integration/test_end_to_end_workflow.py",
            "tests/integration/test_ipea_search_integration.py",
            # Adicionar outros arquivos que estão funcionando
        ]
        
        coverage_results = {}
        
        for test_file in test_files:
            print(f"\n🧪 Analisando cobertura de {Path(test_file).name}...")
            
            try:
                # Executar teste com coverage
                cmd = [
                    sys.executable, "-m", "coverage", "run", 
                    "--source=src", "--append", "-m", "pytest", 
                    test_file, "-v", "--tb=short"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
                
                if result.returncode == 0:
                    print(f"   ✅ Teste executado com sucesso")
                    coverage_results[test_file] = "success"
                else:
                    print(f"   ⚠️  Teste com problemas: {result.returncode}")
                    coverage_results[test_file] = "partial"
                
            except Exception as e:
                print(f"   ❌ Erro na execução: {e}")
                coverage_results[test_file] = "error"
        
        # Gerar relatório de cobertura
        try:
            print(f"\n📋 Gerando relatório de cobertura...")
            result = subprocess.run([sys.executable, "-m", "coverage", "report"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Relatório de cobertura gerado:")
                print(result.stdout)
                
                # Salvar relatório em arquivo
                with open("coverage_report.txt", "w", encoding="utf-8") as f:
                    f.write(result.stdout)
                
            else:
                print(f"⚠️  Problema ao gerar relatório: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
        
        return coverage_results
    
    def analyze_test_structure(self):
        """Analisa a estrutura e qualidade dos testes."""
        print("\n🏗️  ANÁLISE DE ESTRUTURA DOS TESTES")
        print("=" * 50)
        
        test_files = list(self.integration_dir.glob("test_*.py"))
        structure_analysis = {}
        
        for test_file in test_files:
            print(f"\n📁 Analisando {test_file.name}:")
            
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                analysis = self._analyze_ast(tree, content)
                
                structure_analysis[test_file.name] = analysis
                
                print(f"   🧪 Classes de teste: {analysis['test_classes']}")
                print(f"   🔬 Métodos de teste: {analysis['test_methods']}")
                print(f"   🎯 Mocks utilizados: {analysis['mocks_count']}")
                print(f"   📊 Assertions: {analysis['assertions_count']}")
                print(f"   🔧 Fixtures: {analysis['fixtures_count']}")
                print(f"   📝 Docstrings: {analysis['docstrings_count']}")
                print(f"   ⚡ Complexidade média: {analysis['avg_complexity']:.1f}")
                
            except Exception as e:
                print(f"   ❌ Erro na análise: {e}")
                structure_analysis[test_file.name] = {"error": str(e)}
        
        return structure_analysis
    
    def _analyze_ast(self, tree, content):
        """Analisa a árvore AST do arquivo de teste."""
        analysis = {
            'test_classes': 0,
            'test_methods': 0,
            'mocks_count': 0,
            'assertions_count': 0,
            'fixtures_count': 0,
            'docstrings_count': 0,
            'avg_complexity': 0,
            'imports': [],
            'test_patterns': []
        }
        
        complexities = []
        
        for node in ast.walk(tree):
            # Classes de teste
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    analysis['test_classes'] += 1
                    if ast.get_docstring(node):
                        analysis['docstrings_count'] += 1
            
            # Métodos de teste
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    analysis['test_methods'] += 1
                    if ast.get_docstring(node):
                        analysis['docstrings_count'] += 1
                    
                    # Calcular complexidade (número de ifs, loops, etc.)
                    complexity = self._calculate_complexity(node)
                    complexities.append(complexity)
                
                # Fixtures
                if hasattr(node, 'decorator_list'):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == 'fixture':
                            analysis['fixtures_count'] += 1
                        elif isinstance(decorator, ast.Attribute) and decorator.attr == 'fixture':
                            analysis['fixtures_count'] += 1
            
            # Imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis['imports'].append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    analysis['imports'].append(node.module)
        
        # Contar mocks e assertions no código fonte
        analysis['mocks_count'] = content.count('Mock') + content.count('patch')
        analysis['assertions_count'] = content.count('assert ')
        
        # Complexidade média
        if complexities:
            analysis['avg_complexity'] = sum(complexities) / len(complexities)
        
        # Padrões de teste identificados
        analysis['test_patterns'] = self._identify_test_patterns(content)
        
        return analysis
    
    def _calculate_complexity(self, node):
        """Calcula a complexidade ciclomática de um método."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _identify_test_patterns(self, content):
        """Identifica padrões de teste no código."""
        patterns = []
        
        if 'patch(' in content:
            patterns.append('Mocking')
        if 'fixture' in content:
            patterns.append('Fixtures')
        if 'parametrize' in content:
            patterns.append('Parametrized Tests')
        if 'setUp' in content or 'setUpClass' in content:
            patterns.append('Setup/Teardown')
        if 'tempfile' in content:
            patterns.append('Temporary Files')
        if 'requests.get' in content:
            patterns.append('HTTP Mocking')
        if 'pandas' in content:
            patterns.append('Data Testing')
        if 'json' in content:
            patterns.append('JSON Testing')
        
        return patterns
    
    def analyze_source_coverage_mapping(self):
        """Analisa qual código fonte está sendo testado."""
        print("\n🎯 MAPEAMENTO DE COBERTURA DO CÓDIGO FONTE")
        print("=" * 50)
        
        src_files = list(self.src_dir.rglob("*.py"))
        test_files = list(self.integration_dir.glob("test_*.py"))
        
        coverage_mapping = {}
        
        for src_file in src_files:
            relative_path = str(src_file.relative_to(Path.cwd()))
            coverage_mapping[relative_path] = {
                'tested_by': [],
                'coverage_level': 'none'
            }
        
        # Verificar quais arquivos fonte são importados nos testes
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Procurar imports do src
                imports = re.findall(r'from src\.([a-zA-Z0-9_.]+) import', content)
                imports.extend(re.findall(r'import src\.([a-zA-Z0-9_.]+)', content))
                
                for imp in imports:
                    # Converter import para caminho de arquivo
                    src_path = f"src/{imp.replace('.', '/')}.py"
                    if src_path in coverage_mapping:
                        coverage_mapping[src_path]['tested_by'].append(test_file.name)
                        coverage_mapping[src_path]['coverage_level'] = 'integration'
                
            except Exception as e:
                print(f"   ⚠️  Erro ao analisar {test_file.name}: {e}")
        
        # Mostrar resultados
        for src_file, info in coverage_mapping.items():
            if info['tested_by']:
                print(f"✅ {src_file}:")
                for test in info['tested_by']:
                    print(f"   📝 Testado por: {test}")
            else:
                print(f"❌ {src_file}: Não testado")
        
        return coverage_mapping
    
    def generate_comprehensive_report(self):
        """Gera relatório completo de cobertura e validação."""
        print("\n📊 GERANDO RELATÓRIO COMPLETO")
        print("=" * 50)
        
        # Executar todas as análises
        coverage_results = self.analyze_test_coverage()
        structure_analysis = self.analyze_test_structure()
        source_mapping = self.analyze_source_coverage_mapping()
        
        # Compilar relatório
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_test_files': len(list(self.integration_dir.glob("test_*.py"))),
                'total_source_files': len(list(self.src_dir.rglob("*.py"))),
                'coverage_results': coverage_results,
                'structure_quality': self._calculate_structure_quality(structure_analysis)
            },
            'structure_analysis': structure_analysis,
            'source_mapping': source_mapping,
            'recommendations': self._generate_recommendations(structure_analysis, source_mapping)
        }
        
        # Salvar relatório
        with open('comprehensive_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório completo salvo em: comprehensive_test_report.json")
        
        # Mostrar resumo
        self._print_summary(report)
        
        return report
    
    def _calculate_structure_quality(self, structure_analysis):
        """Calcula a qualidade da estrutura dos testes."""
        total_methods = 0
        total_docstrings = 0
        total_assertions = 0
        
        for file_analysis in structure_analysis.values():
            if 'error' not in file_analysis:
                total_methods += file_analysis.get('test_methods', 0)
                total_docstrings += file_analysis.get('docstrings_count', 0)
                total_assertions += file_analysis.get('assertions_count', 0)
        
        return {
            'total_test_methods': total_methods,
            'documentation_ratio': total_docstrings / max(total_methods, 1),
            'avg_assertions_per_test': total_assertions / max(total_methods, 1)
        }
    
    def _generate_recommendations(self, structure_analysis, source_mapping):
        """Gera recomendações baseadas na análise."""
        recommendations = []
        
        # Verificar documentação
        low_doc_files = []
        for file, analysis in structure_analysis.items():
            if 'error' not in analysis:
                doc_ratio = analysis['docstrings_count'] / max(analysis['test_methods'], 1)
                if doc_ratio < 0.8:
                    low_doc_files.append(file)
        
        if low_doc_files:
            recommendations.append({
                'type': 'documentation',
                'priority': 'medium',
                'description': f'Adicionar docstrings em: {", ".join(low_doc_files)}'
            })
        
        # Verificar cobertura do código fonte
        untested_files = [f for f, info in source_mapping.items() if not info['tested_by']]
        if untested_files:
            recommendations.append({
                'type': 'coverage',
                'priority': 'high',
                'description': f'Criar testes para: {", ".join(untested_files[:3])}{"..." if len(untested_files) > 3 else ""}'
            })
        
        # Verificar complexidade
        high_complexity_files = []
        for file, analysis in structure_analysis.items():
            if 'error' not in analysis and analysis['avg_complexity'] > 5:
                high_complexity_files.append(file)
        
        if high_complexity_files:
            recommendations.append({
                'type': 'complexity',
                'priority': 'low',
                'description': f'Simplificar testes complexos em: {", ".join(high_complexity_files)}'
            })
        
        return recommendations
    
    def _print_summary(self, report):
        """Imprime resumo do relatório."""
        print(f"\n📋 RESUMO EXECUTIVO")
        print("=" * 50)
        
        summary = report['summary']
        print(f"📁 Arquivos de teste: {summary['total_test_files']}")
        print(f"📁 Arquivos fonte: {summary['total_source_files']}")
        print(f"🧪 Total de métodos de teste: {summary['structure_quality']['total_test_methods']}")
        print(f"📝 Ratio de documentação: {summary['structure_quality']['documentation_ratio']:.1%}")
        print(f"🎯 Assertions por teste: {summary['structure_quality']['avg_assertions_per_test']:.1f}")
        
        recommendations = report['recommendations']
        if recommendations:
            print(f"\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                print(f"   {i}. {priority_emoji.get(rec['priority'], '⚪')} {rec['description']}")
        else:
            print(f"\n✅ Nenhuma recomendação - testes em excelente estado!")

def main():
    """Executa análise completa de cobertura e validação."""
    print("🚀 ANÁLISE COMPLETA DE COBERTURA E VALIDAÇÃO")
    print("=" * 60)
    
    analyzer = TestCoverageAnalyzer()
    report = analyzer.generate_comprehensive_report()
    
    print(f"\n🎉 Análise concluída! Verifique os arquivos gerados:")
    print(f"   📄 comprehensive_test_report.json")
    print(f"   📄 coverage_report.txt (se disponível)")

if __name__ == "__main__":
    main()
