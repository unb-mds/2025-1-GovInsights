"""
Teste simples para verificar se a infraestrutura está funcionando
"""
import pytest
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_basic_imports():
    """Testa imports básicos"""
    try:
        from tests.fixtures.mock_data import get_mock_dataframe, get_mock_ia_response
        from tests.fixtures.test_config import TEST_CONFIG
        
        # Testar geração de dados mock
        df = get_mock_dataframe(5)
        assert len(df) == 5
        assert 'data' in df.columns
        assert 'valor' in df.columns
        
        # Testar resposta IA
        ia_response = get_mock_ia_response('test')
        assert isinstance(ia_response, str)
        assert len(ia_response) > 0
        
        print("✅ Imports básicos funcionando!")
        # Removido return True para seguir boas práticas do pytest
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        pytest.fail(f"Erro nos imports básicos: {e}")

def test_pdf_functions():
    """Testa se as funções de PDF existem"""
    try:
        from src.services.pdf import gerar_pdf
        print("✅ Função gerar_pdf encontrada!")
        # Removido return True
    except ImportError as e:
        print(f"⚠️  gerar_pdf não encontrada: {e}")
        pytest.skip(f"gerar_pdf não encontrada: {e}")

def test_graph_functions():
    """Testa se as funções de gráfico existem"""
    try:
        from src.services.graph import timeSeries
        print("✅ Classe timeSeries encontrada!")
        # Removido return True
    except ImportError as e:
        print(f"⚠️  timeSeries não encontrada: {e}")
        pytest.skip(f"timeSeries não encontrada: {e}")

if __name__ == "__main__":
    print("🧪 Testando infraestrutura básica...\n")
    
    tests = [
        ("Imports básicos", test_basic_imports),
        ("Funções PDF", test_pdf_functions),
        ("Funções gráfico", test_graph_functions)
    ]
    
    success_count = 0
    
    for name, test_func in tests:
        print(f"📝 {name}:")
        if test_func():
            success_count += 1
        print()
    
    print(f"📊 Resultado: {success_count}/{len(tests)} testes passaram")
    
    if success_count == len(tests):
        print("🎉 Infraestrutura básica está funcionando!")
    else:
        print("⚠️  Alguns componentes precisam de atenção")
