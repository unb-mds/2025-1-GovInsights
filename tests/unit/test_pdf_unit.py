import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


@pytest.fixture
def temp_files(tmp_path):
    # Cria arquivos temporários reais para simular NamedTemporaryFile
    img_file = tmp_path / "temp_img.png"
    img_file.write_text("fake image data")  # conteúdo dummy só para existir o arquivo
    pdf_file = tmp_path / "temp_pdf.pdf"
    pdf_file.write_text("fake pdf data")
    return str(img_file), str(pdf_file)


def fake_tempfile_factory(tmp_img_name, tmp_pdf_name):
    # Factory para simular NamedTemporaryFile retornando um context manager com .name válido
    def _fake_tempfile(*args, **kwargs):
        class FakeContext:
            def __enter__(self_inner):
                class FakeFile:
                    # Retorna nome correto conforme sufixo
                    name = tmp_img_name if kwargs.get('suffix') == '.png' else tmp_pdf_name
                    def close(self): pass
                return FakeFile()
            def __exit__(self_inner, exc_type, exc_value, traceback): return False
        return FakeContext()
    return _fake_tempfile


def test_gerar_pdf_raises_exception_on_invalid_params():
    import src.services.pdf as pdf

    with pytest.raises(Exception):
        pdf.gerar_pdf("", pd.DataFrame(), "")

    with pytest.raises(Exception):
        pdf.gerar_pdf("COD", pd.DataFrame(), "")

    with pytest.raises(Exception):
        pdf.gerar_pdf("", pd.DataFrame({"a": [1]}), "texto")

    with pytest.raises(Exception):
        pdf.gerar_pdf("COD", pd.DataFrame(), "texto")


@patch("pandas.DataFrame.plot")  # evitar plot real
@patch("matplotlib.pyplot.subplots")
@patch("xhtml2pdf.pisa.CreatePDF")
@patch("markdown.markdown")
def test_gerar_pdf_success(mock_md, mock_pisa, mock_subplots, mock_plot, temp_files):
    import src.services.pdf as pdf

    tmp_img_name, tmp_pdf_name = temp_files

    mock_md.return_value = "<p>Relatório em HTML</p>"
    mock_pisa.return_value = MagicMock(err=False)

    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_subplots.return_value = (mock_fig, mock_ax)
    mock_fig.savefig = MagicMock()

    with patch("tempfile.NamedTemporaryFile", side_effect=fake_tempfile_factory(tmp_img_name, tmp_pdf_name)):
        df = pd.DataFrame({"valores": [1, 2, 3, 4]})
        caminho_pdf = pdf.gerar_pdf("COD123", df, "Texto em markdown")

        assert caminho_pdf == tmp_pdf_name
        mock_md.assert_called_once_with("Texto em markdown")
        mock_subplots.assert_called_once()
        mock_fig.savefig.assert_called_once_with(tmp_img_name)
        mock_pisa.assert_called_once()


@patch("xhtml2pdf.pisa.CreatePDF")
def test_gerar_pdf_raises_exception_on_pdf_error(mock_pisa, temp_files):
    import src.services.pdf as pdf

    tmp_img_name, tmp_pdf_name = temp_files

    mock_pisa.return_value = MagicMock(err=True)

    with patch("tempfile.NamedTemporaryFile", side_effect=fake_tempfile_factory(tmp_img_name, tmp_pdf_name)):
        df = pd.DataFrame({"valores": [1, 2, 3]})

        with pytest.raises(Exception, match="PDF não foi gerado."):
            pdf.gerar_pdf("COD", df, "Texto")


@patch("matplotlib.pyplot.subplots")
def test_gerar_pdf_handles_dataframe_plotting_error(mock_subplots, temp_files):
    import src.services.pdf as pdf

    tmp_img_name, tmp_pdf_name = temp_files

    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_subplots.return_value = (mock_fig, mock_ax)
    mock_fig.savefig = MagicMock()

    # Simular erro em ax.plot, pois é ele que gera gráfico
    mock_ax.plot.side_effect = Exception("Erro no plot")

    with patch("tempfile.NamedTemporaryFile", side_effect=fake_tempfile_factory(tmp_img_name, tmp_pdf_name)):
        df = pd.DataFrame({"valores": [1, 2, 3]})

        with pytest.raises(Exception, match="Erro no plot"):
            pdf.gerar_pdf("COD", df, "texto")


@patch("pandas.DataFrame.plot")
@patch("matplotlib.pyplot.subplots")
@patch("xhtml2pdf.pisa.CreatePDF")
@patch("markdown.markdown")
def test_gerar_pdf_handles_markdown_conversion_error(mock_md, mock_pisa, mock_subplots, mock_plot, temp_files):
    import src.services.pdf as pdf

    tmp_img_name, tmp_pdf_name = temp_files

    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_subplots.return_value = (mock_fig, mock_ax)
    mock_fig.savefig = MagicMock()
    mock_pisa.return_value = MagicMock(err=False)

    # Simular exceção na conversão markdown -> html
    mock_md.side_effect = Exception("Erro markdown")

    with patch("tempfile.NamedTemporaryFile", side_effect=fake_tempfile_factory(tmp_img_name, tmp_pdf_name)):
        df = pd.DataFrame({"valores": [1, 2, 3]})

        with pytest.raises(Exception, match="Erro markdown"):
            pdf.gerar_pdf("COD", df, "texto")
