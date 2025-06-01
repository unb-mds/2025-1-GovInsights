import pandas as pd
import ipeadatapy as ipea
import plotly.express as px

def search(source_list: list, theme_list: list, frequency: list) -> pd.DataFrame:
    """
    Retorna os metadados de indicadores do IPEA filtrados por fonte e tema.
    Parâmetros:
    -----------
    source_list : list
        Lista de códigos das fontes. Busca é feita de forma case-insensitive.
    theme_list : list
        Lista de códigos dos temas. Busca é feita de forma case-insensitive.
    Retorno:
    --------
    pd.DataFrame
        DataFrame com os metadados de todos os indicadores encontrados nas fontes e temas especificados.
    """
    filtragem_fonte = get_by_source(source_list)
    filtragem_tema = get_by_theme(theme_list)
    filtragem_frequencia = get_by_frequency(frequency)
    # Realiza INNER JOIN entre os DataFrames filtrados por fonte e tema
    # Como ambos sempre terão as mesmas colunas, basta fazer o merge pelo código do indicador
    df_filtrado = pd.merge(
        filtragem_fonte,
        filtragem_tema,
        how="inner",
        on=['CODE'],
        suffixes=('', '_DROP1')
    )
    df_filtrado = pd.merge(
        df_filtrado,
        filtragem_frequencia,
        how="inner",
        on=['CODE'],
        suffixes=('', '_DROP2')
    )
    # Remove colunas duplicadas criadas pelos merges (terminam com _DROP1 ou _DROP2)
    df_filtrado = df_filtrado.loc[:, ~df_filtrado.columns.str.endswith(('_DROP1', '_DROP2'))]
    return df_filtrado.reset_index(drop=True)

def get_by_source(source_list: list) -> pd.DataFrame:
    """
    Retorna os metadados de todos os indicadores associados a uma ou mais fontes específicas.

    Parâmetros:
    -----------
    source_list : list
        Lista de códigos das fontes. Busca é feita de forma case-insensitive.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os metadados de todos os indicadores encontrados nas fontes especificadas.
    """
    # Busca todos os metadados disponíveis
    metadata_filtrado = ipea.metadata()
    metadata_filtrado =  metadata_filtrado[metadata_filtrado['MEASURE'].str.contains("\\$")] # Filtra apenas indicadores com medidas monetárias
    # Remove séries inativas
    metadata_filtrado = metadata_filtrado[~metadata_filtrado['NAME'].str.contains('INATIVA', case=False, na=False)]
    
    if not source_list:
        return metadata_filtrado  # Se nenhuma fonte for informada, retorna todos os metadados

    
    # Filtra por fontes especificadas
    metadata_filtrado = metadata_filtrado[metadata_filtrado['SOURCE ACRONYM'].isin] # Filtra por fontes especificadas
    
    return metadata_filtrado.reset_index(drop=True)  # Reseta o índice do DataFrame filtrado


def get_by_theme(theme_list: list) -> pd.DataFrame:
    """
    Retorna os metadados de todos os indicadores associados a um tema específico.

    Parâmetros:
    -----------
    theme_nome : str
        Nome (ou parte do nome) do tema. Busca é feita de forma case-insensitive.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os metadados de todos os indicadores encontrados no tema.

    Erros:
    ------
    ValueError
        Se o tema informado não for encontrado na base de dados.
    """
    # Busca todos os temas disponíveis
    metadata_filtrado = ipea.metadata()
    metadata_filtrado =  metadata_filtrado[metadata_filtrado['MEASURE'].str.contains("\\$")] # Filtra apenas indicadores com medidas monetárias
    
    if not theme_list:
        return metadata_filtrado # Se nenhum tema for informado, retorna todos os metadados
    
    metadata_filtrado = metadata_filtrado[metadata_filtrado['THEME CODE'].isin(theme_list)]  # Filtra por temas especificados
    return metadata_filtrado.reset_index(drop=True) # Reseta o índice do DataFrame filtrado

def get_by_frequency(frequency: str) -> pd.DataFrame:
    """
    Retorna os metadados de todos os indicadores associados a uma frequência específica.

    Parâmetros:
    -----------
    frequency : str
        Frequência da série estatística (ex.: "Mensal", "Anual", etc.).

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os metadados de todos os indicadores encontrados na frequência especificada.
    """
    metadata_filtrado = ipea.metadata()
    metadata_filtrado = metadata_filtrado[metadata_filtrado['MEASURE'].str.contains("\\$")] # Filtra apenas indicadores com medidas monetárias
    
    if not frequency:
        return metadata_filtrado  # Se nenhuma frequência for informada, retorna todos os metadados
    
    metadata_filtrado = metadata_filtrado[metadata_filtrado['FREQUENCY'] == frequency]  # Filtra por frequência especificada
    return metadata_filtrado.reset_index(drop=True)  # Reseta o índice do DataFrame filtrado

def descrever_serie(serie: str) -> pd.DataFrame:
    """
    Retorna os metadados de uma série estatística específica.

    Parâmetros:
    -----------
    serie : str
        Código da série estatística.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os metadados da série estatística.
    """
    metadata = ipea.metadata()
    serie_metadata = metadata[metadata['CODE'] == serie]
    
    if serie_metadata.empty:
        raise ValueError(f"Série '{serie}' não encontrada.")
    
    return serie_metadata.reset_index(drop=True)  # Reseta o índice do DataFrame filtrado