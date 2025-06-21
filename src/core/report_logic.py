# src/core/report_logic.py
import pandas as pd
from datetime import datetime, timedelta

# Defina os nomes dos meses em português e capitalizados diretamente.
# Isso garante consistência e independência do locale do sistema operacional.
MONTH_NAMES_PT_BR = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

def get_available_report_periods(start_year: int = 2023, num_months: int = 12) -> list[str]:
    """
    Gera uma lista de strings de períodos disponíveis no formato "Mês Ano" em português.
    Os períodos são gerados do 'start_year' até o mês atual (inclusive),
    limitado pelo 'num_months' total.
    """
    today = datetime.now() # Obtém a data e hora atual do sistema
    periods = []
    # Cria uma data de início no primeiro dia do ano desejado (Janeiro, dia 1)
    current_date = datetime(start_year, 1, 1)

    # Itera para gerar os meses
    for _ in range(num_months):
        # Verifica se o 'current_date' já ultrapassou o mês atual do sistema.
        # Isso evita gerar períodos para o futuro.
        if current_date.year > today.year or \
           (current_date.year == today.year and current_date.month > today.month):
            break # Se sim, para o loop

        # Obtém o nome do mês da lista predefinida (0-indexada)
        month_name = MONTH_NAMES_PT_BR[current_date.month - 1] 
        year = current_date.year
        
        # Adiciona o período formatado à lista
        periods.append(f"{month_name} {year}")
        
        # Avança para o próximo mês.
        # Adiciona 32 dias para garantir que sempre passe para o próximo mês,
        # mesmo em meses mais curtos (como Fevereiro).
        current_date += timedelta(days=32)
        # Reseta o dia para o primeiro, garantindo que o cálculo do mês esteja correto.
        current_date = current_date.replace(day=1) 
        
    return periods

def process_report_export(start_period: str, end_period: str, data_types: list[str], export_format: str) -> dict:
    """
    Processa a solicitação de exportação de relatório.
    Esta é uma função placeholder para a lógica real de coleta e geração de dados,
    adaptada para o seu projeto.

    Args:
        start_period (str): Período de início selecionado (ex: "Maio 2023").
        end_period (str): Período de fim selecionado.
        data_types (list[str]): Tipos de dados selecionados (ex: ["receitas", "despesas"]).
        export_format (str): Formato de exportação (ex: "PDF", "Excel", "HTML").

    Returns:
        dict: Um dicionário contendo informações sobre o relatório gerado ou um erro.
              Em um cenário real, retornaria o caminho do arquivo, bytes do arquivo, etc.
    """
    # Lógica de validação inicial: verifica se algum tipo de dado foi selecionado.
    if not data_types:
        return {"status": "error", "message": "Nenhum tipo de dado selecionado."}

    # Mapeia formatos de exportação recebidos da UI para as extensões de arquivo corretas.
    extension_map = {
        "pdf": "pdf",
        "excel": "xlsx", # Corrigido para a extensão padrão do Excel
        "html": "html"
    }
    # Obtém a extensão correta do mapa. Se o formato não for reconhecido, usa 'txt' como fallback.
    extension = extension_map.get(export_format.lower(), "txt") 
    
    # Constrói o nome do arquivo, substituindo espaços nos períodos por underscores para nomes de arquivo válidos.
    file_name = f"relatorio_{start_period.replace(' ', '_')}_a_{end_period.replace(' ', '_')}.{extension}"

    # Simula a geração do relatório (em um projeto real, aqui haveria a lógica para buscar dados,
    # processá-los e gerar o conteúdo do relatório no formato especificado).
    print(f"Gerando relatório de {start_period} a {end_period} para {data_types} em formato {export_format}...")
    
    # Retorna um dicionário com o status e informações simuladas do relatório gerado.
    return {
        "status": "success",
        "message": f"Relatório '{file_name}' gerado com sucesso!",
        "file_name": file_name,
        "content": f"Conteúdo simulado do relatório em {export_format}." # Conteúdo simulado para fins de teste
    }