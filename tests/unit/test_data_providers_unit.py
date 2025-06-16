import pytest
import pandas as pd
from src.core.data_providers import (
    get_total_receitas,
    get_total_despesas,
    get_alertas_ativos,
    get_series_temporais,
    get_valor_indicador,
    get_gauge_value
)

def test_get_total_receitas_returns_tuple_and_numbers():
    """Verifica se get_total_receitas retorna uma tupla de dois números."""
    receitas, variacao = get_total_receitas()
    assert isinstance(receitas, (int, float))
    assert isinstance(variacao, (int, float))
    assert receitas >= 0  # Assumindo que receitas não são negativas

def test_get_total_despesas_returns_tuple_and_numbers():
    """Verifica se get_total_despesas retorna uma tupla de dois números."""
    despesas, variacao = get_total_despesas()
    assert isinstance(despesas, (int, float))
    assert isinstance(variacao, (int, float))
    assert despesas >= 0 # Assumindo que despesas não são negativas

def test_get_alertas_ativos_returns_tuple_and_numbers():
    """Verifica se get_alertas_ativos retorna uma tupla de dois números."""
    alertas, variacao = get_alertas_ativos()
    assert isinstance(alertas, int)
    assert isinstance(variacao, (int, float))
    assert alertas >= 0

def test_get_series_temporais_returns_dataframe_with_expected_columns():
    """Verifica se get_series_temporais retorna um DataFrame com colunas e tipos corretos."""
    df = get_series_temporais()
    assert isinstance(df, pd.DataFrame)
    assert "Meses" in df.columns
    assert "Receitas" in df.columns
    assert "Despesas" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["Meses"])
    assert pd.api.types.is_numeric_dtype(df["Receitas"])
    assert pd.api.types.is_numeric_dtype(df["Despesas"])
    assert len(df) == 12 # Esperamos 12 meses

def test_get_valor_indicador_returns_int():
    """Verifica se get_valor_indicador retorna um inteiro."""
    valor = get_valor_indicador()
    assert isinstance(valor, int)

def test_get_gauge_value_returns_int_within_range():
    """Verifica se get_gauge_value retorna um inteiro entre 0 e 100."""
    value = get_gauge_value()
    assert isinstance(value, int)
    assert 0 <= value <= 100