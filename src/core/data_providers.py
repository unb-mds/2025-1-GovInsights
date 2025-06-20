import pandas as pd
import random

def get_total_receitas():
    """Retorna o total de receitas e sua variação percentual."""
    # Em um cenário real, aqui haveria lógica para buscar dados reais
    return 50800, 28.4

def get_total_despesas():
    """Retorna o total de despesas e sua variação percentual."""
    return 23600, -12.6

def get_alertas_ativos():
    """Retorna o número de alertas ativos e sua variação percentual."""
    return 3, 3.1

def get_series_temporais():
    """Gera dados de séries temporais simulados para receitas e despesas."""
    meses = pd.date_range("2023-01-01", periods=12, freq="ME")
    receitas = [random.randint(80, 240) for _ in range(12)]
    despesas = [random.randint(60, 180) for _ in range(12)]
    return pd.DataFrame({"Meses": meses, "Receitas": receitas, "Despesas": despesas})

def get_valor_indicador():
    """Retorna um valor de indicador simulado."""
    return 23648

def get_gauge_value():
    """Retorna um valor para o medidor simulado."""
    return 65