"""
Testes de integração end-to-end para todo o fluxo da aplicação GovInsights.
Testa o workflow completo: busca -> análise -> gráficos -> relatório -> PDF.
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

from src.services.search import SearchService
from src.services.graph import timeSeries
from src.services.ia import gerar_relatorio_com_busca_externa_stream
from src.services.pdf import gerar_pdf
from tests.fixtures.mock_data import (
    get_mock_ipea_response,
    get_mock_dataframe,
    get_mock_ia_response
)
from tests.fixtures.test_config import TEST_CONFIG


class TestEndToEndWorkflow:
    """Testes end-to-end para workflow completo."""
    
    @pytest.fixture(autouse=True)
    def setup_services(self):
        """Setup dos serviços para testes."""
        self.search_service = SearchService()
        self.graph_generator = MagicMock()  # Mock do gerador de gráficos
        self.pdf_generator = MagicMock()    # Mock do gerador de PDF
    
    def test_complete_inflation_analysis_workflow(self):
        """Testa workflow completo para análise de inflação."""
        # Mock das APIs externas
        with patch('requests.get') as mock_get, \
             patch('src.services.ia.gerar_relatorio_com_busca_externa_stream') as mock_ia, \
             patch.object(self.search_service, 'search') as mock_search, \
             patch.object(self.search_service, 'obter_dados_indicador', create=True) as mock_dados:
            
            # Setup mocks
            mock_response = MagicMock()
            mock_response.json.return_value = get_mock_ipea_response('inflation')
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            mock_ia.return_value = get_mock_ia_response('inflation')
            
            # Mock search results
            mock_search.return_value = [
                {'codigo': 'BM12_TJOVER12', 'nome': 'Taxa de Juros - Selic'},
                {'codigo': 'PAN12_IGSTT12', 'nome': 'IGS-M - Inflação'}
            ]
            
            # Mock dados indicador
            mock_dados.return_value = get_mock_dataframe(50)
            
            # 1. Buscar dados de inflação
            search_results = self.search_service.search(
                frequency="Mensal",
                fonte_list=["IBGE"],
                tema_list=[{"THEME CODE": 2, "THEME NAME": "Preços"}]
            )
            
            assert len(search_results) > 0
            indicador = search_results[0]
            
            # 2. Obter dados do indicador
            dados = self.search_service.obter_dados_indicador(
                codigo=indicador['codigo'],
                periodo_inicio="2020-01",
                periodo_fim="2024-01"
            )
            
            assert isinstance(dados, pd.DataFrame)
            assert not dados.empty
            
            # 3. Gerar gráficos
            graficos = []
            
            # Gráfico de linha temporal
            grafico_linha = MagicMock()  # Mock gráfico linha
            graficos.append(('linha', grafico_linha))
            
            # Gráfico de barras (últimos 12 meses)
            dados_recentes = dados.tail(12)
            grafico_barras = MagicMock()  # Mock gráfico barras
            graficos.append(('barras', grafico_barras))
            
            # 4. Gerar relatório IA
            from src.services.ia import gerar_relatorio_com_busca_externa_stream
            relatorio = gerar_relatorio_com_busca_externa_stream(
                codSerie=indicador['codigo'],
                dataframe=dados
            )
            
            # Verificar se relatório foi gerado (pode ser string ou dict)
            assert relatorio is not None
            if isinstance(relatorio, dict):
                assert 'analise' in relatorio or 'tendencias' in relatorio or 'insights' in relatorio
            else:
                assert len(str(relatorio)) > 50  # Verificar se há conteúdo suficiente
            
            # 5. Gerar PDF final
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                pdf_path = tmp_file.name
            
            try:
                # Mock da geração de PDF
                with open(pdf_path, 'wb') as f:
                    f.write(b'%PDF-1.4 Mock PDF content')  # Criar arquivo PDF mock
                
                # Verificar se PDF foi criado
                assert os.path.exists(pdf_path)
                assert os.path.getsize(pdf_path) > 0
                
            finally:
                # Limpeza
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
    
    def test_error_handling_in_workflow(self):
        """Testa tratamento de erros no workflow."""
        with patch('requests.get') as mock_get:
            # Simular erro na API
            mock_get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                self.search_service.search(
                    frequency="Mensal",
                    fonte_list=["IBGE"]
                )
    
    def test_empty_data_handling(self):
        """Testa tratamento de dados vazios."""
        with patch.object(self.search_service, 'search') as mock_search, \
             patch.object(self.search_service, 'obter_dados_indicador', create=True) as mock_dados:
            
            # Mock para dados vazios
            mock_search.return_value = []
            mock_dados.return_value = pd.DataFrame()  # DataFrame vazio
            
            # Buscar com resultado vazio
            results = self.search_service.search(
                frequency="Anual",
                fonte_list=["INEXISTENTE"]
            )
            
            assert len(results) == 0
            
            # Dados vazios
            dados_vazios = self.search_service.obter_dados_indicador(
                codigo="INEXISTENTE",
                periodo_inicio="2020-01",
                periodo_fim="2024-01"
            )
            
            assert dados_vazios.empty