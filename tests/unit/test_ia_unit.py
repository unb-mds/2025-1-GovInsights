import pytest
import pandas as pd
from src.services.ia import gerar_relatorio_com_busca_externa_stream
from unittest.mock import patch, MagicMock


def test_gerar_relatorio_parametros_invalidos():
    with pytest.raises(Exception, match="Parametros incorretos."):
        gerar_relatorio_com_busca_externa_stream("COD001", pd.DataFrame())

    df = pd.DataFrame({"ano": [2020], "valor": [100]})
    with pytest.raises(Exception, match="Parametros incorretos."):
        gerar_relatorio_com_busca_externa_stream("", df)


@patch("ipeadatapy.describe")
@patch("feedparser.parse") 
@patch("together.Together")
def test_gerar_relatorio_sucesso(mock_together, mock_feedparser, mock_describe):
    # Mock da descrição da série IPEA
    mock_desc = pd.DataFrame([["Nome da Série Teste"], [None], [None], [None], [None], [None], ["Comentário da série"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = [
        MagicMock(title="Notícia 1", link="http://link1.com", published="2024-01-01", summary="Resumo 1"),
        MagicMock(title="Notícia 2", link="http://link2.com", published="2024-01-02", summary="Resumo 2")
    ]
    mock_feedparser.return_value = mock_feed

    # Mock do streaming da Together API
    mock_client = MagicMock()
    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock()]
    mock_chunk1.choices[0].delta.content = "Relatório "
    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock()]
    mock_chunk2.choices[0].delta.content = "gerado pela IA."
    mock_client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200, 300]}, 
                     index=pd.date_range("2024-01-01", periods=3, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("COD123", df)
    
    # Verifica se contém o header e o conteúdo
    assert "Período dos Dados:" in resultado
    assert "Total de Observações:" in resultado
    assert "Relatório gerado pela IA." in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together", side_effect=Exception("Falha de rede"))
def test_gerar_relatorio_erro_api(mock_together, mock_feedparser, mock_describe):
    # Mock da descrição da série IPEA
    mock_desc = pd.DataFrame([["Nome da Série"], [None], [None], [None], [None], [None], ["Comentário"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    with pytest.raises(Exception, match="Conexão com IA falhou."):
        gerar_relatorio_com_busca_externa_stream("COD321", df)


# NOVOS TESTES ADICIONADOS PARA A IMPLEMENTAÇÃO COM BUSCA EXTERNA E STREAMING

@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_formatacao_prompt(mock_together, mock_feedparser, mock_describe):
    # Mock da descrição da série IPEA
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], ["Descrição teste"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = [
        MagicMock(title="Economia brasileira em alta", link="http://test.com", published="2024-01-01", summary="Resumo")
    ]
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Análise"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    gerar_relatorio_com_busca_externa_stream("SERIE123", df)

    # Verifica se o prompt foi formatado corretamente
    args = mock_client.chat.completions.create.call_args[1]
    prompt = args["messages"][0]["content"]
    assert "SERIE123" in prompt
    assert "PORTUGUÊS BRASILEIRO" in prompt
    assert "Série Teste" in prompt
    assert ",Valor" in prompt  # Nova estrutura otimizada do CSV (índice + coluna Valor)
    assert "NOTÍCIAS RELACIONADAS" in prompt


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_processamento_dataframe(mock_together, mock_feedparser, mock_describe):
    # Mock da descrição da série IPEA
    mock_desc = pd.DataFrame([["Série Grande"], [None], [None], [None], [None], [None], ["Descrição"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    # DataFrame com 500 registros para testar a limitação de 300
    df = pd.DataFrame({
        "valor": list(range(500))
    }, index=pd.date_range("2020-01-01", periods=500, freq="D"))

    gerar_relatorio_com_busca_externa_stream("COD999", df)

    args = mock_client.chat.completions.create.call_args[1]
    prompt = args["messages"][0]["content"]
    
    # Verifica se CSV contém no máximo 300 linhas + header (nova otimização)
    # Procura pela seção "Dados da série (CSV):"
    import re
    csv_match = re.search(r"Dados da série \(CSV\):\s*(.*?)(?=\n\n|\nNOTÍCIAS|$)", prompt, re.DOTALL)
    assert csv_match is not None, "Seção CSV não encontrada no prompt"
    
    csv_content = csv_match.group(1).strip()
    csv_lines = csv_content.splitlines()
    
    # Filtra apenas linhas com dados (que contêm vírgula)
    data_lines = [line for line in csv_lines if "," in line and line.strip()]
    # Remove header se presente
    if data_lines and ("Date" in data_lines[0] or "Valor" in data_lines[0]):
        data_lines = data_lines[1:]
    
    assert len(data_lines) <= 300

    # Verifica ordenação (mais recente primeiro)
    assert str(df.index[-1].date()) in prompt


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_ordenacao_csv_dataframe(mock_together, mock_feedparser, mock_describe):
    import re
    
    # Mock da descrição da série IPEA
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], ["Descrição"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed
    
    df = pd.DataFrame({
        "valor": list(range(500))  # 500 registros para testar limitação de 300
    }, index=pd.date_range("2020-01-01", periods=500, freq="D"))

    mock_client = MagicMock()
    # Mock do streaming
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório teste"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    gerar_relatorio_com_busca_externa_stream("COD999", df)

    args = mock_client.chat.completions.create.call_args[1]
    prompt = args["messages"][0]["content"]

    # Verifica se CSV contém no máximo 300 linhas (nova otimização)
    csv_match = re.search(r"Dados da série \(CSV\):\s*(.*?)(?=\n\n|\nNOTÍCIAS|$)", prompt, re.DOTALL)
    assert csv_match is not None

    csv_part = csv_match.group(1).strip()
    csv_lines = csv_part.splitlines()
    
    # Filtra apenas linhas com dados (que contêm vírgula)
    data_lines = [line for line in csv_lines if "," in line and line.strip()]
    # Remove header se presente
    if data_lines and ("Date" in data_lines[0] or "Valor" in data_lines[0]):
        data_lines = data_lines[1:]
        
    assert len(data_lines) <= 300

    # Verifica ordenação - última data (mais recente) deve estar no início do CSV
    # DataFrame é invertido na função (mais recente primeiro)
    if data_lines:
        first_data_line = data_lines[0]
        expected_date = df.index[-1].strftime("%Y-%m-%d")
        assert expected_date in first_data_line



@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_dados_especiais(mock_together, mock_feedparser, mock_describe):
    # Mock da descrição da série IPEA
    mock_desc = pd.DataFrame([["Série Especial"], [None], [None], [None], [None], [None], ["Dados especiais"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório com dados especiais"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({
        "valor": [None, 3.14, 100]
    }, index=pd.date_range("2024-01-01", periods=3, freq="D"))

    # Validação - Se a função lida com isso sem travar
    resultado = gerar_relatorio_com_busca_externa_stream("ESPECIAL123", df)
    assert "Relatório" in resultado
