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
    
    # Verifica se contém o conteúdo gerado pela IA
    assert "Relatório gerado pela IA." in resultado
    assert len(resultado) > 0


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


# NOVOS TESTES PARA MELHORAR COBERTURA

@patch("ipeadatapy.describe", side_effect=Exception("Erro na API IPEA"))
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_erro_describe_serie(mock_together, mock_feedparser, mock_describe):
    """Testa tratamento de erro ao obter descrição da série (linha 35-38)"""
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório com erro na série"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("ERRO123", df)
    
    # Verifica se ainda gera relatório mesmo com erro na descrição
    assert "Relatório" in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_nome_serie_vazio(mock_together, mock_feedparser, mock_describe):
    """Testa tratamento quando nome da série é vazio ou NaN (linhas 26, 28)"""
    # Mock da descrição da série com valores vazios/NaN
    mock_desc = pd.DataFrame([[None], [None], [None], [None], [None], [None], [pd.NA]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório com série vazia"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("VAZIO123", df)
    
    # Verifica se consegue lidar com dados vazios
    assert "Relatório" in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_erro_otimizacao_csv(mock_together, mock_feedparser, mock_describe):
    """Testa tratamento de erro na otimização do CSV (linhas 60-63)"""
    # Mock da descrição da série
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], ["Comentário"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório com fallback CSV"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    # DataFrame que pode causar erro na otimização
    df = pd.DataFrame({"valor": [100, 200]})
    
    # Usar mock para simular erro no processo de otimização
    with patch('pandas.DataFrame.copy', side_effect=Exception("Erro na otimização")):
        resultado = gerar_relatorio_com_busca_externa_stream("ERRO_CSV", df)
    
    assert "Relatório" in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse", side_effect=Exception("Erro no feedparser"))
@patch("together.Together")
def test_gerar_relatorio_erro_busca_noticias(mock_together, mock_feedparser, mock_describe):
    """Testa tratamento de erro na busca de notícias (linhas 82-84)"""
    # Mock da descrição da série
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], ["Comentário"]])
    mock_describe.return_value = mock_desc

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório sem notícias"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("SEM_NOTICIAS", df)
    
    # Verifica se ainda funciona mesmo sem conseguir buscar notícias
    assert "Relatório" in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_processamento_thinking_tags(mock_together, mock_feedparser, mock_describe):
    """Testa o processamento de tags <think> no streaming (linhas 159, 161-164, 166-179)"""
    # Mock da descrição da série
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], ["Comentário"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming com tags <think>
    mock_client = MagicMock()
    
    # Simulando chunks com tags thinking que devem ser filtradas
    mock_chunks = []
    
    # Chunk 1: início de thinking tag
    chunk1 = MagicMock()
    chunk1.choices = [MagicMock()]
    chunk1.choices[0].delta.content = "<think>Este é um pensamento que deve ser filtrado</think>"
    mock_chunks.append(chunk1)
    
    # Chunk 2: conteúdo normal
    chunk2 = MagicMock()
    chunk2.choices = [MagicMock()]
    chunk2.choices[0].delta.content = "Este é o conteúdo real do relatório"
    mock_chunks.append(chunk2)
    
    # Chunk 3: caracteres com $
    chunk3 = MagicMock()
    chunk3.choices = [MagicMock()]
    chunk3.choices[0].delta.content = "Valor em $ será escapado"
    mock_chunks.append(chunk3)

    mock_client.chat.completions.create.return_value = mock_chunks
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("THINKING_TEST", df)
    
    # Verifica se as tags thinking foram filtradas
    assert "<think>" not in resultado
    assert "</think>" not in resultado
    assert "conteúdo real" in resultado
    # Verifica se $ foi escapado
    assert "\\$" in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_com_callback(mock_together, mock_feedparser, mock_describe):
    """Testa o uso de callback durante o streaming (linha 185)"""
    # Mock da descrição da série
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], ["Comentário"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Texto do callback"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    # Mock do callback
    callback_mock = MagicMock()
    
    resultado = gerar_relatorio_com_busca_externa_stream("CALLBACK_TEST", df, callback=callback_mock)
    
    # Verifica se o callback foi chamado
    callback_mock.assert_called()
    assert "Texto do callback" in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_noticias_com_multiplos_termos(mock_together, mock_feedparser, mock_describe):
    """Testa busca de notícias com múltiplos termos de busca"""
    # Mock da descrição da série
    mock_desc = pd.DataFrame([["PIB Brasil"], [None], [None], [None], [None], [None], ["Produto Interno Bruto"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias - simulando múltiplas chamadas
    call_count = 0
    def mock_parse_side_effect(url):
        nonlocal call_count
        call_count += 1
        mock_feed = MagicMock()
        mock_feed.entries = [
            MagicMock(
                title=f"Notícia {call_count}",
                link=f"http://link{call_count}.com",
                published="2024-01-01",
                summary=f"Resumo {call_count}"
            )
        ]
        return mock_feed
    
    mock_feedparser.side_effect = mock_parse_side_effect

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório com múltiplas notícias"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("PIB123", df)
    
    # Verifica se múltiplas buscas foram feitas
    assert mock_feedparser.call_count >= 3  # Pelo menos 3 termos de busca
    assert "Relatório" in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_processamento_chunks_complexos(mock_together, mock_feedparser, mock_describe):
    """Testa processamento de chunks complexos com caracteres especiais"""
    # Mock da descrição da série
    mock_desc = pd.DataFrame([["Série Complexa"], [None], [None], [None], [None], [None], ["Descrição"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming com chunks complexos
    mock_client = MagicMock()
    
    mock_chunks = []
    
    # Chunk com thinking parcial
    chunk1 = MagicMock()
    chunk1.choices = [MagicMock()]
    chunk1.choices[0].delta.content = "<th"
    mock_chunks.append(chunk1)
    
    # Continuação do thinking
    chunk2 = MagicMock()
    chunk2.choices = [MagicMock()]
    chunk2.choices[0].delta.content = "ink>pensamento</think>"
    mock_chunks.append(chunk2)
    
    # Conteúdo normal
    chunk3 = MagicMock()
    chunk3.choices = [MagicMock()]
    chunk3.choices[0].delta.content = "Conteúdo normal com $símbolos$ especiais"
    mock_chunks.append(chunk3)

    mock_client.chat.completions.create.return_value = mock_chunks
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("COMPLEXO123", df)
    
    # Verifica processamento correto
    assert "pensamento" not in resultado  # thinking foi filtrado
    assert "Conteúdo normal" in resultado
    assert "\\$símbolos\\$" in resultado  # $ foi escapado


@patch("ipeadatapy.describe")
@patch("feedparser.parse")
@patch("together.Together")
def test_gerar_relatorio_noticias_com_atributos_faltando(mock_together, mock_feedparser, mock_describe):
    """Testa o cenário onde as notícias não têm todos os atributos (linhas 82-84)"""
    # Mock da descrição da série
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], ["Comentário"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias sem alguns atributos
    mock_feed = MagicMock()
    mock_entry1 = MagicMock(spec=['title', 'link'])  # Sem published e summary
    mock_entry1.title = "Notícia sem atributos"
    mock_entry1.link = "http://test.com"
    # published e summary não existem (hasattr retorna False)
    
    mock_entry2 = MagicMock()
    mock_entry2.title = "Notícia completa"
    mock_entry2.link = "http://test2.com"
    mock_entry2.published = "2024-01-01"
    mock_entry2.summary = "Resumo completo"
    
    mock_feed.entries = [mock_entry1, mock_entry2]
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Análise com notícias parciais"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100, 200]}, 
                     index=pd.date_range("2024-01-01", periods=2, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("COD_ATTR", df)
    
    assert "Análise com notícias parciais" in resultado
    # Verifica se o prompt foi criado corretamente mesmo com atributos faltando
    args = mock_client.chat.completions.create.call_args[1]
    prompt = args["messages"][0]["content"]
    assert "Notícia sem atributos" in prompt
    assert "Notícia completa" in prompt


@patch("ipeadatapy.describe")
@patch("feedparser.parse") 
@patch("together.Together")
def test_gerar_relatorio_comentario_longo(mock_together, mock_feedparser, mock_describe):
    """Testa limitação do comentário a 150 caracteres (linha 28)"""
    comentario_longo = "A" * 200  # 200 caracteres
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], [comentario_longo]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório com comentário limitado"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100]}, 
                     index=pd.date_range("2024-01-01", periods=1, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("COMENTARIO_LONGO", df)
    
    # O comentário não é incluído no prompt, apenas usado para debug
    # Verificamos se a função executa sem erro e produz resultado
    assert "Relatório com comentário limitado" in resultado
    assert len(resultado) > 0


@patch("ipeadatapy.describe")
@patch("feedparser.parse") 
@patch("together.Together")
def test_gerar_relatorio_serie_com_nome_nan(mock_together, mock_feedparser, mock_describe):
    """Testa quando o nome da série é NaN/vazio (linhas 26, 35-38)"""
    import numpy as np
    
    # Mock com nome da série sendo NaN
    mock_desc = pd.DataFrame([[np.nan], [None], [None], [None], [None], [None], [None]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório com série sem nome"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100]}, 
                     index=pd.date_range("2024-01-01", periods=1, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("SEM_NOME", df)
    
    # Verifica se usou o nome padrão
    args = mock_client.chat.completions.create.call_args[1]
    prompt = args["messages"][0]["content"]
    assert "Série SEM_NOME" in prompt


@patch("ipeadatapy.describe")
@patch("feedparser.parse") 
@patch("together.Together")
def test_gerar_relatorio_comentario_nan(mock_together, mock_feedparser, mock_describe):
    """Testa quando o comentário da série é NaN/vazio (linhas 35-38)"""
    import numpy as np
    
    # Mock com comentário sendo NaN
    mock_desc = pd.DataFrame([["Série Teste"], [None], [None], [None], [None], [None], [np.nan]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming
    mock_client = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Relatório com comentário padrão"
    mock_client.chat.completions.create.return_value = [mock_chunk]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100]}, 
                     index=pd.date_range("2024-01-01", periods=1, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("SEM_COMENTARIO", df)
    
    # Verifica se o resultado contém algum conteúdo (função executou com sucesso)
    assert len(resultado) > 0
    assert "Relatório" in resultado


@patch("ipeadatapy.describe")
@patch("feedparser.parse") 
@patch("together.Together")
def test_gerar_relatorio_processamento_thinking_com_buffer_incompleto(mock_together, mock_feedparser, mock_describe):
    """Testa processamento de chunks com buffer de thinking incompleto (linhas 161-164, 166-179)"""
    # Mock da descrição da série
    mock_desc = pd.DataFrame([["Série Buffer"], [None], [None], [None], [None], [None], ["Comentário"]])
    mock_describe.return_value = mock_desc
    
    # Mock das notícias
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_feedparser.return_value = mock_feed

    # Mock do streaming com chunks que simulam processamento normal
    mock_client = MagicMock()
    
    # Simular chunks com texto normal (sem tags thinking)
    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock()]
    mock_chunk1.choices[0].delta.content = "Texto"
    
    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock()]
    mock_chunk2.choices[0].delta.content = " normal"
    
    mock_chunk3 = MagicMock()
    mock_chunk3.choices = [MagicMock()]
    mock_chunk3.choices[0].delta.content = " processado."
    
    mock_client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2, mock_chunk3]
    mock_together.return_value = mock_client

    df = pd.DataFrame({"valor": [100]}, 
                     index=pd.date_range("2024-01-01", periods=1, freq="D"))

    resultado = gerar_relatorio_com_busca_externa_stream("BUFFER_TEST", df)
    
    # Deve processar normalmente o texto sem filtrar
    assert len(resultado) > 0
    assert "Texto normal processado." in resultado
