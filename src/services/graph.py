import ipeadatapy as ipea
import time
import pandas as pd
import plotly.graph_objects as go

class timeSeries:
    """
    Classe para manipulação de séries.
    Gera objeto com os seguintes atributos:
    - codigo_serie: Código da série estatística.
    - dados_serie: DataFrame com os dados da série.
    - dados_periodos: Dicionário com os dados filtrados por período.
    - percentuais: Dicionário com os percentuais de aumento por período.
    - graficos: Dicionário com os gráficos de cada período.
    """
    
    def __init__(self, codigo_serie: str, frequencia: str):
        self.codigo_serie = codigo_serie
        self.frequencia = frequencia
        self.dados_serie = self.__obter_dados_serie(codigo_serie)
        self.__filtrar_dados_periodo()
        self.percentuais = self.__calcular_percentual_aumento_por_periodo()
        self.graficos = self.__plotar_graficos_periodos()
        self.descricao = self.__describe()
    
    def __obter_dados_serie(self, codigo_serie):
        """
        Obtém a série estatística do IPEA para o código informado e os últimos 'Último anos' Último anos.
        """
        print(f"graph.py: Obtendo dados da série: {codigo_serie}")
        try:
            current_year = time.localtime().tm_year
            dados_serie = ipea.timeseries(codigo_serie, yearGreaterThan=current_year - 21)
            return dados_serie
        except Exception as e:
            raise ValueError(f"Erro ao obter dados da série: {codigo_serie}") from e
    
    def __filtrar_dados_periodo(self):
        """
        Filtra o DataFrame para retornar dados dos períodos:
        semana, mês, 6 meses, ano, 3 anos e 5 anos e armazena em um dicionário.
        """
        print("graph.py: Processando dados da série por período...")
        self.dados_serie["RAW DATE"] = pd.to_datetime(self.dados_serie["RAW DATE"], utc=True)
        ultima_data = self.dados_serie["RAW DATE"].max()
        if self.frequencia == "Diária":
            self.dados_periodos = {
                "Última semana": self.dados_serie[self.dados_serie["RAW DATE"] >= (ultima_data - pd.Timedelta(days=7))],
                "Último mês": self.dados_serie[self.dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(months=1))],
                "Últimos 6 meses": self.dados_serie[self.dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(months=6))],
                "Último ano": self.dados_serie[self.dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(years=1))],
                "Últimos 3 anos": self.dados_serie[self.dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(years=3))],
                "Últimos 5 anos": self.dados_serie[self.dados_serie["RAW DATE"] >= (ultima_data - pd.DateOffset(years=5))]
            }
        elif self.frequencia == "Mensal":
            self.dados_periodos = {
                "Últimos 6 meses": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(months=6))],
                "Último ano": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=1))],
                "Últimos 2 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=2))],
                "Últimos 3 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=3))],
                "Últimos 5 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=5))],
                "Últimos 10 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=10))]
            }
        elif self.frequencia == "Trimestral":
            self.dados_periodos = {
                "Últimos 6 meses": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(months=6))],
                "Último ano": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=1))],
                "Últimos 2 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=2))],
                "Últimos 3 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=3))],
                "Últimos 5 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=5))],
                "Últimos 10 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=10))]
            }
        elif self.frequencia == "Anual":
            self.dados_periodos = {
                "Últimos 5 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=5))],
                "Últimos 10 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=10))],
                "Últimos 20 anos": self.dados_serie[self.dados_serie["RAW DATE"] > (ultima_data - pd.DateOffset(years=20))]
            }
        
    def __calcular_percentual_aumento_por_periodo(self):
        """
        Calcula o percentual de aumento para cada período definido.
        Retorna um dicionário com os percentuais cada período.
        """
        print("graph.py: Calculando percentuais de aumento por período...")
        percentuais = {}
        for periodo, dados in self.dados_periodos.items():
            if len(dados) < 2:
                percentuais[periodo] = None
                continue
            valor_inicial = dados.iloc[0,5]
            valor_final = dados.iloc[-1,5]
            percentual_aumento = round(((valor_final - valor_inicial) / valor_inicial) * 100, 2)
            percentuais[periodo] = percentual_aumento
        return percentuais
    
    def __plotar_graficos_periodos(self):
        """
        Plota gráficos de linha usando Plotly para todos os períodos disponíveis em self.dados_periodos.
        O eixo x é a data e o eixo y é o valor em reais.
        A cor do gráfico é verde se o percentual de aumento for positivo, vermelho caso contrário.
        Retorna um dicionário {periodo: figura_plotly}.
        """
        print("graph.py: Plotando gráficos para cada período...")
        medida = "(" + ipea.metadata(self.codigo_serie)['MEASURE'].iloc[0] + ")"
        graficos = {}
        for periodo, dados_filtrados in self.dados_periodos.items():
            dados = dados_filtrados.copy()
            dados = dados.rename(
                columns={"RAW DATE": "Data", "VALUE " + medida: "Valor " + medida}
            )
            if not dados.empty:
                valor_inicial = dados.iloc[0, dados.columns.get_loc("Valor " + medida)]
                valor_final = dados.iloc[-1, dados.columns.get_loc("Valor " + medida)]
                if valor_inicial != 0:
                    percentual = ((valor_final - valor_inicial) / abs(valor_inicial)) * 100
                else:
                    percentual = float('nan')
            else:
                percentual = float('nan')

            cor = "#2BB17A" if percentual >= 0 else "#f0423c"

            fig_pontos = go.Figure()
            fig_pontos.add_trace(go.Scatter(
                x=dados["Data"],
                y=dados["Valor " + medida],
                mode='markers+lines',
                marker=dict(color=cor, size=4),
                line=dict(color=cor),
                name="Valores"
            ))
            fig_pontos.update_layout(
                xaxis_title="Data",
                yaxis_title="Valor " + medida,
                height=600
            )
            graficos[periodo] = fig_pontos
        return graficos
    
    def __describe(self):
        """
        Retorna uma descrição da série estatística.
        """
        return ipea.describe(self.codigo_serie)
