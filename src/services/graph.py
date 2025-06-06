import ipeadatapy as ipea
import time
import pandas as pd
import plotly.graph_objects as go

def obter_dados_serie(codigo_serie):
    """
    Obtém a série estatística do IPEA para o código informado e os últimos 'Último anos' Último anos.
    """
    current_year = time.localtime().tm_year
    return ipea.timeseries(codigo_serie, yearGreaterThan=current_year - 6)

def filtrar_dados_periodo(codigo_serie, periodo):
    """
    Filtra o DataFrame para retornar dados dos períodos:
    'Última semana', 'Último mês', 'Últimos 6 meses', 'Último ano', 'Últimos 3 anos', 'Últimos 5 anos'
    """
    dados_serie = obter_dados_serie(codigo_serie)
    dados_serie["RAW DATE"] = pd.to_datetime(dados_serie["RAW DATE"])
    ultima_data = dados_serie["RAW DATE"].max()

    if periodo == "Última semana":
        return dados_serie[dados_serie["RAW DATE"] >= (ultima_data - pd.Timedelta(days=7))]
    elif periodo == "Último mês":
        return dados_serie[dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(months=1))]
    elif periodo == "Últimos 6 meses":
        return dados_serie[dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(months=6))]
    elif periodo == "Último ano":
        return dados_serie[dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(years=1))]
    elif periodo == "Últimos 3 anos":
        return dados_serie[dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(years=3))]
    elif periodo == "Últimos 5 anos":
        return dados_serie
    else:
        raise ValueError("Período inválido. Use: Última semana, Último mês, Últimos 6 meses, Último ano, Últimos 3 anos, Últimos 5 anos.")

def calcular_percentual_aumento_por_periodo(codigo_serie):
    """
    Calcula o percentual de aumento para cada período definido.
    Retorna um array com os percentuais para: Última semana, Último mês, Últimos 6 meses, Último ano, Últimos 3 anos, Últimos 5 anos.
    """
    periodos = ["Última semana", "Último mês", "Últimos 6 meses", "Último ano", "Últimos 3 anos", "Últimos 5 anos"]
    percentuais = []
    for periodo in periodos:
        dados_filtrados = filtrar_dados_periodo(codigo_serie, periodo)
        if not dados_filtrados.empty:
            valor_inicial = dados_filtrados.iloc[0,5]
            valor_final = dados_filtrados.iloc[-1,5]
            if valor_inicial != 0:
                percentual = round(((valor_final - valor_inicial) / abs(valor_inicial)) * 100, 2)
            else:
                percentual = float('nan')
        else:
            percentual = float('nan')
        percentuais.append(percentual)
    return percentuais

def plotar_grafico_periodo(codigo_serie, periodo):
    """
    Plota um gráfico de linha usando Plotly para o período selecionado.
    O eixo x é a data e o eixo y é o valor em reais.
    A cor do gráfico é verde se o percentual de aumento for positivo, vermelho caso contrário.
    """
    medida = "(" + ipea.metadata(codigo_serie)['MEASURE'].iloc[0] + ")"
    dados_filtrados = filtrar_dados_periodo(codigo_serie, periodo).copy()
    dados_filtrados = dados_filtrados.rename(
        columns={"RAW DATE": "Data", "VALUE " + medida: "Valor " + medida}
    )
    
    if not dados_filtrados.empty:
        valor_inicial = dados_filtrados.iloc[0,5]
        valor_final = dados_filtrados.iloc[-1,5]
        if valor_inicial != 0:
            percentual = ((valor_final - valor_inicial) / abs(valor_inicial)) * 100
        else:
            percentual = float('nan')
    else:
        percentual = float('nan')

    cor = "#2BB17A" if percentual >= 0 else "#f0423c"

    fig_pontos = go.Figure()
    fig_pontos.add_trace(go.Scatter(
        x=dados_filtrados["Data"],
        y=dados_filtrados["Valor " + medida],
        mode='markers+lines',
        marker=dict(color=cor, size=4),
        line=dict(color=cor),
        name="Valores"
    ))
    fig_pontos.update_layout(
        xaxis_title="Data",
        yaxis_title="Valor " + medida,
        height=600,
        plot_bgcolor="#072333",        # Cor de fundo do gráfico
        paper_bgcolor="#072333",       # Cor de fundo do contêiner
        font=dict(color="white"),      # Cor dos textos
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        )
    )
    return fig_pontos

