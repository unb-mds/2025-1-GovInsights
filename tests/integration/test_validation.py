"""
Teste simples para validar a estrutura dos testes de integração refatorados
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar paths corretos
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_fixtures_import():
    """Testa se os fixtures podem ser importados"""
    try:
        from tests.fixtures.test_config import TEST_CONFIG, API_CONFIG
        from tests.fixtures.mock_data import MOCK_IA_RESPONSE
        
        assert TEST_CONFIG is not None
        assert API_CONFIG is not None
        assert MOCK_IA_RESPONSE is not None
        print("✓ Fixtures importados com sucesso")
        
    except ImportError as e:
        pytest.fail(f"Erro ao importar fixtures: {e}")

def test_integration_structure():
    """Testa se a estrutura de testes de integração está correta"""
    integration_dir = Path(__file__).parent
    
    # Verificar se os arquivos principais existem
    expected_files = [
        "test_end_to_end_workflow.py",
        "test_ia_api_integration.py", 
        "test_pdf_generation_integration.py",
        "test_ipea_search_integration.py",
        "test_search_graph_ia_pipeline.py",
        "test_streamlit_backend_integration.py",
        "test_database_integration.py"
    ]
    
    for file in expected_files:
        file_path = integration_dir / file
        assert file_path.exists(), f"Arquivo {file} não encontrado"
        assert file_path.stat().st_size > 0, f"Arquivo {file} está vazio"
    
    print("✓ Estrutura de testes de integração válida")

def test_mock_data_validity():
    """Testa se os dados mock são válidos"""
    try:
        from tests.fixtures.mock_data import (
            generate_mock_timeseries_data,
            get_mock_search_results,
            MOCK_IPEA_METADATA
        )
        
        # Testar geração de dados mock
        mock_data = generate_mock_timeseries_data(periods=10)
        assert len(mock_data) == 10
        assert 'VALUE' in mock_data.columns  # Padronizado para 'VALUE'
        
        # Testar resultados de busca mock
        search_results = get_mock_search_results()
        assert isinstance(search_results, list)
        assert len(search_results) > 0
        
        # Testar metadados mock
        assert isinstance(MOCK_IPEA_METADATA, list)
        assert len(MOCK_IPEA_METADATA) > 0
        
        print("✓ Dados mock válidos")
        
    except Exception as e:
        pytest.fail(f"Erro ao validar dados mock: {e}")

if __name__ == "__main__":
    test_fixtures_import()
    test_integration_structure()
    test_mock_data_validity()
    print("\n✓ Todos os testes de validação passaram!")
