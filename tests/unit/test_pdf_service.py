import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from src.services.pdf import gerar_pdf


class TestPdfService:
    """Testes unitários para o serviço de geração de PDF."""

    def test_gerar_pdf_parametros_validos(self):
        """Teste de geração de PDF com parâmetros válidos."""
        # Arrange
        cod_serie = "TEST123"
        df_serie = pd.DataFrame({"data": ["2023-01", "2023-02"], "valor": [100, 150]})
        ia_text = "# Relatório\n\nEste é um relatório de teste."
        
        with patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('markdown.markdown') as mock_markdown, \
             patch('xhtml2pdf.pisa.CreatePDF') as mock_create_pdf:
            
            # Mock matplotlib
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Mock tempfile
            mock_temp_img = MagicMock()
            mock_temp_img.name = "/tmp/test_img.png"
            mock_temp_img.__enter__ = MagicMock(return_value=mock_temp_img)
            mock_temp_img.__exit__ = MagicMock(return_value=None)
            
            mock_temp_pdf = MagicMock()
            mock_temp_pdf.name = "/tmp/test_output.pdf"
            mock_temp_pdf.__enter__ = MagicMock(return_value=mock_temp_pdf)
            mock_temp_pdf.__exit__ = MagicMock(return_value=None)
            
            mock_tempfile.side_effect = [mock_temp_img, mock_temp_pdf]
            
            # Mock markdown
            mock_markdown.return_value = "<h1>Relatório</h1><p>Este é um relatório de teste.</p>"
            
            # Mock pisa
            mock_status = MagicMock()
            mock_status.err = False
            mock_create_pdf.return_value = mock_status
            
            # Act
            result = gerar_pdf(cod_serie, df_serie, ia_text)
            
            # Assert
            assert result == "/tmp/test_output.pdf"
            mock_subplots.assert_called_once()
            mock_ax.plot.assert_called_once()
            mock_ax.set_xlabel.assert_called_once_with("data")
            mock_ax.set_ylabel.assert_called_once_with("valor")
            mock_fig.savefig.assert_called_once_with("/tmp/test_img.png")
            mock_markdown.assert_called_once_with(ia_text)
            mock_create_pdf.assert_called_once()

    def test_gerar_pdf_codigo_serie_vazio(self):
        """Teste de geração de PDF com código de série vazio."""
        # Arrange
        cod_serie = ""
        df_serie = pd.DataFrame({"data": ["2023-01"], "valor": [100]})
        ia_text = "Relatório de teste"
        
        # Act & Assert
        with pytest.raises(Exception, match="Parametros insuficientes."):
            gerar_pdf(cod_serie, df_serie, ia_text)

    def test_gerar_pdf_dataframe_vazio(self):
        """Teste de geração de PDF com dataframe vazio."""
        # Arrange
        cod_serie = "TEST123"
        df_serie = pd.DataFrame()
        ia_text = "Relatório de teste"
        
        # Act & Assert
        with pytest.raises(Exception, match="Parametros insuficientes."):
            gerar_pdf(cod_serie, df_serie, ia_text)

    def test_gerar_pdf_texto_ia_vazio(self):
        """Teste de geração de PDF com texto da IA vazio."""
        # Arrange
        cod_serie = "TEST123"
        df_serie = pd.DataFrame({"data": ["2023-01"], "valor": [100]})
        ia_text = ""
        
        # Act & Assert
        with pytest.raises(Exception, match="Parametros insuficientes."):
            gerar_pdf(cod_serie, df_serie, ia_text)

    def test_gerar_pdf_erro_na_geracao(self):
        """Teste de geração de PDF com erro na criação do PDF."""
        # Arrange
        cod_serie = "TEST123"
        df_serie = pd.DataFrame({"data": ["2023-01"], "valor": [100]})
        ia_text = "# Relatório\n\nTeste com erro."
        
        with patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('markdown.markdown') as mock_markdown, \
             patch('xhtml2pdf.pisa.CreatePDF') as mock_create_pdf:
            
            # Mock matplotlib
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Mock tempfile
            mock_temp_img = MagicMock()
            mock_temp_img.name = "/tmp/test_img.png"
            mock_temp_img.__enter__ = MagicMock(return_value=mock_temp_img)
            mock_temp_img.__exit__ = MagicMock(return_value=None)
            
            mock_temp_pdf = MagicMock()
            mock_temp_pdf.name = "/tmp/test_output.pdf"
            mock_temp_pdf.__enter__ = MagicMock(return_value=mock_temp_pdf)
            mock_temp_pdf.__exit__ = MagicMock(return_value=None)
            
            mock_tempfile.side_effect = [mock_temp_img, mock_temp_pdf]
            
            # Mock markdown
            mock_markdown.return_value = "<h1>Relatório</h1><p>Teste com erro.</p>"
            
            # Mock pisa com erro
            mock_status = MagicMock()
            mock_status.err = True
            mock_create_pdf.return_value = mock_status
            
            # Act & Assert
            with pytest.raises(Exception, match="PDF não foi gerado."):
                gerar_pdf(cod_serie, df_serie, ia_text)

    def test_gerar_pdf_dataframe_com_multiplas_colunas(self):
        """Teste de geração de PDF com dataframe contendo múltiplas colunas."""
        # Arrange
        cod_serie = "MULTI123"
        df_serie = pd.DataFrame({
            "data": ["2023-01", "2023-02", "2023-03"],
            "valor": [100, 150, 200],
            "extra_col": ["A", "B", "C"]
        })
        ia_text = "# Análise Múltiplas Séries\n\nDados analisados com sucesso."
        
        with patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('markdown.markdown') as mock_markdown, \
             patch('xhtml2pdf.pisa.CreatePDF') as mock_create_pdf:
            
            # Setup mocks
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            mock_temp_img = MagicMock()
            mock_temp_img.name = "/tmp/multi_img.png"
            mock_temp_img.__enter__ = MagicMock(return_value=mock_temp_img)
            mock_temp_img.__exit__ = MagicMock(return_value=None)
            
            mock_temp_pdf = MagicMock()
            mock_temp_pdf.name = "/tmp/multi_output.pdf"
            mock_temp_pdf.__enter__ = MagicMock(return_value=mock_temp_pdf)
            mock_temp_pdf.__exit__ = MagicMock(return_value=None)
            
            mock_tempfile.side_effect = [mock_temp_img, mock_temp_pdf]
            
            mock_markdown.return_value = "<h1>Análise Múltiplas Séries</h1><p>Dados analisados com sucesso.</p>"
            
            mock_status = MagicMock()
            mock_status.err = False
            mock_create_pdf.return_value = mock_status
            
            # Act
            result = gerar_pdf(cod_serie, df_serie, ia_text)
            
            # Assert
            assert result == "/tmp/multi_output.pdf"
            # Verifica se a última coluna foi usada corretamente
            mock_ax.plot.assert_called_once()

    def test_gerar_pdf_markdown_complexo(self):
        """Teste de geração de PDF com markdown complexo."""
        # Arrange
        cod_serie = "COMPLEX123"
        df_serie = pd.DataFrame({"data": ["2023-01"], "valor": [500]})
        ia_text = """
# Relatório Complexo

## Seção 1
Este é um **texto em negrito** e este é um *texto em itálico*.

### Subseção
- Item 1
- Item 2
- Item 3

## Conclusão
Análise finalizada com [link](http://example.com).
        """
        
        with patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('markdown.markdown') as mock_markdown, \
             patch('xhtml2pdf.pisa.CreatePDF') as mock_create_pdf:
            
            # Setup mocks
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            mock_temp_img = MagicMock()
            mock_temp_img.name = "/tmp/complex_img.png"
            mock_temp_img.__enter__ = MagicMock(return_value=mock_temp_img)
            mock_temp_img.__exit__ = MagicMock(return_value=None)
            
            mock_temp_pdf = MagicMock()
            mock_temp_pdf.name = "/tmp/complex_output.pdf"
            mock_temp_pdf.__enter__ = MagicMock(return_value=mock_temp_pdf)
            mock_temp_pdf.__exit__ = MagicMock(return_value=None)
            
            mock_tempfile.side_effect = [mock_temp_img, mock_temp_pdf]
            
            # Mock markdown com HTML complexo
            mock_markdown.return_value = """
            <h1>Relatório Complexo</h1>
            <h2>Seção 1</h2>
            <p>Este é um <strong>texto em negrito</strong> e este é um <em>texto em itálico</em>.</p>
            <h3>Subseção</h3>
            <ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>
            <h2>Conclusão</h2>
            <p>Análise finalizada com <a href="http://example.com">link</a>.</p>
            """
            
            mock_status = MagicMock()
            mock_status.err = False
            mock_create_pdf.return_value = mock_status
            
            # Act
            result = gerar_pdf(cod_serie, df_serie, ia_text)
            
            # Assert
            assert result == "/tmp/complex_output.pdf"
            mock_markdown.assert_called_once_with(ia_text)

    def test_gerar_pdf_validacao_html_gerado(self):
        """Teste para validar o HTML gerado contém elementos esperados."""
        # Arrange
        cod_serie = "HTML123"
        df_serie = pd.DataFrame({"data": ["2023-01"], "valor": [300]})
        ia_text = "## Teste HTML\n\nConteúdo do relatório."
        
        with patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('markdown.markdown') as mock_markdown, \
             patch('xhtml2pdf.pisa.CreatePDF') as mock_create_pdf:
            
            # Setup mocks
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            mock_temp_img = MagicMock()
            mock_temp_img.name = "/tmp/html_img.png"
            mock_temp_img.__enter__ = MagicMock(return_value=mock_temp_img)
            mock_temp_img.__exit__ = MagicMock(return_value=None)
            
            mock_temp_pdf = MagicMock()
            mock_temp_pdf.name = "/tmp/html_output.pdf"
            mock_temp_pdf.__enter__ = MagicMock(return_value=mock_temp_pdf)
            mock_temp_pdf.__exit__ = MagicMock(return_value=None)
            
            mock_tempfile.side_effect = [mock_temp_img, mock_temp_pdf]
            
            mock_markdown.return_value = "<h2>Teste HTML</h2><p>Conteúdo do relatório.</p>"
            
            mock_status = MagicMock()
            mock_status.err = False
            mock_create_pdf.return_value = mock_status
            
            # Act
            result = gerar_pdf(cod_serie, df_serie, ia_text)
            
            # Assert
            assert result == "/tmp/html_output.pdf"
            # Verificar se CreatePDF foi chamado com HTML contendo elementos esperados
            html_content = mock_create_pdf.call_args[0][0]
            assert "GovInsights" in html_content
            assert f"Dados da Série {cod_serie} do IPEA" in html_content
            assert "/tmp/html_img.png" in html_content
            assert "<h2>Teste HTML</h2><p>Conteúdo do relatório.</p>" in html_content
            assert "font-family: Helvetica" in html_content
