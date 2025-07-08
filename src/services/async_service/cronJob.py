import pandas as pd
import re
import os
import ipeadatapy as ipea
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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

    # Configuração SMTP da Brevo
    smtp_server = "smtp-relay.brevo.com"
    smtp_port = 587
    smtp_login = "905867001@smtp-brevo.com"  # Login SMTP da Brevo
    smtp_password = "h92HcFkdMgUwVySJ"  # Sua SMTP Key

    # HTML com identidade visual GOV INSIGHTS
    if margem >= 0:
        cor_variacao = "#27AE60"
    else:
        cor_variacao = "#E53E3E"
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #ff0000;
                color: #333;
                margin: 0;
                padding: 40px 0;
            }}
            .email-container {{
                max-width: 480px;
                margin: 0 auto;
                background-color: #f3ffff;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                overflow: hidden;
            }}
            .logo-container {{
                background-color: #f0f7ff;
                padding: 15px 30px;
                display: flex;
                align-items: center;
            }}
            .logo {{
                width: 80px;  
                height: auto;
            }}
            .content {{
                padding: 30px;
                text-align: left;
            }}
            .title {{
                font-size: 20px;
                color: #135730;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .alert {{
                background-color: #f0f7ff;
                border-left: 5px solid #27AE60;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
            }}
            .variacao {{
                color: {cor_variacao};
                font-weight: bold;
                font-size: 18px;
            }}
            .button {{
                display: block;
                width: fit-content;
                margin: 25px auto 0 auto;
                background-color: #27AE60;
                color: white !important;
                padding: 12px 24px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                text-decoration: none;
            }}
            .footer {{
                font-size: 12px;
                color: #aaa;
                text-align: center;
                padding: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="logo-container">
                <img src="cid:logo_gov_insights" alt="GOV INSIGHTS" class="logo">
            </div>
            <div class="content">
                <div class="title">Alerta de Variação Econômica</div>
                <div class="alert">
                    <p>Série monitorada: <strong>{codigo_serie}</strong></p>
                    <p>Alteração detectada: <span class="variacao">{'+' if margem > 0 else ''}{margem:.2f}%</span></p>
                </div>
                <p>Este alerta foi gerado automaticamente pelo GOV INSIGHTS com base no monitoramento contínuo.</p>
                <ul>
                    <li>Consulte detalhes no painel de análise</li>
                    <li>Compare com outras séries</li>
                    <li>Realize exportação de dados</li>
                    <li><strong>Ação recomendada:</strong> em até 48h</li>
                </ul>
                <a href="https://painel.govinsights.com.br/analise?serie={codigo_serie}" class="button">Ver análise completa</a>
            </div>
            <div class="footer">
                GOV INSIGHTS • SQUAD 10<br>
                Este é um e-mail automático, não responda.<br>
                <a href="https://govinsights.com.br/unsubscribe?email={email_usuario}" style="color: #888;">Cancelar inscrição</a>
            </div>
        </div>
    </body>
    </html>
    """

    # Criar a mensagem multipart/related
    mensagem = MIMEMultipart('related')
    mensagem['Subject'] = f"Alerta da Série #{codigo_serie}"
    mensagem['From'] = 'govinsightstests@gmail.com'
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