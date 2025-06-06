# init services
from .ia import gerar_relatorio
from .pdf import gerar_pdf
from .search import obter_dados_serie, search
from .graph import plotar_grafico_periodo, calcular_percentual_aumento_por_periodo


__all__ = ["gerar_relatorio", "gerar_pdf", "obter_dados_serie", "plotar_grafico_periodo", "search", "calcular_percentual_aumento_por_periodo"]