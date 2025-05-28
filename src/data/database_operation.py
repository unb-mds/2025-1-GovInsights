from connect import supabase

def insert(codeSerie: str, userEmail: str, checkType: str):
    """
    Realiza a inserção dos dados fornecidos na tabela "series" do banco de dados no Supabase.

    :param codeSerie: Código do serie.
    :param userEmail: Email do usuário.
    :param checkType: Tipo de verificação a ser realizado pelo serviço assíncrono.
    :return: Caso a inserção seja bem sucedida, é retornado uma lista contendo um dict com os dados inseridos.
    :raises ValueError: Se algum dos parâmetros obrigatórios for vazio ou None.
    :raises Exception: Para erros genéricos que podem ocorrer na inserção no Supabase.
    """
    if not codeSerie or not userEmail or not checkType:
        raise ValueError('Dados insuficientes.')

    try:
        # Tentativa de inserção
        response = (
            supabase.table("series")
            .insert({
                "code_serie": codeSerie,
                "user_email": userEmail,
                "check_type": checkType
            })
            .execute()
        )

        return response.data  # Dados inseridos com sucesso

    except Exception as error:
        raise error