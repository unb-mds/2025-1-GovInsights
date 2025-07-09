import pytest
import pandas as pd
from unittest.mock import patch
from src.core.data_providers import (
    get_total_receitas,
    get_total_despesas, 
    get_alertas_ativos,
    get_series_temporais,
    get_valor_indicador,
    get_gauge_value
)


class TestDataProviders:
    """Testes unitários para os provedores de dados."""

    def test_get_total_receitas(self):
        """Teste da função get_total_receitas."""
        total, variacao = get_total_receitas()
        
        assert isinstance(total, (int, float))
        assert isinstance(variacao, (int, float))
        assert total == 50800
        assert variacao == 28.4

    def test_get_total_despesas(self):
        """Teste da função get_total_despesas."""
        total, variacao = get_total_despesas()
        
        assert isinstance(total, (int, float))
        assert isinstance(variacao, (int, float))
        assert total == 23600
        assert variacao == -12.6

    def test_get_alertas_ativos(self):
        """Teste da função get_alertas_ativos."""
        alertas, variacao = get_alertas_ativos()
        
        assert isinstance(alertas, int)
        assert isinstance(variacao, (int, float))
        assert alertas == 3
        assert variacao == 3.1

    def test_get_series_temporais(self):
        """Teste básico da função get_series_temporais."""
        df = get_series_temporais()
        
        # Verificações básicas
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 12
        assert list(df.columns) == ["Meses", "Receitas", "Despesas"]
        
        # Verificar se as datas estão corretas
        assert df["Meses"].iloc[0].month == 1  # Janeiro
        assert df["Meses"].iloc[0].year == 2023
        assert df["Meses"].iloc[-1].month == 12  # Dezembro

    def test_get_series_temporais_valores_range(self):
        """Teste se get_series_temporais gera valores nos ranges esperados."""
        df = get_series_temporais()
        
        # Verificar se os valores estão nos ranges esperados
        assert all(80 <= valor <= 240 for valor in df["Receitas"])
        assert all(60 <= valor <= 180 for valor in df["Despesas"])

    def test_get_series_temporais_estrutura(self):
        """Teste da estrutura do DataFrame retornado por get_series_temporais."""
        df = get_series_temporais()
        
        # Verificar tipos de dados
        assert pd.api.types.is_datetime64_any_dtype(df["Meses"])
        assert pd.api.types.is_integer_dtype(df["Receitas"])
        assert pd.api.types.is_integer_dtype(df["Despesas"])
        
        # Verificar que não há valores nulos
        assert df.isnull().sum().sum() == 0

    def test_get_valor_indicador(self):
        """Teste da função get_valor_indicador."""
        valor = get_valor_indicador()
        
        assert isinstance(valor, int)
        assert valor == 23648

    def test_get_gauge_value(self):
        """Teste da função get_gauge_value."""
        valor = get_gauge_value()
        
        assert isinstance(valor, int)
        assert valor == 65

    def test_get_series_temporais_datas_sequenciais(self):
        """Teste se as datas em get_series_temporais são sequenciais por mês."""
        df = get_series_temporais()
        
        # Verificar se as datas são sequenciais mês a mês
        for i in range(1, len(df)):
            mes_anterior = df["Meses"].iloc[i-1]
            mes_atual = df["Meses"].iloc[i]
            
            # Verificar se é o próximo mês
            if mes_anterior.month == 12:
                # Se for dezembro, próximo deve ser janeiro do próximo ano
                assert mes_atual.month == 1
                assert mes_atual.year == mes_anterior.year + 1
            else:
                # Senão, deve ser o próximo mês do mesmo ano
                assert mes_atual.month == mes_anterior.month + 1
                assert mes_atual.year == mes_anterior.year

    def test_get_series_temporais_multiplas_execucoes(self):
        """Teste se múltiplas execuções de get_series_temporais geram valores diferentes."""
        df1 = get_series_temporais()
        df2 = get_series_temporais()
        
        # Como usa random, os valores devem ser diferentes (na maioria dos casos)
        # Mas a estrutura deve ser a mesma
        assert df1.shape == df2.shape
        assert list(df1.columns) == list(df2.columns)
        
        # As datas devem ser iguais
        pd.testing.assert_series_equal(df1["Meses"], df2["Meses"])

    def test_get_series_temporais_com_mock_simples(self):
        """Teste get_series_temporais com mock simples do random."""
        with patch('src.core.data_providers.random.randint', return_value=100):
            df = get_series_temporais()
            
            assert len(df) == 12
            assert all(valor == 100 for valor in df["Receitas"])
            assert all(valor == 100 for valor in df["Despesas"])

    def test_todas_funcoes_retornam_valores_validos(self):
        """Teste geral para verificar se todas as funções retornam valores válidos."""
        # Teste get_total_receitas
        receitas_total, receitas_var = get_total_receitas()
        assert receitas_total > 0
        assert isinstance(receitas_var, (int, float))
        
        # Teste get_total_despesas
        despesas_total, despesas_var = get_total_despesas()
        assert despesas_total > 0
        assert isinstance(despesas_var, (int, float))
        
        # Teste get_alertas_ativos
        alertas, alertas_var = get_alertas_ativos()
        assert alertas >= 0
        assert isinstance(alertas_var, (int, float))
        
        # Teste get_series_temporais
        series = get_series_temporais()
        assert not series.empty
        assert len(series.columns) == 3
        
        # Teste get_valor_indicador
        indicador = get_valor_indicador()
        assert isinstance(indicador, int)
        
        # Teste get_gauge_value
        gauge = get_gauge_value()
        assert isinstance(gauge, int)
        assert 0 <= gauge <= 100  # Assumindo que é uma porcentagem
