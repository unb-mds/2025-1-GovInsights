from reportlab.lib.validators import isNumber

from src.data.connect import supabase

# Quando for inserir a serie no BD o campo de ultima atualizacao diz respeito a última atualização da série no IPEA
def inserir_nova_serie(codigo_serie: str, email_usuario: str, margem: str, ultima_atualizacao: str):
    """
    Realiza a inserção dos dados parametrizados na tabela "series" do banco de dados no Supabase.

    :param codigo_serie: str - Código da série.
    :param email_usuario: str - Email do usuário.
    :param margem: str - Margem mínima de envio de alerta.
    :param ultima_atualizacao: str - Ultima atualizacao da série no IPEA.
    :return: dict - Caso a inserção seja bem sucedida, é retornado uma lista contendo um dicionario com os dados inseridos.
    :raises ValueError: Se algum dos parâmetros obrigatórios for vazio ou None.
    :raises Exception: Para erros genéricos que podem ocorrer na inserção no Supabase.
    """
    if codigo_serie == "" or email_usuario == "" or isNumber(margem) == False or ultima_atualizacao == "":
        raise ValueError('Dados insuficientes.')

    try:
        resposta = (
            supabase.table("series")
            .insert({
                "codigo_serie": codigo_serie,
                "email_usuario": email_usuario,
                "margem": margem,
                "ultima_atualizacao": ultima_atualizacao
            })
            .execute()
        )

        return resposta.data

    except Exception as error:
        raise error

def alterar_ultima_atualizacao(data: str, idSerie: str):
    """
    Altera a coluna que diz respeito a ultima atualização da série.

    :param data: str - Recebe a nova data.
    :param idSerie: str - Recebe o id da série do IPEA.
    :return: dict - Caso a atualização seja bem sucedida, é retornado uma lista contendo um dicionario com os dados da serie.
    :raise Exception: Caso ocorra algum erro.
    """
    if (data == "" or idSerie == ""):
        raise ValueError('Dados insuficientes.')
    try:
        resposta = supabase.table("series").update({"ultima_atualizacao": data}).eq("id", idSerie).execute()
        return resposta.data
    except Exception as error:
        raise error

def alterar_ultimo_alerta(data: str, idSerie: str):
    """
        Altera a coluna que diz respeito ao ultimo alerta enviado da serie.

        :param data: str - Recebe a nova data.
        :param idSerie: str - Recebe o id da série do IPEA.
        :return: dict - Caso a atualização seja bem sucedida, é retornado uma lista contendo um dicionario com os dados da serie.
        :raise Exception: Caso ocorra algum erro.
    """
    if (data == "" or idSerie == ""):
        raise ValueError('Dados insuficientes.')
    try:
        resposta = supabase.table("series").update({"ultimo_alerta": data}).eq("id", idSerie).execute()
        return resposta.data
    except Exception as error:
        raise error

def alterar_ultima_checagem(data: str, idSerie: str):
    """
        Altera a coluna que diz respeito a ultima checagem da série.

        :param data: str - Recebe a nova data.
        :param idSerie: str - Recebe o id da série do IPEA.
        :return: dict - Caso a atualização seja bem sucedida, é retornado uma lista contendo um dicionario com os dados da serie.
        :raise Exception: Caso ocorra algum erro.
    """
    if (data == "" or idSerie == ""):
        raise ValueError('Dados insuficientes.')
    try:
        resposta = supabase.table("series").update({"ultima_checagem": data}).eq("id", idSerie).execute()
        return resposta.data
    except Exception as error:
        raise error