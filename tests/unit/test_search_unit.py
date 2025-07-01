import pytest
import pandas as pd
from unittest.mock import patch
from src.services.search import organization, theme, code, date, SearchService

# Mock de DataFrame para metadata
mock_metadata_df = pd.DataFrame({
    'CODE': ['ORG001', 'ORG002', 'PNADCT_RREPUF', 'PNADCT_RRETUF', 'PNADCT_RRHTUF'],
    'MEASURE': ['$', '$', '%', '%', '%'],
    'SOURCE ACRONYM': ['IBGE', 'IPEA', 'IBGE', 'IBGE', 'IBGE'],
    'SOURCE': [
        'Instituto Brasileiro de Geografia e Estatística',
        'Instituto de Pesquisa Econômica Aplicada',
        'Instituto Brasileiro de Geografia e Estatística',
        'Instituto Brasileiro de Geografia e Estatística',
        'Instituto Brasileiro de Geografia e Estatística'
    ],
    'NAME': ['Nome 1', 'Nome 2', 'Nome 3', 'Nome 4', 'Nome 5'],
    'LAST UPDATE': ['2025-02-25T18:04:01-03:00'] * 5,
    'THEME CODE': [1, 1, 2, 2, 3],
    'FREQUENCY': ['Monthly'] * 5,
    'BIG THEME': ['Economia', 'Economia', 'Regional', 'Regional', 'Regional']
})

mock_themes_df = pd.DataFrame({
    'THEME CODE': [1, 2, 3],
    'THEME NAME': ['Economia', 'Finanças', 'Social']
})



@patch('src.services.search.ipea.metadata')
def test_organization_found_by_acronym(mock_metadata):
    mock_metadata.return_value = mock_metadata_df
    from src.services import search
    search.metadata_economicos = mock_metadata_df
    search.search_service = search.SearchService()

    result = organization("IBGE")
    assert not result.empty
    assert 'ORG001' in result['CODE'].values or 'PNADCT_RREPUF' in result['CODE'].values


@patch('src.services.search.ipea.metadata')
def test_organization_found_by_source_name(mock_metadata):
    mock_metadata.return_value = mock_metadata_df
    from src.services import search
    search.metadata_economicos = mock_metadata_df
    search.search_service = search.SearchService()

    result = organization("IPEA")
    assert not result.empty


@patch('src.services.search.ipea.metadata')
@patch('src.services.search.ipea.themes')
def test_theme_found(mock_themes, mock_metadata):
    mock_metadata.return_value = mock_metadata_df
    mock_themes.return_value = mock_themes_df

    from src.services import search
    search.temas_df = mock_themes_df.rename(columns={'ID': 'THEME CODE', 'NAME': 'THEME NAME'})
    search.metadata_economicos = mock_metadata_df
    search.search_service = search.SearchService()

    result = theme('Economia')
    assert not result.empty
    assert (result['THEME CODE'] == 1).all()


@patch('src.services.search.ipea.metadata')
def test_code_found(mock_metadata):
    mock_metadata.return_value = mock_metadata_df

    from src.services import search
    search.metadata_economicos = mock_metadata_df
    search.search_service = search.SearchService()

    result = code("ORG001")
    assert not result.empty
    assert (result['CODE'] == 'ORG001').all()


@patch('src.services.search.ipea.metadata')
def test_date_with_start_and_end_date(mock_metadata):
    mock_metadata.return_value = mock_metadata_df
    from src.services import search
    search.metadata_economicos = mock_metadata_df
    search.search_service = search.SearchService()

    result = date("2025-01-01", "2025-12-31")
    assert not result.empty
    dt_parsed = pd.to_datetime(result['LAST UPDATE'], utc=True)
    assert dt_parsed.min() >= pd.to_datetime("2025-01-01", utc=True)
    assert dt_parsed.max() <= pd.to_datetime("2025-12-31", utc=True)


@patch('src.services.search.ipea.metadata')
def test_date_only_start_date(mock_metadata):
    mock_metadata.return_value = mock_metadata_df
    from src.services import search
    search.metadata_economicos = mock_metadata_df
    search.search_service = search.SearchService()

    result = date("2025-01-01")
    assert not result.empty
    dt_parsed = pd.to_datetime(result['LAST UPDATE'], utc=True)
    assert dt_parsed.min() >= pd.to_datetime("2025-01-01", utc=True)


@patch('src.services.search.ipea.metadata')
def test_date_only_end_date(mock_metadata):
    mock_metadata.return_value = mock_metadata_df
    from src.services import search
    search.metadata_economicos = mock_metadata_df
    search.search_service = search.SearchService()

    result = date(data_final="2025-12-31")
    assert not result.empty
    dt_parsed = pd.to_datetime(result['LAST UPDATE'], utc=True)
    assert dt_parsed.max() <= pd.to_datetime("2025-12-31", utc=True)


@patch('src.services.search.ipea.metadata')
def test_date_no_results(mock_metadata):
    mock_metadata.return_value = mock_metadata_df
    from src.services import search
    search.metadata_economicos = mock_metadata_df
    search.search_service = search.SearchService()

    result = date("2026-01-01", "2026-12-31")
    assert result.empty
@patch('src.services.search.ipea.metadata')
def test_get_by_source_direct(mock_metadata):
    mock_metadata.return_value = mock_metadata_df
    from src.services.search import SearchService
    service = SearchService()
    df = service.get_by_source(['IBGE'])
    assert not df.empty
    assert (df['SOURCE ACRONYM'] == 'IBGE').all()

@pytest.fixture
def service():
    # Patch das variáveis globais da classe (metadata_economicos e temas_df)
    with patch('src.services.search.metadata_economicos', mock_metadata_df), \
         patch('src.services.search.temas_df', mock_themes_df):
        # Instancia a classe com os dados mockados
        service_instance = SearchService()
        # Substitui os dados internos para garantir isolamento
        service_instance.metadata_economicos = mock_metadata_df.copy()
        service_instance.temas_df = mock_themes_df.copy()
        yield service_instance


def test_get_by_source(service):
    df = service.get_by_source(['IBGE'])
    assert not df.empty
    assert (df['SOURCE ACRONYM'] == 'IBGE').all()

    # Testar retorno completo quando lista vazia
    df_all = service.get_by_source([])
    assert len(df_all) == len(mock_metadata_df)

def test_get_by_theme(service):
    # Pode passar lista de códigos
    df = service.get_by_theme([1])
    assert not df.empty
    assert (df['THEME CODE'] == 1).all()

    # Pode passar lista de dicts com 'THEME CODE'
    df_dict = service.get_by_theme([{'THEME CODE': 2}])
    assert not df_dict.empty
    assert (df_dict['THEME CODE'] == 2).all()

    # Sem filtro retorna tudo
    df_all = service.get_by_theme([])
    assert len(df_all) == len(mock_metadata_df)

def test_get_by_frequency(service):
    df = service.get_by_frequency('Monthly')
    assert not df.empty
    assert (df['FREQUENCY'] == 'Monthly').all()

    # Frequência inexistente retorna vazio
    df_empty = service.get_by_frequency('Daily')
    assert df_empty.empty

def test_get_available_sources(service):
    sources_df = service.get_available_sources('Monthly')
    assert isinstance(sources_df, pd.DataFrame)
    assert 'SOURCE ACRONYM' in sources_df.columns
    # Deve conter só os fontes únicos presentes na frequência mensal
    unique_sources = mock_metadata_df[mock_metadata_df['FREQUENCY']=='Monthly']['SOURCE ACRONYM'].unique()
    assert set(sources_df['SOURCE ACRONYM']) == set(unique_sources)

def test_get_available_themes(service):
    themes = service.get_available_themes('Monthly')
    assert isinstance(themes, list)
    # Deve conter os temas presentes na frequência 'Monthly'
    theme_codes = [t['THEME CODE'] for t in themes]
    expected_codes = mock_metadata_df[mock_metadata_df['FREQUENCY'] == 'Monthly']['THEME CODE'].unique()
    for code in theme_codes:
        assert code in expected_codes

def test_search(service):
    # Busca com fonte, tema e frequência válidos
    results = service.search(frequency='Monthly', fonte_list=['IBGE'], tema_list=[1])
    assert isinstance(results, list)
    # Deve retornar apenas códigos que tenham todas as condições
    for r in results:
        assert r['SOURCE ACRONYM'] == 'IBGE'
        assert r['THEME CODE'] == 1
        assert r['FREQUENCY'] == 'Monthly'

    # Busca sem fonte (vazio) retorna só filtrado por tema e frequência
    results2 = service.search(frequency='Monthly', fonte_list=[], tema_list=[1])
    assert all(r['THEME CODE'] == 1 for r in results2)

    # Busca sem tema (vazio) retorna só filtrado por fonte e frequência
    results3 = service.search(frequency='Monthly', fonte_list=['IBGE'], tema_list=[])
    assert all(r['SOURCE ACRONYM'] == 'IBGE' for r in results3)

    # Busca sem tema e fonte (ambos vazios) retorna tudo filtrado por frequência
    results4 = service.search(frequency='Monthly', fonte_list=[], tema_list=[])
    assert all(r['FREQUENCY'] == 'Monthly' for r in results4)