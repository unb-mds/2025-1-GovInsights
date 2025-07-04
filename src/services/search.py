import pandas as pd
import ipeadatapy as ipea

# Carregamento das variáveis globais
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
    """

    def __init__(self):
        print("Inicializando SearchService...")
        self.metadata_economicos = metadata_economicos.copy()
        self.temas_df = temas_df.copy()
        print(f"Metadata carregada com {self.metadata_economicos.shape[0]} séries estatísticas.")

    def search(self, frequency: str, fonte_list: list, tema_list: list) -> pd.DataFrame:
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
        return metadata_filtrado.reset_index(drop=True)

    def get_by_theme(self, tema_list: list) -> pd.DataFrame:
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
        return metadata_filtrado.reset_index(drop=True)

    def get_by_frequency(self, frequency: str) -> pd.DataFrame:
        metadata_filtrado = self.metadata_economicos.copy()
        metadata_filtrado = metadata_filtrado[metadata_filtrado['FREQUENCY'] == frequency]
        print(f"Filtrado por frequência: {metadata_filtrado.shape}")
        return metadata_filtrado.reset_index(drop=True)

    def get_available_sources(self, frequencia: str) -> list:
        filtragem_frequencia = self.get_by_frequency(frequencia)
        return filtragem_frequencia[['SOURCE ACRONYM']].drop_duplicates()

    def get_available_themes(self, frequencia: str) -> dict:
        filtragem_frequencia = self.get_by_frequency(frequencia)
        merge_df = pd.merge(
            filtragem_frequencia,
            self.temas_df,
            how="left",
            on='THEME CODE'
        )
        return merge_df[['THEME CODE', 'THEME NAME']].drop_duplicates().to_dict(orient='records')

# Criar uma instância global para uso nas funções abaixo
search_service = SearchService()

# Funções públicas para testes e uso externo

def organization(acronym_or_source_name: str) -> pd.DataFrame:
    """
    Busca organização por acrônimo ou nome da fonte.
    """
    # Tenta filtrar por acrônimo
    df = search_service.get_by_source([acronym_or_source_name])
    if df.empty:
        # Tenta filtrar por nome completo na coluna 'SOURCE'
        df = search_service.metadata_economicos[
            search_service.metadata_economicos['SOURCE'].str.contains(acronym_or_source_name, case=False, na=False)
        ]
    return df.reset_index(drop=True)

def theme(theme_code_or_name) -> pd.DataFrame:
    """
    Busca séries pelo código ou nome do tema.
    """
    if isinstance(theme_code_or_name, str):
        filtered_theme = temas_df[temas_df['THEME NAME'].str.contains(theme_code_or_name, case=False, na=False)]
        if filtered_theme.empty:
            return pd.DataFrame()
        theme_codes = filtered_theme['THEME CODE'].tolist()
    else:
        theme_codes = [theme_code_or_name]

    return search_service.get_by_theme(theme_codes)

def code(code_value: str) -> pd.DataFrame:
    """
    Busca série pelo código exato.
    """
    df = search_service.metadata_economicos
    result = df[df['CODE'] == code_value]
    return result.reset_index(drop=True)

def date(data_inicial=None, data_final=None) -> pd.DataFrame:
    """
    Busca séries filtrando por intervalo de datas na coluna 'LAST UPDATE'.
    """
    df = search_service.metadata_economicos.copy()
    df['LAST UPDATE'] = pd.to_datetime(df['LAST UPDATE'], utc=True, errors='coerce')

    if data_inicial:
        start_date = pd.to_datetime(data_inicial, utc=True)
        df = df[df['LAST UPDATE'] >= start_date]
    if data_final:
        end_date = pd.to_datetime(data_final, utc=True)
        df = df[df['LAST UPDATE'] <= end_date]

    return df.reset_index(drop=True)

