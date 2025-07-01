import pytest
import pandas as pd
from src.services.ia import gerar_relatorio
from unittest.mock import patch, MagicMock


def test_gerar_relatorio_parametros_invalidos():
    with pytest.raises(Exception, match="Parametros incorretos."):
        gerar_relatorio("COD001", pd.DataFrame())

    df = pd.DataFrame({"ano": [2020], "valor": [100]})
    with pytest.raises(Exception, match="Parametros incorretos."):
        gerar_relatorio("", df)


@patch("src.services.ia.Together")
def test_gerar_relatorio_sucesso(mock_together):
    df = pd.DataFrame({"ano": range(2000, 2100), "valor": [i for i in range(100)]})
    df.index.name = "ano"

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Relatório gerado pela IA."
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_together.return_value = mock_client

    resultado = gerar_relatorio("COD123", df)
    assert resultado == "Relatório gerado pela IA."


@patch("src.services.ia.Together", side_effect=Exception("Falha de rede"))
def test_gerar_relatorio_erro_api(mock_together):
    df = pd.DataFrame({"ano": range(2000, 2100), "valor": [i for i in range(100)]})
    df.index.name = "ano"

    with pytest.raises(Exception, match="Conexão com IA falhou."):
        gerar_relatorio("COD321", df)


# NOVOS TESTES ADICIONADOS

@patch("src.services.ia.Together")
def test_gerar_relatorio_formatacao_prompt(mock_together):
    df = pd.DataFrame({"ano": [2020, 2021], "valor": [100, 200]})
    df.index.name = "ano"

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Relatório"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_together.return_value = mock_client

    # Captura o conteúdo enviado no prompt
    with patch("src.services.ia.re") as mock_re:
        gerar_relatorio("SERIE123", df)

        args = mock_client.chat.completions.create.call_args[1]
        prompt = args["messages"][0]["content"]
        assert "SERIE123" in prompt
        assert "Segue os dados da série no formato CSV:" in prompt
        assert "Resumo sobre o que se trata a série" in prompt
        assert "ano,valor" in prompt


@patch("src.services.ia.Together")
def test_gerar_relatorio_processamento_dataframe(mock_together):
    df = pd.DataFrame({
        "valor": list(range(150))
    }, index=pd.date_range("2020-01-01", periods=150, freq="D"))

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Relatório"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_together.return_value = mock_client

    gerar_relatorio("COD999", df)

    args = mock_client.chat.completions.create.call_args[1]
    prompt = args["messages"][0]["content"]
    # Verifica se CSV contém no máximo 100 linhas
    assert prompt.count("\n") <= 120  # margem maior para quebras de linha

    # Verifica ordenação (mais recente primeiro)
    assert str(df.index[-1].date()) in prompt


@patch("src.services.ia.Together")
def test_gerar_relatorio_processamento_dataframe(mock_together):
    import re

    df = pd.DataFrame({
        "valor": list(range(150))
    }, index=pd.date_range("2020-01-01", periods=150, freq="D"))

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Relatório"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_together.return_value = mock_client

    gerar_relatorio("COD999", df)

    args = mock_client.chat.completions.create.call_args[1]
    prompt = args["messages"][0]["content"]

    # Extrai CSV do prompt
    csv_match = re.search(r"Segue os dados da série no formato CSV:\s*(.*)", prompt, re.DOTALL)
    assert csv_match is not None

    csv_part = csv_match.group(1).strip()
    csv_lines = csv_part.splitlines()

    # Verifica se tem 101 linhas: 1 header + 100 dados
    assert len(csv_lines) == 101

    # Verifica ordenação - última data (mais recente) deve estar no início do CSV
    # DataFrame é invertido na função (mais recente primeiro)
    first_data_date = csv_lines[1].split(",")[0]
    expected_date = df.index[-1].strftime("%Y-%m-%d")
    assert first_data_date == expected_date



def test_gerar_relatorio_dados_especiais():
    df = pd.DataFrame({
        "col1": [None, "çãó", 3.14],
        "col2": [1, None, "texto"]
    })
    df.index.name = "índice"

    # Validação - Se a função lida com isso sem travar
    with patch("src.services.ia.Together") as mock_together:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Relatório com dados especiais"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_together.return_value = mock_client

        resultado = gerar_relatorio("ESPECIAL123", df)
        assert "Relatório" in resultado
