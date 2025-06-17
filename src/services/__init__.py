# init services
from .ia import gerar_relatorio
from .pdf import gerar_pdf
from .search import SearchService
from .graph import timeSeries


__all__ = ["gerar_relatorio", "gerar_pdf", "obter_dados_serie", "plotar_grafico_periodo", "search", "calcular_percentual_aumento_por_periodo"]