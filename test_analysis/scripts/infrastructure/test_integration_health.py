"""
Script de teste simplificado para verificar imports e funcionalidade básica
"""
import sys
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_basic_imports():
    """Testa imports básicos dos serviços"""
    print("🔍 Testando imports básicos...")
    
    try:
        from src.services.search import SearchService
        print("✅ SearchService - OK")
    except ImportError as e:
        print(f"❌ SearchService - {e}")
    
    try:
        from src.services.graph import timeSeries
        print("✅ timeSeries - OK")
    except ImportError as e:
        print(f"❌ timeSeries - {e}")
    
    try:
        from src.services.ia import gerar_relatorio
        print("✅ gerar_relatorio - OK")
    except ImportError as e:
        print(f"❌ gerar_relatorio - {e}")
    
    try:
        from src.services.pdf import gerar_pdf
        print("✅ gerar_pdf - OK")
    except ImportError as e:
        print(f"❌ gerar_pdf - {e}")

def test_fixtures():
    """Testa fixtures dos testes"""
    print("\n🔧 Testando fixtures...")
    
    try:
        from tests.fixtures.test_config import TEST_CONFIG, API_CONFIG
        print("✅ test_config - OK")
        print(f"   Environment: {TEST_CONFIG.get('environment')}")
    except ImportError as e:
        print(f"❌ test_config - {e}")
    
    try:
        from tests.fixtures.mock_data import generate_mock_timeseries_data, MOCK_IA_RESPONSE
        print("✅ mock_data - OK")
        
        # Testar geração de dados
        data = generate_mock_timeseries_data(5)
        print(f"   Generated {len(data)} mock data rows")
        
    except ImportError as e:
        print(f"❌ mock_data - {e}")
    except Exception as e:
        print(f"⚠️ mock_data function error - {e}")

def test_simple_functionality():
    """Testa funcionalidade básica"""
    print("\n🧪 Testando funcionalidade básica...")
    
    try:
        from src.services.search import SearchService
        service = SearchService()
        print("✅ SearchService instanciado")
        
        # Verificar se tem metadados
        if hasattr(service, 'metadata_economicos'):
            if hasattr(service.metadata_economicos, '__len__'):
                print(f"   Metadados disponíveis: {len(service.metadata_economicos)} itens")
            else:
                print("   Metadados: estrutura não reconhecida")
        else:
            print("   Metadados: não encontrados")
            
    except Exception as e:
        print(f"❌ SearchService error - {e}")
    
    try:
        # Testar função de PDF
        from src.services.pdf import gerar_pdf
        print("✅ gerar_pdf importado")
        
        # Não vamos executar realmente para evitar dependências
        
    except Exception as e:
        print(f"❌ gerar_pdf error - {e}")

def test_pytest_compatibility():
    """Testa compatibilidade com pytest"""
    print("\n🎯 Testando compatibilidade com pytest...")
    
    try:
        import pytest
        print("✅ pytest disponível")
        
        # Verificar se consegue encontrar os testes
        import ast
        
        test_files = [
            "tests/integration/test_end_to_end_workflow.py",
            "tests/integration/test_ia_api_integration.py",
            "tests/integration/test_pdf_generation_integration.py",
        ]
        
        working_files = 0
        for test_file in test_files:
            try:
                file_path = Path(test_file)
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                    working_files += 1
                    print(f"   ✅ {test_file} - Sintaxe OK")
                else:
                    print(f"   ❌ {test_file} - Não encontrado")
            except SyntaxError as e:
                print(f"   ❌ {test_file} - Erro de sintaxe: {e}")
            except Exception as e:
                print(f"   ⚠️ {test_file} - {e}")
        
        print(f"\n📊 Arquivos de teste funcionais: {working_files}/{len(test_files)}")
        
    except ImportError:
        print("❌ pytest não disponível")

def main():
    print("🚀 Verificação de Integridade - GovInsights Tests")
    print("=" * 50)
    
    test_basic_imports()
    test_fixtures()
    test_simple_functionality()
    test_pytest_compatibility()
    
    print("\n✅ Verificação concluída!")
    print("\n💡 Para executar os testes:")
    print("   python -m pytest tests/integration/ -v")
    print("   python -m pytest tests/integration/test_pdf_generation_integration.py -v")

if __name__ == "__main__":
    main()
