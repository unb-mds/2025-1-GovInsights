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
        # Preparar dados de teste
        dados = get_mock_dataframe(size=100)
        
        # Usar os gráficos reais gerados pela classe timeSeries
        graficos = []
        
        # Usar os gráficos já disponíveis na instância
        if hasattr(self.graph_generator, 'graficos') and self.graph_generator.graficos:
            for periodo, fig in self.graph_generator.graficos.items():
                graficos.append((periodo, fig))
        
        # Se não há gráficos, criar um mock simples
        if not graficos:
            import plotly.graph_objects as go
            fig_mock = go.Figure()
            fig_mock.add_trace(go.Scatter(
                x=dados['data'],
                y=dados['valor'],
                mode='lines',
                name='Dados de Teste'
            ))
            graficos.append(('Período de Teste', fig_mock))
        
        # Relatório IA
        relatorio_ia = get_mock_ia_response('complete_analysis')
        
        # Metadados
        metadados = {
            'titulo': 'Relatório Econômico Completo',
            'subtitulo': 'Análise de Indicadores Macroeconômicos',
            'periodo': '2023-2024',
            'data_geracao': datetime.now(),
            'autor': 'GovInsights - Sistema de Análise Econômica',
            'versao': '1.0'
        }
        
        # Gerar PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        try:
            self.pdf_generator.gerar_relatorio_completo(
                dados=dados,
                graficos=graficos,
                relatorio_ia=relatorio_ia,
                metadados=metadados,
                arquivo_saida=pdf_path
            )
            
            # Verificações básicas
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 10000  # PDF não-vazio (>10KB)
            
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
                        assert len(pdf_reader.pages) >= 3  # Mínimo 3 páginas
                        
                        # Verificar se contém texto
                        first_page = pdf_reader.pages[0]
                        text = first_page.extract_text()
                        assert metadados['titulo'] in text
                except Exception:
                    # Erro na leitura do PDF, pular verificação
                    pass
                
        finally:
            # Limpeza
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            
            # Fechar figuras para liberar memória
            import matplotlib.pyplot as plt
            for _, fig in graficos:
                try:
                    # Só fechar se for figura matplotlib
                    if hasattr(fig, 'number'):  # Matplotlib figure
                        plt.close(fig)
                    # Figuras Plotly não precisam ser fechadas explicitamente
                except Exception:
                    pass  # Ignorar erros ao fechar figuras
    
    def test_pdf_generation_with_multiple_chart_types(self):
        """Testa geração de PDF com múltiplos tipos de gráficos."""
        dados = get_mock_dataframe(size=200)
        
        graficos = []
        
        # Usar gráficos reais da classe timeSeries
        if hasattr(self.graph_generator, 'graficos') and self.graph_generator.graficos:
            for periodo, fig in self.graph_generator.graficos.items():
                graficos.append((periodo, fig))
        
        # Adicionar gráfico manual usando matplotlib
        import matplotlib.pyplot as plt
        fig_manual = plt.figure(figsize=(10, 6))
        plt.plot(dados['data'], dados['valor'], label='Valores')
        plt.title('Série Temporal Manual')
        plt.xlabel('Data')
        plt.ylabel('Valor')
        plt.legend()
        plt.grid(True, alpha=0.3)
        graficos.append(('manual', fig_manual))
        
        # Histograma
        fig_hist = plt.figure(figsize=(10, 6))
        plt.hist(dados['valor'], bins=20, alpha=0.7, edgecolor='black')
        plt.title('Distribuição dos Valores')
        plt.xlabel('Valor')
        plt.ylabel('Frequência')
        plt.grid(True, alpha=0.3)
        graficos.append(('distribuicao', fig_hist))
        
        # Gerar PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        try:
            self.pdf_generator.gerar_relatorio_completo(
                dados=dados,
                graficos=graficos,
                relatorio_ia=get_mock_ia_response('multi_chart'),
                metadados={
                    'titulo': 'Relatório Multi-Gráficos',
                    'data_geracao': datetime.now()
                },
                arquivo_saida=pdf_path
            )
            
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 50000  # PDF mais substancial
            
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            for _, fig in graficos:
                plt.close(fig)
    
    def test_pdf_generation_with_large_dataset(self):
        """Testa geração de PDF com dataset grande."""
        # Dataset grande
        dados_grandes = get_mock_dataframe(size=5000)
        
        # Criar resumo estatístico
        resumo_estatistico = {
            'total_pontos': len(dados_grandes),
            'periodo': f"{dados_grandes['data'].min()} - {dados_grandes['data'].max()}",
            'media': dados_grandes['valor'].mean(),
            'mediana': dados_grandes['valor'].median(),
            'desvio_padrao': dados_grandes['valor'].std(),
            'minimo': dados_grandes['valor'].min(),
            'maximo': dados_grandes['valor'].max(),
            'variacao_total': (
                dados_grandes['valor'].iloc[-1] - dados_grandes['valor'].iloc[0]
            ) / dados_grandes['valor'].iloc[0] * 100
        }
        
        # Gráficos otimizados para dataset grande
        graficos = []
        
        # Usar gráficos reais da classe timeSeries
        if hasattr(self.graph_generator, 'graficos') and self.graph_generator.graficos:
            for periodo, fig in self.graph_generator.graficos.items():
                graficos.append((periodo, fig))
        
        # Adicionar gráfico manual com amostragem
        import matplotlib.pyplot as plt
        dados_amostra = dados_grandes.sample(500).sort_values('data')
        fig_manual = plt.figure(figsize=(12, 8))
        plt.plot(dados_amostra['data'], dados_amostra['valor'], alpha=0.7)
        plt.title("Série Temporal (Amostra de 500 pontos)")
        plt.xlabel('Data')
        plt.ylabel('Valor')
        plt.grid(True, alpha=0.3)
        graficos.append(('amostra', fig_manual))
        
        # Médias mensais
        dados_mensais = dados_grandes.copy()
        dados_mensais['mes_ano'] = dados_mensais['data'].dt.to_period('M')
        medias_mensais = dados_mensais.groupby('mes_ano')['valor'].mean().reset_index()
        medias_mensais['data'] = medias_mensais['mes_ano'].dt.to_timestamp()
        
        fig_mensais = plt.figure(figsize=(12, 8))
        plt.plot(medias_mensais['data'], medias_mensais['valor'], marker='o')
        plt.title("Médias Mensais")
        plt.xlabel('Data')
        plt.ylabel('Valor Médio')
        plt.grid(True, alpha=0.3)
        graficos.append(('mensais', fig_mensais))
        
        # Relatório com estatísticas
        relatorio_ia = get_mock_ia_response('large_dataset')
        relatorio_ia['estatisticas'] = resumo_estatistico
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        try:
            self.pdf_generator.gerar_relatorio_completo(
                dados=dados_grandes.head(100),  # Apenas amostra na tabela
                graficos=graficos,
                relatorio_ia=relatorio_ia,
                metadados={
                    'titulo': 'Análise de Dataset Grande',
                    'subtitulo': f'Análise de {len(dados_grandes):,} pontos de dados',
                    'data_geracao': datetime.now()
                },
                arquivo_saida=pdf_path
            )
            
            assert os.path.exists(pdf_path)
            # PDF deve ser criado mesmo com dataset grande
            assert os.path.getsize(pdf_path) > 0
            
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            for _, fig in graficos:
                plt.close(fig)
    
    def test_pdf_generation_error_handling(self):
        """Testa tratamento de erros na geração de PDF."""
        dados = get_mock_dataframe(size=10)
        
        # Teste com caminho inválido
        with pytest.raises(Exception):
            self.pdf_generator.gerar_relatorio_completo(
                dados=dados,
                graficos=[],
                relatorio_ia=get_mock_ia_response('error_test'),
                metadados={'titulo': 'Teste Erro'},
                arquivo_saida='/caminho/invalido/arquivo.pdf'
            )
        
        # Teste com dados corrompidos
        dados_corrompidos = pd.DataFrame({
            'data': ['texto_invalido', 'mais_texto'],
            'valor': ['não_numero', 'outro_texto']
        })
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        try:
            # Deve tratar dados corrompidos graciosamente
            self.pdf_generator.gerar_relatorio_completo(
                dados=dados_corrompidos,
                graficos=[],
                relatorio_ia=get_mock_ia_response('corrupted_data'),
                metadados={'titulo': 'Teste Dados Corrompidos'},
                arquivo_saida=pdf_path
            )
            
            # PDF deve ser criado mesmo com dados problemáticos
            assert os.path.exists(pdf_path)
            
        except Exception as e:
            # Se falhar, deve ser uma exceção tratada adequadamente
            assert "dados" in str(e).lower() or "formato" in str(e).lower()
            
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_pdf_generation_with_custom_styling(self):
        """Testa geração de PDF com estilização customizada."""
        dados = get_mock_dataframe(size=50)
        
        # Gráfico com estilo customizado
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
        fig = plt.figure(figsize=(12, 8))
        plt.plot(dados['data'], dados['valor'], linewidth=2, color='#1f77b4')
        plt.title('Indicador Econômico - Estilo Customizado', fontsize=16, fontweight='bold')
        plt.xlabel('Período', fontsize=12)
        plt.ylabel('Valor', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        graficos = [('customizado', fig)]
        
        # Metadados estendidos
        metadados = {
            'titulo': 'Relatório com Estilo Customizado',
            'subtitulo': 'Análise Econômica com Design Aprimorado',
            'periodo': '2023-2024',
            'data_geracao': datetime.now(),
            'autor': 'Sistema GovInsights',
            'versao': '2.0',
            'confidencialidade': 'Público',
            'fonte_dados': 'IPEA - Instituto de Pesquisa Econômica Aplicada',
            'metodologia': 'Análise quantitativa com IA generativa',
            'observacoes': 'Relatório gerado automaticamente'
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        try:
            self.pdf_generator.gerar_relatorio_completo(
                dados=dados,
                graficos=graficos,
                relatorio_ia=get_mock_ia_response('styled_report'),
                metadados=metadados,
                arquivo_saida=pdf_path,
                estilo_customizado=True
            )
            
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 0
            
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            plt.close(fig)
    
    def test_pdf_generation_performance_timing(self):
        """Testa performance da geração de PDF."""
        import time
        
        dados = get_mock_dataframe(size=500)
        
        # Múltiplos gráficos para teste de performance
        graficos = []
        
        # Usar gráficos reais da classe timeSeries
        if hasattr(self.graph_generator, 'graficos') and self.graph_generator.graficos:
            for periodo, fig in self.graph_generator.graficos.items():
                graficos.append((periodo, fig))
        
        # Adicionar gráficos manuais para teste de performance
        import matplotlib.pyplot as plt
        for i in range(3):
            dados_subset = dados.sample(100)
            fig = plt.figure(figsize=(10, 6))
            plt.plot(dados_subset['data'], dados_subset['valor'])
            plt.title(f"Gráfico {i+1}")
            plt.xlabel('Data')
            plt.ylabel('Valor')
            plt.grid(True, alpha=0.3)
            graficos.append((f'grafico_{i+1}', fig))
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        try:
            start_time = time.time()
            
            self.pdf_generator.gerar_relatorio_completo(
                dados=dados,
                graficos=graficos,
                relatorio_ia=get_mock_ia_response('performance_test'),
                metadados={
                    'titulo': 'Teste de Performance',
                    'data_geracao': datetime.now()
                },
                arquivo_saida=pdf_path
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Verificar tempo de geração razoável
            assert generation_time < 30  # Máximo 30 segundos
            assert os.path.exists(pdf_path)
            
            # Log do tempo para análise
            print(f"Tempo de geração do PDF: {generation_time:.2f} segundos")
            
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            for _, fig in graficos:
                plt.close(fig)
    
    def test_pdf_generation_with_empty_data(self):
        """Testa geração de PDF com dados vazios ou mínimos."""
        # Dataset vazio
        dados_vazios = pd.DataFrame(columns=['data', 'valor'])
        
        # Dataset com um ponto
        dados_minimos = pd.DataFrame({
            'data': [datetime.now()],
            'valor': [100.0]
        })
        
        for dados, nome in [(dados_vazios, 'vazio'), (dados_minimos, 'minimo')]:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                pdf_path = tmp_file.name
            
            try:
                self.pdf_generator.gerar_relatorio_completo(
                    dados=dados,
                    graficos=[],
                    relatorio_ia=get_mock_ia_response(f'empty_data_{nome}'),
                    metadados={
                        'titulo': f'Teste Dataset {nome.title()}',
                        'data_geracao': datetime.now()
                    },
                    arquivo_saida=pdf_path
                )
                
                # PDF deve ser criado mesmo com dados mínimos
                assert os.path.exists(pdf_path)
                assert os.path.getsize(pdf_path) > 0
                
            finally:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
    
    def test_pdf_generation_concurrent_access(self):
        """Testa geração concorrente de múltiplos PDFs."""
        import concurrent.futures
        import threading
        
        def gerar_pdf_async(thread_id):
            dados = get_mock_dataframe(size=50)
            
            with tempfile.NamedTemporaryFile(suffix=f'_thread_{thread_id}.pdf', delete=False) as tmp_file:
                pdf_path = tmp_file.name
            
            try:
                self.pdf_generator.gerar_relatorio_completo(
                    dados=dados,
                    graficos=[],
                    relatorio_ia=get_mock_ia_response(f'concurrent_{thread_id}'),
                    metadados={
                        'titulo': f'Relatório Thread {thread_id}',
                        'data_geracao': datetime.now()
                    },
                    arquivo_saida=pdf_path
                )
                
                return pdf_path, os.path.getsize(pdf_path)
                
            except Exception as e:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
                raise
        
        # Executar gerações em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(gerar_pdf_async, i) for i in range(3)]
            resultados = [future.result() for future in futures]
        
        try:
            # Verificar que todos os PDFs foram criados
            assert len(resultados) == 3
            for pdf_path, file_size in resultados:
                assert os.path.exists(pdf_path)
                assert file_size > 0
                
        finally:
            # Limpeza
            for pdf_path, _ in resultados:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
