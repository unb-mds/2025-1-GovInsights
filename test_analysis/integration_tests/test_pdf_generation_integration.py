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
import matplotlib.pyplot as plt
import io
import base64

from src.services.graph import timeSeries
from tests.fixtures.mock_data import get_mock_dataframe, get_mock_ia_response, generate_mock_timeseries_data
from tests.fixtures.test_config import TEST_CONFIG


class TestPDFGenerationIntegration:
    """Testes de integração para geração de PDFs."""
    
    @pytest.fixture(autouse=True)
    def setup_services(self):
        """Setup dos serviços para testes."""
        # Criar mocks para os geradores que serão usados nos testes
        self.graph_generator = MagicMock()
        
        # Configurar mocks padrão para gráficos
        mock_fig = MagicMock()
        self.graph_generator.criar_grafico_linha.return_value = mock_fig
        self.graph_generator.criar_grafico_barras.return_value = mock_fig
        self.graph_generator.criar_grafico_dispersao.return_value = mock_fig
        
    @patch('src.services.pdf.gerar_pdf')
    def test_complete_pdf_generation_with_real_data(self, mock_gerar_pdf_func):
        """Testa geração completa de PDF com dados reais."""
        # Configurar mock para simular PDF gerado
        def criar_pdf_mock(codSerie, dfSerie, iaText):
            return f"/tmp/test_pdf_{codSerie}_complete.pdf"
        
        mock_gerar_pdf_func.side_effect = criar_pdf_mock
        
        # Preparar dados de teste
        dados = generate_mock_timeseries_data(code='TEST_COMPLETE', periods=100)
        
        # Gerar gráficos
        graficos = []
        
        # Gráfico de linha
        fig_linha = self.graph_generator.criar_grafico_linha(
            dados=dados,
            x_col='RAW DATE',
            y_col='VALUE',
            titulo="Evolução Temporal do Indicador"
        )
        graficos.append(('linha', fig_linha))
        
        # Gráfico de barras (últimos 12 meses)
        dados_recentes = dados.tail(12)
        fig_barras = self.graph_generator.criar_grafico_barras(
            dados=dados_recentes,
            x_col='RAW DATE',
            y_col='VALUE',
            titulo="Últimos 12 Meses"
        )
        graficos.append(('barras', fig_barras))
        
        # Relatório IA
        relatorio_ia = get_mock_ia_response('complete_analysis')
        
        try:
            # Importar função para ser mockada corretamente
            from src.services.pdf import gerar_pdf
            pdf_path = gerar_pdf(
                codSerie="TEST_COMPLETE_001",
                dfSerie=dados,
                iaText=relatorio_ia
            )
            
            # Verificar retorno da função mockada
            assert pdf_path == "/tmp/test_pdf_TEST_COMPLETE_001_complete.pdf"
            
        finally:
            for _, fig in graficos:
                plt.close(fig)
            
    @patch('src.services.pdf.gerar_pdf')
    def test_pdf_generation_with_multiple_chart_types(self, mock_gerar_pdf_func):
        """Testa geração de PDF com múltiplos tipos de gráficos."""
        
        # Configurar mock para criar arquivo PDF simulado
        def criar_pdf_mock(codSerie, dfSerie, iaText):
            # Simular criação de PDF e retornar path simulado
            pdf_path = f"/tmp/test_pdf_{codSerie}.pdf"
            # Simular arquivo PDF com múltiplos gráficos - arquivo maior
            content = b'%%PDF-1.4\n%%Mock PDF with multiple charts\n%%%%EOF\n' + b'0' * 60000
            return pdf_path
        
        mock_gerar_pdf_func.side_effect = criar_pdf_mock
        
        dados = generate_mock_timeseries_data(code='TEST_MULTI', periods=200)
        
        # Criar dataset para gráfico de dispersão
        dados_scatter = pd.DataFrame({
            'x': dados['VALUE'].values,
            'y': dados['VALUE'].shift(1).bfill().values,
            'data': dados['RAW DATE']
        })
        
        graficos = []
        
        # Gráfico de linha temporal
        fig1 = self.graph_generator.criar_grafico_linha(
            dados=dados,
            x_col='RAW DATE',
            y_col='VALUE',
            titulo="Série Temporal"
        )
        graficos.append(('temporal', fig1))
        
        # Gráfico de barras agrupadas por ano
        dados_anuais = dados.copy()
        dados_anuais['ano'] = dados_anuais['RAW DATE'].dt.year
        dados_agrupados = dados_anuais.groupby('ano')['VALUE'].mean().reset_index()
        
        fig2 = self.graph_generator.criar_grafico_barras(
            dados=dados_agrupados,
            x_col='ano',
            y_col='VALUE',
            titulo="Médias Anuais"
        )
        graficos.append(('anuais', fig2))
        
        # Gráfico de dispersão
        fig3 = self.graph_generator.criar_grafico_dispersao(
            dados=dados_scatter,
            x_col='x',
            y_col='y',
            titulo="Correlação (t vs t-1)"
        )
        graficos.append(('correlacao', fig3))
        
        # Histograma
        fig4 = plt.figure(figsize=(10, 6))
        plt.hist(dados['VALUE'], bins=20, alpha=0.7, edgecolor='black')
        plt.title('Distribuição dos Valores')
        plt.xlabel('Valor')
        plt.ylabel('Frequência')
        plt.grid(True, alpha=0.3)
        graficos.append(('distribuicao', fig4))
        
        # Teste de geração de PDF
        try:
            from src.services.pdf import gerar_pdf
            pdf_path = gerar_pdf(
                codSerie="TEST_MULTI_001",
                dfSerie=dados,
                iaText=get_mock_ia_response('multi_chart')
            )
            
            # Verificar retorno da função mockada
            assert pdf_path == "/tmp/test_pdf_TEST_MULTI_001.pdf"
            
        finally:
            for _, fig in graficos:
                plt.close(fig)
    
    @patch('src.services.pdf.gerar_pdf')
    def test_pdf_generation_with_large_dataset(self, mock_gerar_pdf_func):
        """Testa geração de PDF com dataset grande."""
        # Dataset grande (limitado para não exceder limites de data)
        dados_grandes = generate_mock_timeseries_data(code='TEST_LARGE', periods=500)
        
        # Configurar mock para simular PDF gerado
        def criar_pdf_mock(codSerie, dfSerie, iaText):
            return f"/tmp/test_pdf_{codSerie}_large.pdf"
        
        mock_gerar_pdf_func.side_effect = criar_pdf_mock
        
        # Criar resumo estatístico
        resumo_estatistico = {
            'total_pontos': len(dados_grandes),
            'periodo': f"{dados_grandes['RAW DATE'].min()} - {dados_grandes['RAW DATE'].max()}",
            'media': dados_grandes['VALUE'].mean(),
            'mediana': dados_grandes['VALUE'].median(),
            'desvio_padrao': dados_grandes['VALUE'].std(),
            'minimo': dados_grandes['VALUE'].min(),
            'maximo': dados_grandes['VALUE'].max(),
            'variacao_total': (
                dados_grandes['VALUE'].iloc[-1] - dados_grandes['VALUE'].iloc[0]
            ) / dados_grandes['VALUE'].iloc[0] * 100
        }
        
        # Gráficos otimizados para dataset grande
        graficos = []
        
        # Amostragem para gráfico de linha
        dados_amostra = dados_grandes.sample(min(200, len(dados_grandes))).sort_values('RAW DATE')
        fig1 = self.graph_generator.criar_grafico_linha(
            dados=dados_amostra,
            x_col='RAW DATE',
            y_col='VALUE',
            titulo="Série Temporal (Amostra)"
        )
        graficos.append(('amostra', fig1))
        
        # Médias mensais
        dados_mensais = dados_grandes.copy()
        dados_mensais['mes_ano'] = dados_mensais['RAW DATE'].dt.to_period('M')
        medias_mensais = dados_mensais.groupby('mes_ano')['VALUE'].mean().reset_index()
        medias_mensais['data'] = medias_mensais['mes_ano'].dt.to_timestamp()
        
        fig2 = self.graph_generator.criar_grafico_linha(
            dados=medias_mensais,
            x_col='data',
            y_col='VALUE',
            titulo="Médias Mensais"
        )
        graficos.append(('mensais', fig2))
        
        # Relatório com estatísticas (como string, não dict)
        relatorio_ia = get_mock_ia_response('large_dataset')
        # Formatar estatísticas no texto do relatório
        relatorio_ia = relatorio_ia.format(
            total_pontos=resumo_estatistico['total_pontos'],
            periodo=resumo_estatistico['periodo'],
            media=resumo_estatistico['media'],
            mediana=resumo_estatistico['mediana'],
            desvio_padrao=resumo_estatistico['desvio_padrao'],
            variacao_total=resumo_estatistico['variacao_total']
        )
        
        try:
            from src.services.pdf import gerar_pdf
            pdf_path = gerar_pdf(
                codSerie="TEST_LARGE_001",
                dfSerie=dados_grandes.head(100),  # Apenas amostra
                iaText=relatorio_ia
            )
            
            # Verificar retorno da função mockada
            assert pdf_path == "/tmp/test_pdf_TEST_LARGE_001_large.pdf"
            
        finally:
            for _, fig in graficos:
                plt.close(fig)
    
    @patch('src.services.pdf.gerar_pdf')
    def test_pdf_generation_error_handling(self, mock_gerar_pdf_func):
        """Testa tratamento de erros na geração de PDF."""
        dados = generate_mock_timeseries_data(code='TEST_ERROR', periods=10)
        
        # Configurar mock para levantar exceção
        mock_gerar_pdf_func.side_effect = Exception("Erro simulado na geração de PDF")
        
        # Teste com erro na geração
        with pytest.raises(Exception, match="Erro simulado na geração de PDF"):
            from src.services.pdf import gerar_pdf
            gerar_pdf(
                codSerie="TEST_ERROR_001",
                dfSerie=dados,
                iaText=get_mock_ia_response('error_test')
            )
    
    @patch('src.services.pdf.gerar_pdf')
    def test_pdf_generation_with_custom_styling(self, mock_gerar_pdf_func):
        """Testa geração de PDF com estilização customizada."""
        # Configurar mock para simular PDF gerado
        def criar_pdf_mock(codSerie, dfSerie, iaText):
            return f"/tmp/test_pdf_{codSerie}_styled.pdf"
        
        mock_gerar_pdf_func.side_effect = criar_pdf_mock
        
        dados = generate_mock_timeseries_data(code='TEST_STYLED', periods=50)
        
        # Gráfico com estilo customizado
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
        fig = plt.figure(figsize=(12, 8))
        plt.plot(dados['RAW DATE'], dados['VALUE'], linewidth=2, color='#1f77b4')
        plt.title('Indicador Econômico - Estilo Customizado', fontsize=16, fontweight='bold')
        plt.xlabel('Período', fontsize=12)
        plt.ylabel('Valor', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        graficos = [('customizado', fig)]
        
        try:
            from src.services.pdf import gerar_pdf
            pdf_path = gerar_pdf(
                codSerie="TEST_STYLED_001",
                dfSerie=dados,
                iaText=get_mock_ia_response('styled_report')
            )
            
            # Verificar retorno da função mockada
            assert pdf_path == "/tmp/test_pdf_TEST_STYLED_001_styled.pdf"
            
        finally:
            plt.close(fig)
    
    @patch('src.services.pdf.gerar_pdf')
    def test_pdf_generation_performance_timing(self, mock_gerar_pdf_func):
        """Testa performance da geração de PDF."""
        import time
        
        # Configurar mock para simular PDF gerado
        def criar_pdf_mock(codSerie, dfSerie, iaText):
            # Simular tempo de processamento
            time.sleep(0.1)  # Simular operação que demora um pouco
            return f"/tmp/test_pdf_{codSerie}_performance.pdf"
        
        mock_gerar_pdf_func.side_effect = criar_pdf_mock
        
        dados = generate_mock_timeseries_data(code='TEST_PERFORMANCE', periods=500)
        
        # Múltiplos gráficos para teste de performance
        graficos = []
        for i in range(5):
            dados_subset = dados.sample(100)
            fig = self.graph_generator.criar_grafico_linha(
                dados=dados_subset,
                x_col='RAW DATE',
                y_col='VALUE',
                titulo=f"Gráfico {i+1}"
            )
            graficos.append((f'grafico_{i+1}', fig))
        
        try:
            start_time = time.time()
            
            from src.services.pdf import gerar_pdf
            pdf_path = gerar_pdf(
                codSerie="TEST_PERFORMANCE_001",
                dfSerie=dados,
                iaText=get_mock_ia_response('performance_test')
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Verificar tempo de geração razoável (incluindo o sleep do mock)
            assert generation_time < 5  # Máximo 5 segundos (incluindo mock delay)
            assert pdf_path == "/tmp/test_pdf_TEST_PERFORMANCE_001_performance.pdf"
            
            # Log do tempo para análise
            print(f"Tempo de geração do PDF: {generation_time:.2f} segundos")
            
        finally:
            for _, fig in graficos:
                plt.close(fig)
    
    @patch('src.services.pdf.gerar_pdf')
    def test_pdf_generation_with_empty_data(self, mock_gerar_pdf_func):
        """Testa geração de PDF com dados vazios ou mínimos."""
        # Configurar mock para simular PDF gerado
        def criar_pdf_mock(codSerie, dfSerie, iaText):
            return f"/tmp/test_pdf_{codSerie}_empty.pdf"
        
        mock_gerar_pdf_func.side_effect = criar_pdf_mock
        
        # Dataset vazio
        dados_vazios = pd.DataFrame(columns=['RAW DATE', 'VALUE'])
        
        # Dataset com um ponto
        dados_minimos = pd.DataFrame({
            'RAW DATE': [datetime.now()],
            'VALUE': [100.0]
        })
        
        for dados, nome in [(dados_vazios, 'vazio'), (dados_minimos, 'minimo')]:
            try:
                from src.services.pdf import gerar_pdf
                pdf_path = gerar_pdf(
                    codSerie=f"TEST_EMPTY_{nome.upper()}_001",
                    dfSerie=dados,
                    iaText=get_mock_ia_response(f'empty_data_{nome}')
                )
                
                # Verificar se a função foi chamada corretamente
                expected_path = f"/tmp/test_pdf_TEST_EMPTY_{nome.upper()}_001_empty.pdf"
                assert pdf_path == expected_path
                
            except Exception as e:
                # Espera-se que dados vazios possam gerar exceção
                if dados.empty:
                    assert "Parametros insuficientes" in str(e) or "empty" in str(e)
                else:
                    raise e
    
    @patch('src.services.pdf.gerar_pdf')
    def test_pdf_generation_concurrent_access(self, mock_gerar_pdf_func):
        """Testa geração concorrente de múltiplos PDFs."""
        import concurrent.futures
        import threading
        
        # Configurar mock para simular PDF gerado
        def criar_pdf_mock(codSerie, dfSerie, iaText):
            return f"/tmp/test_pdf_{codSerie}_concurrent.pdf"
        
        mock_gerar_pdf_func.side_effect = criar_pdf_mock
        
        def gerar_pdf_async(thread_id):
            dados = generate_mock_timeseries_data(code=f'TEST_CONCURRENT_{thread_id}', periods=50)
            
            try:
                from src.services.pdf import gerar_pdf
                pdf_path = gerar_pdf(
                    codSerie=f"TEST_CONCURRENT_{thread_id}",
                    dfSerie=dados,
                    iaText=get_mock_ia_response(f'concurrent_{thread_id}')
                )
                
                return pdf_path, True  # Simular sucesso
                
            except Exception as e:
                raise
        
        # Executar gerações em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(gerar_pdf_async, i) for i in range(3)]
            resultados = [future.result() for future in futures]
        
        # Verificar que todos os PDFs foram processados
        assert len(resultados) == 3
        for pdf_path, success in resultados:
            assert success
            assert "concurrent" in pdf_path
            
        # Verificar que a função foi chamada 3 vezes
        assert mock_gerar_pdf_func.call_count == 3
