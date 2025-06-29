"""
Script para validar todos os arquivos de integração
"""
import ast
import os
import sys
from pathlib import Path

def validate_syntax(file_path):
    """Valida a sintaxe de um arquivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Erro de sintaxe: {e}"
    except Exception as e:
        return False, f"Erro: {e}"

def validate_imports(file_path):
    """Tenta importar o módulo para verificar imports"""
    try:
        # Adicionar caminhos necessários
        sys.path.insert(0, str(Path(__file__).parent.parent))
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        # Obter o nome do módulo
        module_name = file_path.stem.replace('.py', '')
        spec = ast.parse(open(file_path).read())
        
        # Verificar imports básicos
        imports = []
        for node in ast.walk(spec):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return True, imports
    except Exception as e:
        return False, str(e)

def main():
    integration_dir = Path("tests/integration")
    
    test_files = [
        "test_end_to_end_workflow.py",
        "test_ia_api_integration.py", 
        "test_pdf_generation_integration.py",
        "test_ipea_search_integration.py",
        "test_search_graph_ia_pipeline.py",
        "test_streamlit_backend_integration.py",
        "test_database_integration.py"
    ]
    
    print("🔍 Validando arquivos de integração...\n")
    
    results = {}
    
    for test_file in test_files:
        file_path = integration_dir / test_file
        
        print(f"📁 Validando {test_file}:")
        
        # Verificar se arquivo existe
        if not file_path.exists():
            print(f"  ❌ Arquivo não encontrado")
            results[test_file] = {'exists': False}
            continue
        
        # Verificar tamanho do arquivo
        file_size = file_path.stat().st_size
        print(f"  📊 Tamanho: {file_size:,} bytes")
        
        if file_size == 0:
            print(f"  ❌ Arquivo vazio")
            results[test_file] = {'exists': True, 'empty': True}
            continue
        
        # Validar sintaxe
        syntax_ok, syntax_error = validate_syntax(file_path)
        if syntax_ok:
            print(f"  ✅ Sintaxe: OK")
        else:
            print(f"  ❌ Sintaxe: {syntax_error}")
        
        # Validar imports
        imports_ok, imports_info = validate_imports(file_path)
        if imports_ok:
            print(f"  ✅ Imports: {len(imports_info)} módulos")
        else:
            print(f"  ⚠️  Imports: {imports_info}")
        
        # Contar classes e métodos de teste
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            test_classes = 0
            test_methods = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        test_classes += 1
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        test_methods += 1
            
            print(f"  🧪 Classes de teste: {test_classes}")
            print(f"  🔬 Métodos de teste: {test_methods}")
            
            results[test_file] = {
                'exists': True,
                'syntax_ok': syntax_ok,
                'imports_ok': imports_ok,
                'test_classes': test_classes,
                'test_methods': test_methods,
                'file_size': file_size
            }
            
        except Exception as e:
            print(f"  ❌ Erro na análise: {e}")
            results[test_file] = {'exists': True, 'analysis_error': str(e)}
        
        print()
    
    # Resumo
    print("📋 RESUMO DA VALIDAÇÃO:")
    print("=" * 50)
    
    total_files = len(test_files)
    valid_files = 0
    total_test_methods = 0
    
    for file, result in results.items():
        if result.get('syntax_ok') and result.get('test_methods', 0) > 0:
            valid_files += 1
            total_test_methods += result.get('test_methods', 0)
    
    print(f"📊 Arquivos válidos: {valid_files}/{total_files}")
    print(f"🧪 Total de métodos de teste: {total_test_methods}")
    
    if valid_files == total_files:
        print("✅ Todos os arquivos estão válidos!")
    else:
        print("⚠️  Alguns arquivos precisam de atenção")
    
    # Verificar fixtures
    print("\n🔧 Verificando fixtures:")
    fixtures_dir = Path("tests/fixtures")
    
    fixture_files = ["test_config.py", "mock_data.py"]
    for fixture_file in fixture_files:
        fixture_path = fixtures_dir / fixture_file
        if fixture_path.exists():
            syntax_ok, _ = validate_syntax(fixture_path)
            status = "✅" if syntax_ok else "❌"
            print(f"  {status} {fixture_file}")
        else:
            print(f"  ❌ {fixture_file} - Não encontrado")

if __name__ == "__main__":
    main()
