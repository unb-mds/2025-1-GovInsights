import ipeadatapy as ipea
import time
import pandas as pd
import plotly.graph_objects as go
import numpy as np # Importar numpy para np.nan

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

        # Garante que self.dados_periodos é sempre inicializado como um dicionário
        self.dados_periodos = {}
        self.__filtrar_dados_periodo() # Este método agora popula self.dados_periodos com segurança

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
            # Tenta buscar 25 anos de dados para ter margem para os períodos mais longos
            dados_serie = ipea.timeseries(codigo_serie, yearGreaterThan=current_year - 25)
            if dados_serie.empty:
                print(f"Aviso: Nenhuns dados encontrados para a série {codigo_serie}.")
            return dados_serie
        except Exception as e:
            print(f"Erro ao obter dados da série {codigo_serie}: {e}")
            # Retorna um DataFrame vazio em caso de erro para evitar quebrar o app
            return pd.DataFrame()

    def __filtrar_dados_periodo(self):
        """
        Filtra o DataFrame para retornar dados dos períodos e armazena em um dicionário.
        """
        print("graph.py: Processando dados da série por período...")
        # Garante que dados_periodos seja sempre um dicionário
        self.dados_periodos = {}

        if self.dados_serie.empty:
            print("Aviso: dados_serie está vazio, não é possível filtrar por período.")
            return

        # Converter a coluna de data e definir como índice para facilitar o fatiamento
        self.dados_serie["RAW DATE"] = pd.to_datetime(self.dados_serie["RAW DATE"], utc=True)
        # Sort by date to ensure .max() and slicing work correctly
        self.dados_serie = self.dados_serie.sort_values(by="RAW DATE").set_index("RAW DATE")
        ultima_data = self.dados_serie.index.max() # Pega a última data do índice

        # Definição dos períodos para cada frequência
        if self.frequencia == "Diária":
            periods = {
                "Última semana": '7D',
                "Último mês": '1M',
                "Últimos 6 meses": '6M',
                "Último ano": '1Y',
                "Últimos 3 anos": '3Y',
                "Últimos 5 anos": '5Y'
            }
        elif self.frequencia == "Mensal" or self.frequencia == "Trimestral":
            periods = {
                "Últimos 6 meses": '6M',
                "Último ano": '1Y',
                "Últimos 2 anos": '2Y',
                "Últimos 3 anos": '3Y',
                "Últimos 5 anos": '5Y',
                "Últimos 10 anos": '10Y'
            }
        elif self.frequencia == "Anual":
            periods = {
                "Últimos 5 anos": '5Y',
                "Últimos 10 anos": '10Y',
                "Últimos 20 anos": '20Y'
            }
        else:
            print(f"Aviso: Frequência '{self.frequencia}' não reconhecida para filtrar dados por período.")
            return

        # Popula dados_periodos com os DataFrames filtrados
        for name, offset in periods.items():
            start_date = ultima_data - pd.DateOffset(years=int(offset[:-1])) if 'Y' in offset else \
                         ultima_data - pd.DateOffset(months=int(offset[:-1])) if 'M' in offset else \
                         ultima_data - pd.Timedelta(days=int(offset[:-1])) if 'D' in offset else \
                         None # Fallback

            if start_date:
                # Usar loc com index para fatiamento de data baseado no índice
                self.dados_periodos[name] = self.dados_serie.loc[self.dados_serie.index >= start_date].reset_index()
            else:
                self.dados_periodos[name] = pd.DataFrame() # DataFrame vazio se offset não for reconhecido


    def __calcular_percentual_aumento_por_periodo(self):
        """
        Calcula o percentual de aumento para cada período definido.
        Retorna um dicionário com os percentuais cada período.
        """
        print("graph.py: Calculando percentuais de aumento por período...")
        percentuais = {}
        for periodo, dados in self.dados_periodos.items():
            if dados.empty or len(dados) < 2:
                percentuais[periodo] = None
                continue

            # Assuming the value column is the last one or at index 5 (adjust if needed)
            # It's safer to get the column by name if possible (e.g., 'VALUE (...)')
            try:
                # Assuming the actual value column is at index 5 (adjust if necessary)
                valor_inicial = dados.iloc[0, 5]
                valor_final = dados.iloc[-1, 5]
            except IndexError:
                # Fallback if DataFrame structure is unexpected
                percentuais[periodo] = None
                continue

            if valor_inicial == 0:
                percentual_aumento = np.nan # Usar np.nan para divisão por zero
            else:
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
        metadata = ipea.metadata(self.codigo_serie)
        # Garante que 'MEASURE' existe e não é NaN
        if not metadata.empty and 'MEASURE' in metadata.columns and not pd.isna(metadata['MEASURE'].iloc[0]):
            medida = "(" + metadata['MEASURE'].iloc[0] + ")"
        else:
            medida = "(Valor)" # Fallback

        graficos = {}
        for periodo, dados_filtrados in self.dados_periodos.items():
            # Acessa os percentuais já calculados
            percentual = self.percentuais.get(periodo, np.nan) # Usa .get para segurança
            cor = "#2BB17A" if percentual is not None and percentual >= 0 else "#f0423c" if percentual is not None else "#CCCCCC"

            # Renomeia colunas de forma segura, evitando criar novas se já existem
            dados = dados_filtrados.copy()
            # O nome da coluna de valor real pode variar, é melhor obtê-lo dinamicamente
            # Supondo que a coluna de valor é a que não é 'RAW DATE' ou o índice
            value_col = [col for col in dados.columns if col not in ['RAW DATE', dados.index.name]]
            value_col_name = value_col[0] if value_col else 'Valor' # Default to 'Valor'
            
            # Renomeia se 'RAW DATE' e a coluna de valor real ainda existem
            dados.rename(
                columns={"RAW DATE": "Data", value_col_name: f"Valor {medida}"},
                inplace=True, errors='ignore' # errors='ignore' previne erro se coluna não existe
            )
            
            # Garante que as colunas 'Data' e 'Valor {medida}' existem após renomeio
            if 'Data' not in dados.columns or f'Valor {medida}' not in dados.columns:
                print(f"Aviso: Colunas 'Data' ou 'Valor {medida}' não encontradas no DataFrame para o período {periodo}.")
                fig_pontos = go.Figure()
                fig_pontos.update_layout(title=f"Dados incompletos para {periodo}", height=600,
                                         plot_bgcolor='#101120', paper_bgcolor='#101120', font=dict(color='#cfcfcf'))
                graficos[periodo] = fig_pontos
                continue # Pula para o próximo período

            if not dados.empty:
                fig_pontos = go.Figure()
                fig_pontos.add_trace(go.Scatter(
                    x=dados["Data"],
                    y=dados[f"Valor {medida}"],
                    mode='markers+lines',
                    marker=dict(color=cor, size=4),
                    line=dict(color=cor),
                    name="Valores"
                ))
            else:
                fig_pontos = go.Figure()
                fig_pontos.add_annotation(
                    text=f"Dados não disponíveis para {periodo}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="#cfcfcf")
                )

            fig_pontos.update_layout(
                xaxis_title="Data",
                yaxis_title=f"Valor {medida}",
                height=600,
                plot_bgcolor='#101120',
                paper_bgcolor='#101120',
                font=dict(color='#cfcfcf'),
                xaxis=dict(gridcolor='#333333'),
                yaxis=dict(gridcolor='#333333')
            )
            graficos[periodo] = fig_pontos
        return graficos

    def __describe(self):
        """
        Retorna uma descrição da série estatística.
        """
        description_df = ipea.describe(self.codigo_serie)
        # Garante que o DataFrame de descrição tem o formato esperado, mesmo que vazio
        if description_df.empty:
            return pd.DataFrame({
                0: ["Descrição não disponível", "Órgão não disponível", "Tema não disponível",
                    "", "Unidade não disponível", "", "", "", "Fonte não disponível"]
            }).T
        return description_df
