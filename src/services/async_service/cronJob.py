import pandas as pd
import re
import ipeadatapy as ipea
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from src.data.connect import supabase
from src.data.operacoes_bd import alterar_ultima_atualizacao, alterar_ultima_checagem, alterar_ultimo_alerta


def calcular_margem(valores: pd.DataFrame):
    """
    Realiza o cálculo de porcentagem da margem de mudança da atualização mais recente em relação a sua anterior de uma série do IPEA

    :param valores: pd.DataFrame - Recebe um dataframe contendo SOMENTE a coluna dos valores de uma série do IPEA de forma descendente em relação ao tempo.
    :return: float - Retorna o valor calculado para a margem.
    """
    valorNovo = float(valores.iloc[0])
    valorAnterior = float(valores.iloc[1])
    margem = (((valorNovo - valorAnterior) / abs(valorAnterior)) * 100)
    return margem


def enviar_email(codigo_serie: str, email_usuario: str, margem: float):
    """
    Realiza o envio de um email contendo informações sobre a variação da margem de atualização de uma série do IPEA

    :param codigo_serie: Recebe o código da série do IPEA.
    :param email_usuario: Recebe o email do destinatário.
    :param margem: Recebe o valor de margem de atualição da série.
    :return: Retorna um valor booleano referente ao sucesso de envio do email.

    """
    texto = f"Houve um {'aumento' if margem > 0 else 'decréscimo'} de {margem:.2f}% na série {codigo_serie} de acordo com a nova atualizacação."

    # Configuração SMTP da Brevo
    smtp_server = "smtp-relay.brevo.com"
    smtp_port = 587
    smtp_login = "905867001@smtp-brevo.com"  # Login SMTP da Brevo
    smtp_password = "h92HcFkdMgUwVySJ"  # Sua SMTP Key

    # Criar a mensagem
    mensagem = MIMEMultipart()
    mensagem['Subject'] = f"Alerta da Série {codigo_serie}"
    mensagem['From'] = 'govinsightstests@gmail.com'
    mensagem['To'] = email_usuario

    # Corpo da mensagem
    corpo = MIMEText(texto, 'html')
    mensagem.attach(corpo)

    # Enviar o e-mail
    try:
        servidor = smtplib.SMTP(smtp_server, smtp_port)
        servidor.starttls()
        servidor.login(smtp_login, smtp_password)
        servidor.sendmail(mensagem['From'], [mensagem['To']], mensagem.as_string())
        servidor.quit()
        return True
    except:
        return False



def enviar_alerta(serie: dict, valores: pd.DataFrame, data: str):
    """
    :param serie: dict - Recebe um dicionário contendo informações sobre a série do BD.
    :param valores: pd.DataFrame - Recebe um dataframe contendo SOMENTE a coluna dos valores de uma série do IPEA de forma descendente em relação ao tempo.
    :param data: str - Recebe a nova data de atualização de último alerta.
    :return: boolean - Retorna verdadeiro caso todo o processo de alteração de data de ultimo alerta enviado e envio de email sejam concluidos, caso contrário falso.
    """
    try:
        margem = calcular_margem(valores)
        if int(serie["margem"]) <= abs(margem): #Verifica se o modulo da margem é maior ou igual que a margem mínima de atualização definida para envio de alertas
            alterar_ultimo_alerta(data, serie["id"])
            envio_email = enviar_email(serie["codigo_serie"], serie["email_usuario"], margem)
            return True if envio_email  else False
        else:
            return False
    except Exception as error:
        return False


def verificar_atualizacao_series():
    """
    Realiza uma verificação no BD onde é realizado a tentativa de envio de alerta caso a série sofra
    uma atualização de alerta ou seja uma nova série a ser alertada.

    Realiza atualizações no BD em relação a datas de última checagem, último alerta e última atualização.
    """

    try:
        # Armazena a data de hoje
        hoje = str(datetime.today().date())

        series = supabase.table("series").select("*").or_(f"ultima_checagem.neq.{hoje},ultima_checagem.is.null").execute()

        # Para cada serie na tabela series
        for serie in series.data:

            # Armazena o dataframe de atualizações da série de forma descendente
            dataframe_serie = ipea.timeseries(serie["codigo_serie"]).iloc[::-1]

            # Armazena a última coluna do dataframe que diz respeito aos valores
            valores = dataframe_serie.iloc[:, -1]

            #Realiza o envio de alerta de series novas no BD
            if serie["ultima_checagem"] is None:
                alterar_ultima_checagem(str(hoje), serie["id"])
                envio = enviar_alerta(serie, valores, str(hoje))
                if envio:
                    print(f"Envio de alerta para ID {serie['id']} bem sucedido.")
                else:
                    print(f"Envio de alerta para ID {serie['id']} mal sucedido.")

            else:

                # Armazena a data da última checagem realizada
                ultima_checagem = datetime.strptime(serie["ultima_checagem"], "%Y-%m-%d").date()

                # Atualiza a data de última checagem
                alterar_ultima_checagem(str(hoje), serie["id"])

                # Armazena a data da ultima atualização da serie no BD
                ultima_atualizacao_BD = datetime.strptime(serie["ultima_atualizacao"], "%Y-%m-%d").date()

                # Armazena a data de última atualização da série no IPEA
                ultima_atualizacao_IPEA = dataframe_serie.iloc[0]["RAW DATE"]
                ultima_atualizacao_IPEA = re.sub(r"[a-zA-Z].*", "", ultima_atualizacao_IPEA)
                ultima_atualizacao_IPEA = datetime.strptime(ultima_atualizacao_IPEA, "%Y-%m-%d").date()

                # Caso a serie não tenha sido checada hoje e a informação de última atualização da série no BD seja diferente do IPEA
                if ultima_atualizacao_BD != ultima_atualizacao_IPEA:

                    alterar_ultima_atualizacao(str(ultima_atualizacao_IPEA), serie["id"])
                    enviar_alerta(serie, valores, str(hoje))

    except Exception as error:
        raise error