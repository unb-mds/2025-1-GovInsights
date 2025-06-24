import pandas as pd
import ipeadatapy as ipea
import plotly.express as px

@staticmethod
def load_global_variables():
    global metadata_economicos, temas_df
    metadata_economicos = ipea.metadata()
    print(f"metadata_economicos carregado com {metadata_economicos.shape[0]} linhas.")
    metadata_economicos = metadata_economicos[metadata_economicos['MEASURE'].str.contains("\\$")]
    print(f"Após filtrar medidas monetárias: {metadata_economicos.shape[0]} linhas.")
    metadata_economicos = metadata_economicos[~metadata_economicos['NAME'].str.contains('INATIVA', case=False, na=False)]
    print(f"Após remover séries inativas: {metadata_economicos.shape[0]} linhas.")
    metadata_economicos = metadata_economicos[~metadata_economicos['BIG THEME'].str.contains('Regional', case=False, na=False)]
    print(f"Após remover séries regionais: {metadata_economicos.shape[0]} linhas.")
    temas_df = ipea.themes()[['ID', 'NAME']].rename(columns={'ID': 'THEME CODE', 'NAME': 'THEME NAME'})
    print(f"temas_df carregado com {temas_df.shape[0]} linhas.")

if 'metadata_economicos' not in globals():
    load_global_variables()

class SearchService:
    """
    Serviço para busca e filtragem de séries estatísticas econômicas a partir de metadados.
    Métodos
    -------
    __init__():
        Inicializa o serviço, carregando os metadados econômicos.
    search(frequency: str, fonte_list: list, tema_list: list) -> pd.DataFrame:
        Realiza busca filtrando por frequência, fontes e temas, retornando os resultados como lista de dicionários.
    get_by_source(fonte_list: list) -> pd.DataFrame:
        Filtra os metadados pelas fontes especificadas.
    get_by_theme(tema_list: list) -> pd.DataFrame:
        Filtra os metadados pelos temas especificados.
    get_by_frequency(frequency: str) -> pd.DataFrame:
        Filtra os metadados pela frequência especificada.
    get_available_sources(frequencia: str) -> list:
        Retorna as fontes disponíveis para uma determinada frequência.
    get_available_themes(frequencia: str) -> dict:
        Retorna os temas disponíveis para uma determinada frequência.
    """
    
    def __init__(self):
        print("Inicializando SearchService...")
        self.metadata_economicos = metadata_economicos.copy()
        print(f"Metadata carregada com {self.metadata_economicos.shape[0]} séries estatísticas.")

    def search(self, frequency: str, fonte_list: list, tema_list: list ) -> pd.DataFrame:
        print(f"Buscando com fontes: {fonte_list}, temas: {tema_list}, frequência: {frequency}")
        filtragem_fonte = self.get_by_source(fonte_list)
        print(f"Filtragem por fonte: {filtragem_fonte.shape}")
        filtragem_tema = self.get_by_theme(tema_list)
        print(f"Filtragem por tema: {filtragem_tema.shape}")
        filtragem_frequencia = self.get_by_frequency(frequency)
        print(f"Filtragem por frequência: {filtragem_frequencia.shape}")
        df_filtrado = pd.merge(
            filtragem_fonte,
            filtragem_tema,
            how="inner",
            on=['CODE'],
            suffixes=('', '_DROP1')
        )
        print(f"Após merge fonte-tema: {df_filtrado.shape}")
        df_filtrado = pd.merge(
            df_filtrado,
            filtragem_frequencia,
            how="inner",
            on=['CODE'],
            suffixes=('', '_DROP2')
        )
        print(f"Após merge com frequência: {df_filtrado.shape}")
        df_filtrado = df_filtrado.loc[:, ~df_filtrado.columns.str.endswith(('_DROP1', '_DROP2'))]
        print(f"Após remover colunas duplicadas: {df_filtrado.shape}")
        return df_filtrado.reset_index(drop=True).to_dict(orient='records')

    def get_by_source(self, fonte_list: list) -> pd.DataFrame:
        metadata_filtrado = self.metadata_economicos.copy()
        if not fonte_list:
            print("Nenhuma fonte selecionada, retornando todos os dados.")
            return metadata_filtrado
        metadata_filtrado = metadata_filtrado[metadata_filtrado['SOURCE ACRONYM'].isin(fonte_list)]
        print(f"Filtrado por fonte: {metadata_filtrado.shape}")
        filtragem_fonte = metadata_filtrado.reset_index(drop=True)
        return filtragem_fonte

    def get_by_theme(self, tema_list: list) -> pd.DataFrame:
        # Para cada item em tema_list, mantenha apenas o atributo 'THEME CODE'
        tema_list = [
            item['THEME CODE'] if isinstance(item, dict) and 'THEME CODE' in item else item
            for item in tema_list
        ]
        metadata_filtrado = self.metadata_economicos.copy()
        if not tema_list:
            print("Nenhum tema selecionado, retornando todos os dados.")
            return metadata_filtrado
        metadata_filtrado = metadata_filtrado[metadata_filtrado['THEME CODE'].isin(tema_list)]
        print(f"Filtrado por tema: {metadata_filtrado.shape}")
        filtragem_tema = metadata_filtrado.reset_index(drop=True)
        return filtragem_tema

    def get_by_frequency(self, frequency: str) -> pd.DataFrame:
        metadata_filtrado = self.metadata_economicos.copy()
        metadata_filtrado = metadata_filtrado[metadata_filtrado['FREQUENCY'] == frequency]
        print(f"Filtrado por frequência: {metadata_filtrado.shape}")
        filtragem_frequencia = metadata_filtrado.reset_index(drop=True)
        return filtragem_frequencia
    
    def get_available_sources(self, frequencia: str) -> list:
        filtragem_frequencia = self.get_by_frequency(frequencia)
        return filtragem_frequencia[['SOURCE ACRONYM']].drop_duplicates()
    
    def get_available_themes(self, frequencia: str) -> dict:
        filtragem_frequencia = self.get_by_frequency(frequencia)
        merge_df = pd.merge(
            filtragem_frequencia,
            temas_df,
            how="left",
            on='THEME CODE'
        )
        return merge_df[['THEME CODE', 'THEME NAME']].drop_duplicates().to_dict(orient='records')