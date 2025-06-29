import pandas as pd

def gerar_pdf(codSerie: str, dfSerie: pd.DataFrame, iaText: str):
    import matplotlib.pyplot as plt
    import tempfile
    from xhtml2pdf import pisa
    import markdown
    """
    :arg codSerie: código da série do IPEA
    :arg dfSerie: dataframe da série do IPEA
    :arg iaText: relatório em markdown gerado pelo DeepSeek

    :return retorna um PDF criado com base nos dados informados sobre a série do IPEA
    """

    if codSerie == "" or dfSerie.empty or iaText == "":
        raise Exception("Parametros insuficientes.")

    # Preparar dataframe para o gráfico
    dataframe = pd.DataFrame(dict(VALUE=dfSerie.iloc[:, -1]))

    # Criar gráfico matplotlib
    fig, ax = plt.subplots()
    ax.plot(dataframe.index, dataframe["VALUE"])
    ax.set_xlabel("data")
    ax.set_ylabel("valor")

    # Salvar imagem do gráfico em arquivo temporário
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
        fig.savefig(tmp_img.name)
        img_path = tmp_img.name

    # Converter markdown do iaText para HTML
    ia_html = markdown.markdown(iaText)

    # Criar HTML completo para o PDF com CSS atualizado
    html = f"""
            <html>
                <head>
                    <style>
                        h1, h3, h4, body, p {{font-family: Helvetica; color: black;}}
                        h1 {{ font-size: 36px; }}
                        h3 {{ font-size: 24px; }}
                        h4 {{ font-size: 20px; }}
                        body, p {{ margin: 30px; font-size: 16px; line-height: 1.5; }}
                        img {{ max-width: 100%; height: auto; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <h1>GovInsights</h1>
                    <h3>Dados da Série {codSerie} do IPEA</h3>
                    <img src="{img_path}"/>
                    {ia_html}
                </body>
            </html>
            """

    # Salvar PDF em arquivo temporário
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        pdf_path = tmp_pdf.name
        pisa_status = pisa.CreatePDF(html, dest=tmp_pdf)

    if pisa_status.err:
        raise Exception("PDF não foi gerado.")

    return pdf_path
