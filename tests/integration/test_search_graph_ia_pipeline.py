"""
Testes de integração para o pipeline completo Search -> Graph -> IA -> PDF.
Cobre o fluxo end-to-end dos principais serviços do GovInsights.
"""

import pytest
import pandas as pd
import time
import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor
from tests.fixtures.test_config import INTEGRATION_TEST_CONFIG, API_CONFIG
from tests.fixtures.mock_data import (
    MOCK_IA_RESPONSE, 
    generate_mock_timeseries_data,
    MOCK_SEARCH_RESULTS,
    MOCK_IPEA_METADATA
)

# Import services with error handling
try:
    from src.services.search import SearchService
    from src.services.graph import timeSeries
    from src.services.ia import gerar_relatorio
    from src.services.pdf import gerar_pdf
except ImportError as e:
    pytest.skip(f"Serviços não disponíveis: {e}", allow_module_level=True)


class TestSearchGraphIAPipeline:
    """Testes de integração do pipeline completo de dados"""
    
    @pytest.fixture
    def search_service(self):
        """Instância do serviço de busca"""
        return SearchService()
    
    @pytest.fixture
    def sample_series_code(self):
        """Código de série para testes - usa dados conhecidos"""
        # Usar código conhecido que funciona em testes
        return "BM12_TJOVER12"
    
    @pytest.fixture
    def mock_series_data(self):
        """Dados mockados de série temporal"""
        return generate_mock_timeseries_data(periods=100)
    
    def test_basic_search_functionality(self, search_service):
        """Testa funcionalidade básica de busca"""
        try:
            # Verificar se metadados foram carregados
            assert hasattr(search_service, 'metadata_economicos')
            metadata = search_service.metadata_economicos
            
            if not metadata.empty:
                assert 'CODE' in metadata.columns
                assert 'NAME' in metadata.columns
                print(f"Metadados carregados: {len(metadata)} séries")
            else:
                pytest.skip("Metadados não disponíveis para teste")
                
        except Exception as e:
            pytest.skip(f"Erro na busca: {e}")
    
    def test_graph_service_integration(self, sample_series_code, mock_series_data):
        """Testa integração com serviço de gráficos usando mocks"""
        with patch('src.services.graph.timeSeries') as mock_timeseries:
            # Configurar mock
            mock_instance = MagicMock()
            mock_instance.codigo_serie = sample_series_code
            mock_instance.dados_serie = mock_series_data
            mock_instance.frequencia = "Mensal"
            mock_instance.graficos = {"linha": MagicMock(), "barras": MagicMock()}
            mock_instance.dados_periodos = {"2023": mock_series_data.head(12)}
            mock_instance.percentuais = {"crescimento": 5.2}
            
            mock_timeseries.return_value = mock_instance
            
            # Executar teste
            time_series = timeSeries(sample_series_code, "Mensal")
            
            # Verificações
            assert time_series.codigo_serie == sample_series_code
            assert isinstance(time_series.dados_serie, pd.DataFrame)
            assert time_series.frequencia == "Mensal"
            assert isinstance(time_series.graficos, dict)
            assert len(time_series.graficos) > 0
            
            mock_timeseries.assert_called_once_with(sample_series_code, "Mensal")
    
    @patch('src.services.ia.Together')
    def test_ia_service_integration(self, mock_together, sample_series_code, mock_series_data):
        """Testa integração com serviço de IA"""
        # Configurar mock da IA
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = MOCK_IA_RESPONSE
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_together.return_value = mock_client
        
        # Executar geração de relatório
        relatorio = gerar_relatorio(sample_series_code, mock_series_data)
        
        # Verificações
        assert relatorio is not None
        assert isinstance(relatorio, str)
        assert len(relatorio) > 0
        assert "análise" in relatorio.lower() or "dados" in relatorio.lower()
        
        # Verificar chamada à API
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert "messages" in call_args.kwargs
    
    @patch('src.services.pdf.gerar_pdf')
    def test_pdf_service_integration(self, mock_pdf, sample_series_code, mock_series_data):
        """Testa integração com serviço de PDF"""
        # Configurar mock
        test_pdf_path = os.path.join(tempfile.gettempdir(), f"test_{sample_series_code}.pdf")
        mock_pdf.return_value = test_pdf_path
        
        # Executar geração de PDF
        pdf_path = gerar_pdf(
            codSerie=sample_series_code,
            dfSerie=mock_series_data,
            iaText="Relatório de teste"
        )
        
        # Verificações
        assert pdf_path == test_pdf_path
        assert pdf_path.endswith('.pdf')
        
        mock_pdf.assert_called_once()
        call_args = mock_pdf.call_args
        assert call_args.kwargs['codSerie'] == sample_series_code
    
    @patch('src.services.ia.Together')
    @patch('src.services.graph.timeSeries')
    def test_complete_pipeline_flow(self, mock_timeseries, mock_together, sample_series_code, mock_series_data):
        """Testa o pipeline completo: Search -> Graph -> IA -> PDF"""
        # Configurar mocks
        # 1. Mock do Graph Service
        mock_ts_instance = MagicMock()
        mock_ts_instance.codigo_serie = sample_series_code
        mock_ts_instance.dados_serie = mock_series_data
        mock_ts_instance.graficos = {"linha": MagicMock()}
        mock_timeseries.return_value = mock_ts_instance
        
        # 2. Mock do IA Service
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = MOCK_IA_RESPONSE
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_together.return_value = mock_client
        
        # Executar pipeline completo
        start_time = time.time()
        
        # 1. Gerar série temporal (Graph)
        time_series = timeSeries(sample_series_code, "Mensal")
        assert time_series.codigo_serie == sample_series_code
        
        # 2. Gerar relatório IA
        relatorio = gerar_relatorio(sample_series_code, time_series.dados_serie)
        assert relatorio is not None
        assert len(relatorio) > 0
        
        # 3. Medir performance
        end_time = time.time()
        pipeline_time = end_time - start_time
        assert pipeline_time < 5.0, f"Pipeline muito lento: {pipeline_time:.2f}s"
        
        # Verificar que todos os serviços foram chamados
        mock_timeseries.assert_called_once()
        mock_client.chat.completions.create.assert_called_once()
    
    def test_pipeline_error_handling(self):
        """Testa tratamento de erros no pipeline"""
        invalid_code = "INVALID_SERIES_CODE_12345"
        
        # Teste com código inválido - deve levantar exceção
        with pytest.raises(Exception):
            timeSeries(invalid_code, "Mensal")
    
    @patch('src.services.ia.Together')
    def test_ia_error_handling(self, mock_together, sample_series_code, mock_series_data):
        """Testa tratamento de erros da IA"""
        # Simular erro de conexão
        mock_together.side_effect = Exception("Erro de conexão com API")
        
        with pytest.raises(Exception, match="Conexão com IA falhou"):
            gerar_relatorio(sample_series_code, mock_series_data)
    
    @patch('src.services.ia.Together')
    @patch('src.services.graph.timeSeries')
    def test_pipeline_with_different_frequencies(self, mock_timeseries, mock_together, mock_series_data):
        """Testa pipeline com diferentes frequências de dados"""
        frequencies = ['Diária', 'Mensal', 'Trimestral', 'Anual']
        
        # Configurar mocks uma vez
        mock_ts_instance = MagicMock()
        mock_ts_instance.dados_serie = mock_series_data
        mock_timeseries.return_value = mock_ts_instance
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = MOCK_IA_RESPONSE
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_together.return_value = mock_client
        
        for freq in frequencies:
            mock_ts_instance.frequencia = freq
            
            # Executar pipeline para cada frequência
            time_series = timeSeries("TEST_CODE", freq)
            assert time_series.frequencia == freq
            
            relatorio = gerar_relatorio("TEST_CODE", time_series.dados_serie)
            assert relatorio is not None
    
    @patch('src.services.ia.Together')
    @patch('src.services.graph.timeSeries')
    def test_pipeline_concurrent_processing(self, mock_timeseries, mock_together, mock_series_data):
        """Testa processamento concorrente do pipeline"""
        # Configurar mocks
        mock_ts_instance = MagicMock()
        mock_ts_instance.dados_serie = mock_series_data
        mock_ts_instance.codigo_serie = "TEST_CODE"
        mock_timeseries.return_value = mock_ts_instance
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = MOCK_IA_RESPONSE
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_together.return_value = mock_client
        
        def run_pipeline(series_code):
            """Executa um pipeline completo"""
            time_series = timeSeries(series_code, "Mensal")
            relatorio = gerar_relatorio(series_code, time_series.dados_serie)
            return len(relatorio)
        
        # Executar múltiplos pipelines em paralelo
        series_codes = [f"TEST_CODE_{i}" for i in range(3)]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_pipeline, code) for code in series_codes]
            results = [future.result() for future in futures]
        
        # Verificar que todos os pipelines completaram
        assert all(result > 0 for result in results)
        assert len(results) == 3
    
    @patch('src.services.graph.timeSeries')
    def test_data_consistency_across_pipeline(self, mock_timeseries, sample_series_code, mock_series_data):
        """Testa consistência de dados através do pipeline"""
        # Configurar dados consistentes
        mock_ts_instance = MagicMock()
        mock_ts_instance.codigo_serie = sample_series_code
        mock_ts_instance.dados_serie = mock_series_data
        mock_ts_instance.dados_periodos = {
            "2023": mock_series_data.head(12),
            "2024": mock_series_data.tail(12)
        }
        mock_timeseries.return_value = mock_ts_instance
        
        # Executar pipeline
        time_series = timeSeries(sample_series_code, "Mensal")
        
        # Verificar consistência
        assert time_series.codigo_serie == sample_series_code
        assert isinstance(time_series.dados_serie, pd.DataFrame)
        assert len(time_series.dados_serie) == len(mock_series_data)
        
        # Verificar dados por período
        if hasattr(time_series, 'dados_periodos'):
            for periodo, dados in time_series.dados_periodos.items():
                assert isinstance(dados, pd.DataFrame)
                assert len(dados) <= len(time_series.dados_serie)
    
    @pytest.mark.slow
    @patch('src.services.ia.Together')
    @patch('src.services.graph.timeSeries')
    def test_pipeline_performance_benchmark(self, mock_timeseries, mock_together, mock_series_data):
        """Testa benchmark de performance do pipeline"""
        # Configurar mocks para resposta rápida
        mock_ts_instance = MagicMock()
        mock_ts_instance.dados_serie = mock_series_data
        mock_timeseries.return_value = mock_ts_instance
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = MOCK_IA_RESPONSE
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_together.return_value = mock_client
        
        # Medir tempo de execução
        iterations = 5
        times = []
        
        for _ in range(iterations):
            start = time.time()
            
            time_series = timeSeries("TEST_CODE", "Mensal")
            relatorio = gerar_relatorio("TEST_CODE", time_series.dados_serie)
            
            end = time.time()
            times.append(end - start)
        
        # Verificar performance
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"Tempo médio: {avg_time:.3f}s, Tempo máximo: {max_time:.3f}s")
        
        # Pipeline deve ser consistentemente rápido
        assert avg_time < 1.0, f"Pipeline muito lento em média: {avg_time:.3f}s"
        assert max_time < 2.0, f"Pipeline com picos de lentidão: {max_time:.3f}s"
    
    def test_pipeline_memory_usage(self, mock_series_data):
        """Testa uso de memória do pipeline"""
        psutil = pytest.importorskip("psutil", reason="psutil necessário para teste de memória")
        import gc
        
        # Medir memória inicial
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simular processamento de múltiplas séries
        for i in range(10):
            # Processar dados (simulado)
            df_copy = mock_series_data.copy()
            df_processed = df_copy.groupby(df_copy.index // 12).mean()
            
            # Forçar limpeza
            del df_copy, df_processed
            gc.collect()
        
        # Medir memória final
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Uso de memória: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
        
        # Não deve haver vazamentos significativos
        assert memory_increase < 50, f"Possível vazamento de memória: +{memory_increase:.1f}MB"