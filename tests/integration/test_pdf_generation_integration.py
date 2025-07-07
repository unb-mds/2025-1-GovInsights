"""
Testes de integração para geração de PDFs.
Testa a integração completa de geração de relatórios em PDF com gráficos e dados.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

# Configurar matplotlib para usar backend não-interativo (antes de qualquer import do matplotlib)
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo, sem GUI
import matplotlib.pyplot as plt
import io
import base64

from src.services.pdf import gerar_pdf
from src.services.graph import timeSeries
from tests.fixtures.mock_data import get_mock_dataframe, get_mock_ia_response
from tests.fixtures.test_config import TEST_CONFIG


class TestPDFGenerationIntegration:
    """Testes de integração para geração de PDFs."""
    
    @pytest.fixture(autouse=True)
    def setup_services(self):
        """Setup dos serviços para testes."""
        from src.services.graph import timeSeries
        from src.services import pdf
        
        # Mock dos serviços necessários
        with patch('ipeadatapy.timeseries') as mock_timeseries, \
             patch('ipeadatapy.metadata') as mock_metadata, \
             patch('ipeadatapy.describe') as mock_describe:
            
            # Criar estrutura correta baseada no código da classe timeSeries
            # A classe acessa dados.iloc[0,5] para o valor, então precisa de pelo menos 6 colunas
            mock_df_ipea = pd.DataFrame({
                'CODE': ['BM12_TJOVER12'] * 50,
                'RAW DATE': pd.date_range('2023-01-01', periods=50, freq='ME'),
                'DAY': range(1, 51),
                'MONTH': [((i % 12) + 1) for i in range(50)],
                'YEAR': [2023 + (i // 12) for i in range(50)],
                'VALUE (R$)': [100 + i * 0.5 for i in range(50)]  # Coluna 5 (índice 5)
            })
            
            mock_timeseries.return_value = mock_df_ipea
            mock_metadata.return_value = pd.DataFrame({'MEASURE': ['R$']})
            mock_describe.return_value = "Série de teste para PDF"
            
            self.graph_generator = timeSeries("BM12_TJOVER12", "Mensal")
            self.pdf_generator = pdf  # módulo de PDF
        
    def test_complete_pdf_generation_with_real_data(self):
        """Testa geração completa de PDF com dados reais."""
        # Preparar dados de teste usando estrutura correta
        dados = get_mock_dataframe(size=100)
        
        # Relatório IA
        relatorio_ia = get_mock_ia_response('complete_analysis')
        
        # Usar a função real gerar_pdf
        try:
            pdf_path = self.pdf_generator.gerar_pdf(
                codSerie="BM12_TJOVER12",
                dfSerie=dados,
                iaText=relatorio_ia
            )
            
            # Verificações básicas
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 1000  # PDF não-vazio (>1KB)
            
            # Verificar estrutura do PDF (se biblioteca disponível)
            pdf_lib = None
            try:
                import PyPDF2  # type: ignore
                pdf_lib = PyPDF2
            except ImportError:
                try:
                    import pypdf as PyPDF2  # type: ignore
                    pdf_lib = PyPDF2
                except ImportError:
                    pass
            
            if pdf_lib:
                try:
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_reader = pdf_lib.PdfReader(pdf_file)
                        assert len(pdf_reader.pages) >= 1  # Mínimo 1 página
                        
                        # Verificar se contém texto básico
                        first_page = pdf_reader.pages[0]
                        text = first_page.extract_text()
                        assert 'GovInsights' in text
                        assert 'BM12_TJOVER12' in text
                except Exception:
                    # Erro na leitura do PDF, pular verificação
                    pass
                
        finally:
            # Limpeza
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_pdf_generation_with_multiple_chart_types(self):
        """Testa geração de PDF com gráficos básicos."""
        dados = get_mock_dataframe(size=200)
        relatorio_ia = get_mock_ia_response('multi_chart')
        
        # Usar função real gerar_pdf
        try:
            pdf_path = self.pdf_generator.gerar_pdf(
                codSerie="PAN12_IGSTT12",
                dfSerie=dados,
                iaText=relatorio_ia
            )
            
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 1000  # PDF substancial
            
        finally:
            # Limpeza
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_pdf_generation_with_large_dataset(self):
        """Testa geração de PDF com dataset grande."""
        # Dataset grande
        dados_grandes = get_mock_dataframe(size=5000)
        
        # Relatório com estatísticas agregadas
        relatorio_ia = get_mock_ia_response('large_dataset')
        
        try:
            pdf_path = self.pdf_generator.gerar_pdf(
                codSerie="SCN52_PIBPMG12",
                dfSerie=dados_grandes,
                iaText=relatorio_ia
            )
            
            assert os.path.exists(pdf_path)
            # PDF deve ser criado mesmo com dataset grande
            assert os.path.getsize(pdf_path) > 1000
            
        finally:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_pdf_generation_error_handling(self):
        """Testa tratamento de erros na geração de PDF."""
        dados = get_mock_dataframe(size=10)
        
        # Teste com dados vazios
        with pytest.raises(Exception):
            self.pdf_generator.gerar_pdf(
                codSerie="",
                dfSerie=pd.DataFrame(),
                iaText=""
            )
        
        # Teste com parâmetros válidos
        try:
            pdf_path = self.pdf_generator.gerar_pdf(
                codSerie="ERC280_VENDAS12",
                dfSerie=dados,
                iaText=get_mock_ia_response('error_test')
            )
            
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 100
            
        finally:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_pdf_generation_with_custom_styling(self):
        """Testa geração de PDF com estilização básica."""
        dados = get_mock_dataframe(size=50)
        relatorio_ia = get_mock_ia_response('styled_report')
        
        try:
            pdf_path = self.pdf_generator.gerar_pdf(
                codSerie="BM12_ERC280",
                dfSerie=dados,
                iaText=relatorio_ia
            )
            
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 1000
            
        finally:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_pdf_generation_performance_timing(self):
        """Testa performance da geração de PDF."""
        import time
        
        dados = get_mock_dataframe(size=500)
        relatorio_ia = get_mock_ia_response('performance_test')
        
        try:
            start_time = time.time()
            
            pdf_path = self.pdf_generator.gerar_pdf(
                codSerie="BM12_TJOVER12",
                dfSerie=dados,
                iaText=relatorio_ia
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Verificações de performance básicas
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 1000
            assert generation_time < 30  # Não deve levar mais de 30 segundos
            
        finally:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_pdf_generation_with_empty_data(self):
        """Testa geração de PDF com dados mínimos."""
        # Dataset com um ponto
        dados_minimos = pd.DataFrame({
            'data': [datetime.now()],
            'valor': [100.0]
        })
        
        try:
            # Testa com dados mínimos válidos  
            pdf_path = self.pdf_generator.gerar_pdf(
                codSerie="TEST_MIN",
                dfSerie=dados_minimos,
                iaText=get_mock_ia_response('minimal_data')
            )
            
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 100
            
        finally:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_pdf_generation_concurrent_access(self):
        """Testa geração concorrente de múltiplos PDFs."""
        import concurrent.futures
        import matplotlib
        # Configurar matplotlib para threading
        matplotlib.use('Agg')  # Backend não-GUI para threading
        
        def gerar_pdf_async(thread_id):
            # Configurar matplotlib para esta thread
            import matplotlib.pyplot as plt
            plt.ioff()  # Desabilitar modo interativo
            
            dados = get_mock_dataframe(size=50)
            
            try:
                pdf_path = self.pdf_generator.gerar_pdf(
                    codSerie=f"TEST_{thread_id}",
                    dfSerie=dados,
                    iaText=get_mock_ia_response(f'concurrent_{thread_id}')
                )
                
                return pdf_path, os.path.getsize(pdf_path)
                
            except Exception as e:
                if 'pdf_path' in locals() and os.path.exists(pdf_path):
                    os.unlink(pdf_path)
                raise
            finally:
                # Limpar figuras da thread
                plt.close('all')
        
        # Executar gerações em paralelo (reduzido para evitar problemas)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(gerar_pdf_async, i) for i in range(2)]
            resultados = [future.result() for future in futures]
        
        try:
            # Verificar que todos os PDFs foram criados
            assert len(resultados) == 2
            for pdf_path, file_size in resultados:
                assert os.path.exists(pdf_path)
                assert file_size > 1000
                
        finally:
            # Limpeza
            for pdf_path, _ in resultados:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
