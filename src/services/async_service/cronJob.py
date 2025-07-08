import pandas as pd
import re
import os
import ipeadatapy as ipea
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from dotenv import load_dotenv  # <-- 1. IMPORTADO

from src.data.connect import supabase
from src.data.operacoes_bd import alterar_ultima_atualizacao, alterar_ultima_checagem, alterar_ultimo_alerta

# --- Bloco de Configuração Segura ---
load_dotenv()  # <-- 2. CARREGA as variáveis do arquivo .env
# --- Fim do Bloco de Configuração ---


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
    # --- 3. BUSCA SEGURA das configurações de SMTP a partir do .env ---
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port_str = os.getenv("SMTP_PORT")
    smtp_login = os.getenv("SMTP_LOGIN")
    smtp_password = os.getenv("SMTP_PASSWORD")
    mail_from = os.getenv("MAIL_FROM")

    # --- 4. VALIDAÇÃO das credenciais ---
    if not all([smtp_server, smtp_port_str, smtp_login, smtp_password, mail_from]):
        raise ValueError("Uma ou mais configurações de e-mail (SMTP) não foram encontradas no arquivo .env.")

    smtp_port = int(smtp_port_str)  # Converte a porta para inteiro

    # HTML com identidade visual GOV INSIGHTS (código do corpo do e-mail omitido para brevidade, permanece igual)
    if margem >= 0:
        cor_variacao = "#27AE60"
    else:
        cor_variacao = "#E53E3E"
    html_content = f"""
    <html>
        ... (Seu código HTML aqui, sem alterações) ...
    </html>
    """

    # Criar a mensagem multipart/related
    mensagem = MIMEMultipart('related')
    mensagem['Subject'] = f"Alerta da Série #{codigo_serie}"
    mensagem['From'] = mail_from  # <-- 5. USA a variável segura
    mensagem['To'] = email_usuario

    # Criar o container multipart/alternative (texto + html)
    msg_alternative = MIMEMultipart('alternative')
    mensagem.attach(msg_alternative)

    # Texto plano para clientes que não suportam html (opcional)
    texto_plano = "Seu cliente de email não suporta HTML."
    msg_text = MIMEText(texto_plano, 'plain')
    msg_alternative.attach(msg_text)

    # Corpo html
    msg_html = MIMEText(html_content, 'html')
    msg_alternative.attach(msg_html)

    # Anexar imagem da logo embutida
    logo_path = 'src/services/async_service/assets/icon.png'
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as img:
            logo = MIMEImage(img.read())
            logo.add_header('Content-ID', '<logo_gov_insights>')
            mensagem.attach(logo)

    # Enviar o e-mail
    try:
        # <-- 6. USA as variáveis seguras para conectar e logar
        servidor = smtplib.SMTP(smtp_server, smtp_port)
        servidor.starttls()
        servidor.login(smtp_login, smtp_password)
        servidor.sendmail(mensagem['From'], [mensagem['To']], mensagem.as_string())
        servidor.quit()
        print(f"✅ E-mail de alerta para '{email_usuario}' sobre a série '{codigo_serie}' enviado com sucesso.")
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ Erro de autenticação SMTP. Verifique as credenciais no arquivo .env.")
        return False
    except Exception as e:
        print(f"❌ Falha ao enviar e-mail: {e}")
        return False

# O resto do seu código (funções enviar_alerta e verificar_atualizacao_series) permanece exatamente o mesmo.
# ... (código das outras funções omitido, pois não há alterações neles) ...

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
            try:
                dataframe_serie = ipea.timeseries(serie["codigo_serie"]).iloc[::-1]
            except:
                continue

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
