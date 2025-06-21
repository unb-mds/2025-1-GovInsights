import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Importa as funções do seu módulo de lógica de relatórios
# Certifique-se que o caminho está correto para o seu projeto
from src.core.report_logic import get_available_report_periods, process_report_export

# --- Testes para get_available_report_periods ---

def test_get_available_report_periods_default_values():
    """
    Testa a função com valores padrão (iniciando em 2023 por 12 meses)
    e verifica o formato das strings de período.
    """
    # Mocka datetime.now() para ter uma data controlada para o teste
    # Assim, o teste não falha quando o mês/ano atual muda.
    with patch('src.core.report_logic.datetime') as mock_datetime:
        # Define a data atual simulada para este teste
        mock_datetime.now.return_value = datetime(2024, 7, 10)
        # Garante que datetime.fromtimestamp e outras funções funcionem
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)


        periods = get_available_report_periods(start_year=2023, num_months=12)

        expected_periods = [
            "Janeiro 2023", "Fevereiro 2023", "Março 2023", "Abril 2023",
            "Maio 2023", "Junho 2023", "Julho 2023", "Agosto 2023",
            "Setembro 2023", "Outubro 2023", "Novembro 2023", "Dezembro 2023"
        ]
        assert periods == expected_periods
        assert len(periods) == 12

def test_get_available_report_periods_current_month_limit():
    """
    Testa se a função limita os períodos até o mês atual
    quando a quantidade de meses excede o futuro.
    """
    with patch('src.core.report_logic.datetime') as mock_datetime:
        # Define a data atual simulada para este teste
        mock_datetime.now.return_value = datetime(2024, 3, 15)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        periods = get_available_report_periods(start_year=2024, num_months=6)

        # Esperamos apenas Jan, Fev, Mar de 2024
        expected_periods = ["Janeiro 2024", "Fevereiro 2024", "Março 2024"]
        assert periods == expected_periods
        assert len(periods) == 3

def test_get_available_report_periods_custom_start_year_and_months():
    """
    Testa a função com um ano de início e número de meses personalizados.
    """
    with patch('src.core.report_logic.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 5, 1) # Data atual simulada
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        periods = get_available_report_periods(start_year=2024, num_months=5)

        expected_periods = [
            "Janeiro 2024", "Fevereiro 2024", "Março 2024", "Abril 2024", "Maio 2024"
        ]
        assert periods == expected_periods
        assert len(periods) == 5

def test_get_available_report_periods_empty_if_start_year_in_future():
    """
    Testa se a função retorna uma lista vazia se o ano de início estiver no futuro.
    """
    with patch('src.core.report_logic.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        periods = get_available_report_periods(start_year=2024, num_months=12)
        assert periods == []
        assert len(periods) == 0

# --- Testes para process_report_export ---

# Mock para as funções de busca do IPEA que 'process_report_export' pode chamar
# Adaptar o caminho do patch se sua função 'process_report_export' chamar algo de 'ipea_search.py'
# Exemplo: @patch('src.services.ipea_search.organization')
# @patch('src.services.ipea_search.date')
# Se você não chamar funções de 'ipea_search' diretamente em 'process_report_export',
# e sim a lógica de análise de dados, então mockaria essas lógicas.

def test_process_report_export_no_data_types_selected():
    """
    Testa se a função retorna um erro quando nenhum tipo de dado é selecionado.
    """
    result = process_report_export("Maio 2023", "Julho 2023", [], "PDF")
    assert result["status"] == "error"
    assert "Nenhum tipo de dado selecionado." in result["message"]

def test_process_report_export_success_pdf_output():
    """
    Testa um cenário de exportação bem-sucedida para PDF.
    Mocka quaisquer dependências internas para focar na lógica de orquestração.
    """
    # Aqui você mockaria as chamadas internas que 'process_report_export' faria
    # para buscar dados do IPEA ou para gerar o PDF real.
    # Por exemplo:
    # @patch('src.core.report_logic.get_ipea_data_based_on_filters')
    # @patch('src.core.report_logic.generate_pdf_report_content')

    start_period = "Maio 2023"
    end_period = "Julho 2023"
    data_types = ["receitas", "despesas"]
    export_format = "PDF"

    result = process_report_export(start_period, end_period, data_types, export_format)

    assert result["status"] == "success"
    assert "gerado com sucesso!" in result["message"]
    assert result["file_name"] == "relatorio_Maio_2023_a_Julho_2023.pdf"
    assert "Conteúdo simulado do relatório em PDF." in result["content"]
    # Se você mockou chamadas internas, aqui você afirmaria que elas foram chamadas
    # mock_get_ipea_data.assert_called_once()
    # mock_generate_pdf_content.assert_called_once()

def test_process_report_export_success_excel_output():
    """
    Testa um cenário de exportação bem-sucedida para Excel.
    """
    start_period = "Junho 2023"
    end_period = "Agosto 2023"
    data_types = ["alertas"]
    export_format = "Excel"

    result = process_report_export(start_period, end_period, data_types, export_format)

    assert result["status"] == "success"
    assert "gerado com sucesso!" in result["message"]
    assert result["file_name"] == "relatorio_Junho_2023_a_Agosto_2023.xlsx"
    assert "Conteúdo simulado do relatório em Excel." in result["content"]

def test_process_report_export_success_html_output():
    """
    Testa um cenário de exportação bem-sucedida para HTML.
    """
    start_period = "Janeiro 2024"
    end_period = "Fevereiro 2024"
    data_types = ["receitas", "despesas", "alertas"]
    export_format = "HTML"

    result = process_report_export(start_period, end_period, data_types, export_format)

    assert result["status"] == "success"
    assert "gerado com sucesso!" in result["message"]
    assert result["file_name"] == "relatorio_Janeiro_2024_a_Fevereiro_2024.html"
    assert "Conteúdo simulado do relatório em HTML." in result["content"]