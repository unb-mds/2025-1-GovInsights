# init services
from .ia import gerar_relatorio_com_busca_externa_stream
from .pdf import gerar_pdf
from .search import SearchService
from .graph import timeSeries


__all__ = ["gerar_relatorio_com_busca_externa_stream", "gerar_pdf", "obter_dados_serie", "plotar_grafico_periodo", "search", "calcular_percentual_aumento_por_periodo"]