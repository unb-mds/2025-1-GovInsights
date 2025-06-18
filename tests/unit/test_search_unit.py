import pytest
import pandas as pd
from unittest.mock import MagicMock, patch # Para simular a biblioteca ipea

from src.services.search import organization, theme, code, date

# Fixtures para dados simulados de metadados do IPEA 
@pytest.fixture
def mock_ipea_metadata_dataframe():
    """Retorna um DataFrame mockado para ipea.metadata()."""
    data = {
        "CODE": ["ORG001", "ORG002", "THEME001", "CODE001", "DATE001", "DATE002", "DATE003", "DATE004"],
        "MEASURE": ["R$ Receita", "R$ Despesa", "Vendas ($)", "Preço ($)", "Dólar ($)", "Euro ($)", "Cotação ($)", "Impostos (%)"],
        "SOURCE ACRONYM": ["IBGE", "IPEA", "FGV", "BCB", "BCB", "BACEN", "IBGE", "Receita"],
        "SOURCE": ["Instituto Brasileiro de Geografia e Estatística", "Instituto de Pesquisa Econômica Aplicada", "Fundação Getúlio Vargas", "Banco Central do Brasil", "Banco Central do Brasil", "Banco Central do Brasil", "Instituto Brasileiro de Geografia e Estatística", "Receita Federal"],
        "NAME": ["Receita Total", "Despesa Govern. IPEA", "Vendas no Comércio", "Preço do Combustível", "Taxa de Câmbio USD", "Taxa de Câmbio EUR", "Cotação de Ações", "Imposto de Renda"],
        "LAST UPDATE": ["2024-01-15", "2024-02-20", "2023-12-01", "2024-03-10", "2024-04-05", "2024-04-10", "2024-05-01", "2023-11-25"]
    }
    df = pd.DataFrame(data)
    # Garante que 'LAST UPDATE' é datetime para a função date
    df["LAST UPDATE"] = pd.to_datetime(df["LAST UPDATE"])
    return df

@pytest.fixture
def mock_ipea_themes_dataframe():
    """Retorna um DataFrame mockado para ipea.themes()."""
    data = {
        "ID": [1, 2, 3],
        "NAME": ["Economia", "Finanças", "Social"]
    }
    return pd.DataFrame(data)

# Testes para a função 'organization' 
@patch('src.services.search.ipea.metadata') # Substitui ipea.metadata no módulo ipea_search
def test_organization_found_by_acronym(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = organization("IBGE")
    assert not result.empty
    assert "ORG001" in result["CODE"].values
    assert "ORG002" not in result["CODE"].values # Garante que apenas os com $ são retornados

@patch('src.services.search.ipea.metadata')
def test_organization_found_by_source_name(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = organization("Instituto de Pesquisa Econômica Aplicada")
    assert not result.empty
    assert "ORG002" in result["CODE"].values

@patch('src.services.search.ipea.metadata')
def test_organization_not_found(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = organization("OrgaoInexistente")
    assert result == "Não Encontrado"

@patch('src.services.search.ipea.metadata')
def test_organization_no_dollar_measure(mock_metadata, mock_ipea_metadata_dataframe):
    # Mockando para retornar um DataFrame sem séries com "$"
    df_no_dollar = mock_ipea_metadata_dataframe[~mock_ipea_metadata_dataframe["MEASURE"].str.contains("\\$")]
    mock_metadata.return_value = df_no_dollar
    result = organization("Receita") # Tenta buscar algo que não deveria ter $
    assert result == "Não Encontrado" # Pois não há séries com $ para "Receita"

# --- Testes para a função 'theme' ---
@patch('src.services.search.ipea.themes')
@patch('src.services.search.ipea.metadata')
def test_theme_found(mock_metadata, mock_themes, mock_ipea_metadata_dataframe, mock_ipea_themes_dataframe):
    mock_themes.return_value = mock_ipea_themes_dataframe
    # Mocka ipea.metadata para retornar um subconjunto de dados para um theme_id específico
    def mock_metadata_side_effect(**kwargs):
        if kwargs.get('theme_id') == 1: # 'Economia'
            return mock_ipea_metadata_dataframe[mock_ipea_metadata_dataframe['CODE'].isin(["ORG001", "ORG002"])]
        return pd.DataFrame() # Retorna vazio para outros temas
    mock_metadata.side_effect = mock_metadata_side_effect

    result = theme("Economia")
    assert not result.empty
    assert "ORG001" in result["CODE"].values
    assert "ORG002" in result["CODE"].values
    assert "THEME001" not in result["CODE"].values # Não deveria ter, pois não mockamos para theme_id=1

@patch('src.services.search.ipea.themes')
@patch('src.services.search.ipea.metadata')
def test_theme_not_found(mock_metadata, mock_themes, mock_ipea_metadata_dataframe, mock_ipea_themes_dataframe):
    mock_themes.return_value = mock_ipea_themes_dataframe
    mock_metadata.return_value = mock_ipea_metadata_dataframe # Não deve ser chamado se o tema não for encontrado
    
    result = theme("TemaInexistente")
    assert result == "Não Encontrado"
    mock_metadata.assert_not_called() # Garante que metadata não foi chamada se o tema não existe

# Testes para a função 'code' 
@patch('src.services.search.ipea.metadata')
def test_code_found(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = code("ORG001")
    assert not result.empty
    assert "ORG001" in result["CODE"].values
    assert "ORG002" not in result["CODE"].values # Garante filtro exato

@patch('src.services.search.ipea.metadata')
def test_code_not_found(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = code("CODINEXISTENTE")
    assert result == "Não Encontrado"

# Testes para a função 'date' 
@patch('src.services.search.ipea.metadata')
def test_date_with_start_and_end_date(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = date("2024-03-01", "2024-04-15")
    assert not result.empty
    assert "CODE001" in result["CODE"].values # 2024-03-10
    assert "DATE001" in result["CODE"].values # 2024-04-05
    assert "DATE002" in result["CODE"].values # 2024-04-10
    assert "ORG001" not in result["CODE"].values # 2024-01-15

@patch('src.services.search.ipea.metadata')
def test_date_only_start_date(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = date("2024-04-01")
    assert not result.empty
    assert "DATE001" in result["CODE"].values # 2024-04-05
    assert "DATE002" in result["CODE"].values # 2024-04-10
    assert "DATE003" in result["CODE"].values # 2024-05-01
    assert "CODE001" not in result["CODE"].values # 2024-03-10

@patch('src.services.search.ipea.metadata')
def test_date_only_end_date(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = date(data_final="2024-02-29")
    assert not result.empty
    assert "ORG001" in result["CODE"].values # 2024-01-15
    assert "ORG002" in result["CODE"].values # 2024-02-20
    assert "CODE001" not in result["CODE"].values # 2024-03-10

def test_date_raises_error_if_no_dates_provided():
    with pytest.raises(ValueError, match="Data de início e data final não podem ser ambas nulas."):
        date()

@patch('src.services.search.ipea.metadata')
def test_date_no_results(mock_metadata, mock_ipea_metadata_dataframe):
    mock_metadata.return_value = mock_ipea_metadata_dataframe
    result = date("2025-01-01", "2025-01-31")
    assert result.empty # Espera um DataFrame vazio