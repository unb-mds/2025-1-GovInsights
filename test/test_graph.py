import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.services.graph import timeSeries

@pytest.fixture
def fake_dados_serie():
    return pd.DataFrame({
        "RAW DATE": pd.to_datetime(["2020-01-01", "2021-01-01"]),
        "col1": [0, 0],
        "col2": [0, 0],
        "col3": [0, 0],
        "col4": [0, 0],
        "VALUE (R$)": [100, 200]  # coluna de índice 5
    })

@pytest.fixture
def fake_metadata():
    return pd.DataFrame({"MEASURE": ["R$"]})

@patch("src.services.graph.ipea.timeseries")
@patch("src.services.graph.ipea.metadata")
@patch("src.services.graph.ipea.describe")
def test_timeseries_full_flow(mock_describe, mock_metadata, mock_timeseries, fake_dados_serie, fake_metadata):
    # Mock retornos
    mock_timeseries.return_value = fake_dados_serie
    mock_metadata.return_value = fake_metadata
    mock_describe.return_value = "Descrição fake"

    # Instancia a classe
    ts = timeSeries("FAKE_CODE", "Mensal")

    # Testa atributos principais
    assert ts.codigo_serie == "FAKE_CODE"
    assert ts.frequencia == "Mensal"
    assert isinstance(ts.dados_serie, pd.DataFrame)
    assert isinstance(ts.dados_periodos, dict)
    assert isinstance(ts.percentuais, dict)
    assert isinstance(ts.graficos, dict)
    assert ts.descricao == "Descrição fake"

    # Testa cálculo de percentual
    for periodo, valor in ts.percentuais.items():
        # Como os dados são [100, 200], o aumento é 100%
        assert valor == 100.0 or valor is None

    dados = fake_dados_serie
    valor_inicial = dados.iloc[0]["VALUE (R$)"]
    valor_final = dados.iloc[-1]["VALUE (R$)"]