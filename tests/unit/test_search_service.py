import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.services.search import SearchService, organization, theme, code, date


class TestSearchService:
    """Testes unitários para o serviço de busca."""

    @pytest.fixture
    def mock_metadata(self):
        """Fixture com dados de teste para metadata."""
        return pd.DataFrame({
            'CODE': ['SERIE001', 'SERIE002', 'SERIE003', 'SERIE004'],
            'NAME': ['Série Test 1', 'Série Test 2', 'Série Test 3 INATIVA', 'Série Test 4'],
            'SOURCE ACRONYM': ['BCB', 'IBGE', 'BCB', 'IPEA'],
            'SOURCE': ['Banco Central do Brasil', 'Instituto Brasileiro de Geografia e Estatística', 
                      'Banco Central do Brasil', 'Instituto de Pesquisa Econômica Aplicada'],
            'THEME CODE': [100, 200, 100, 300],
            'BIG THEME': ['Economia', 'Demografia', 'Economia', 'Regional'],
            'FREQUENCY': ['M', 'A', 'M', 'T'],
            'MEASURE': ['R$ milhões', 'Unidades', '$ milhões', 'Índice'],
            'LAST UPDATE': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05']
        })

    @pytest.fixture
    def mock_themes(self):
        """Fixture com dados de teste para temas."""
        return pd.DataFrame({
            'ID': [100, 200, 300],
            'NAME': ['Economia e Finanças', 'Demografia e População', 'Desenvolvimento Regional']
        })

    @pytest.fixture
    def search_service(self, mock_metadata, mock_themes):
        """Fixture para criar uma instância do SearchService com dados mock."""
        with patch('src.services.search.metadata_economicos', mock_metadata), \
             patch('src.services.search.temas_df', mock_themes.rename(columns={'ID': 'THEME CODE', 'NAME': 'THEME NAME'})):
            service = SearchService()
            return service

    def test_search_service_init(self, search_service):
        """Teste de inicialização do SearchService."""
        assert search_service.metadata_economicos is not None
        assert search_service.temas_df is not None
        assert len(search_service.metadata_economicos) > 0
        assert len(search_service.temas_df) > 0

    def test_get_by_source_lista_vazia(self, search_service):
        """Teste get_by_source com lista vazia retorna todos os dados."""
        result = search_service.get_by_source([])
        assert len(result) == len(search_service.metadata_economicos)

    def test_get_by_source_fonte_existente(self, search_service):
        """Teste get_by_source com fonte existente."""
        result = search_service.get_by_source(['BCB'])
        assert len(result) == 2  # Deve retornar 2 séries do BCB
        assert all(row['SOURCE ACRONYM'] == 'BCB' for _, row in result.iterrows())

    def test_get_by_source_fonte_inexistente(self, search_service):
        """Teste get_by_source com fonte inexistente."""
        result = search_service.get_by_source(['FONTE_INEXISTENTE'])
        assert len(result) == 0

    def test_get_by_source_multiplas_fontes(self, search_service):
        """Teste get_by_source com múltiplas fontes."""
        result = search_service.get_by_source(['BCB', 'IBGE'])
        assert len(result) == 3  # 2 do BCB + 1 do IBGE
        assert all(row['SOURCE ACRONYM'] in ['BCB', 'IBGE'] for _, row in result.iterrows())

    def test_get_by_theme_lista_vazia(self, search_service):
        """Teste get_by_theme com lista vazia retorna todos os dados."""
        result = search_service.get_by_theme([])
        assert len(result) == len(search_service.metadata_economicos)

    def test_get_by_theme_tema_existente(self, search_service):
        """Teste get_by_theme com tema existente."""
        result = search_service.get_by_theme([100])
        assert len(result) == 2  # Deve retornar 2 séries do tema 100
        assert all(row['THEME CODE'] == 100 for _, row in result.iterrows())

    def test_get_by_theme_tema_dicionario(self, search_service):
        """Teste get_by_theme com tema como dicionário."""
        result = search_service.get_by_theme([{'THEME CODE': 200}])
        assert len(result) == 1
        assert result.iloc[0]['THEME CODE'] == 200

    def test_get_by_theme_tema_inexistente(self, search_service):
        """Teste get_by_theme com tema inexistente."""
        result = search_service.get_by_theme([999])
        assert len(result) == 0

    def test_get_by_frequency_existente(self, search_service):
        """Teste get_by_frequency com frequência existente."""
        result = search_service.get_by_frequency('M')
        assert len(result) == 2  # Duas séries mensais
        assert all(row['FREQUENCY'] == 'M' for _, row in result.iterrows())

    def test_get_by_frequency_inexistente(self, search_service):
        """Teste get_by_frequency com frequência inexistente."""
        result = search_service.get_by_frequency('Z')
        assert len(result) == 0

    def test_get_available_sources(self, search_service):
        """Teste get_available_sources."""
        result = search_service.get_available_sources('M')
        assert len(result) == 1  # BCB aparece nas séries mensais
        assert 'SOURCE ACRONYM' in result.columns

    def test_get_available_themes(self, search_service):
        """Teste get_available_themes."""
        result = search_service.get_available_themes('M')
        assert isinstance(result, list)
        assert len(result) == 1  # Apenas tema 100 nas séries mensais
        assert 'THEME CODE' in result[0]
        assert 'THEME NAME' in result[0]

    def test_search_completo(self, search_service):
        """Teste do método search completo."""
        result = search_service.search('M', ['BCB'], [100])
        assert isinstance(result, list)
        assert len(result) == 2  # Duas séries que atendem todos os critérios
        for item in result:
            assert item['FREQUENCY'] == 'M'
            assert item['SOURCE ACRONYM'] == 'BCB'
            assert item['THEME CODE'] == 100

    def test_search_sem_resultados(self, search_service):
        """Teste do método search sem resultados."""
        result = search_service.search('M', ['IBGE'], [100])
        assert isinstance(result, list)
        assert len(result) == 0

    def test_search_fonte_vazia(self, search_service):
        """Teste do método search com fonte vazia."""
        result = search_service.search('M', [], [100])
        assert isinstance(result, list)
        assert len(result) == 2  # Todas as séries mensais do tema 100


class TestSearchFunctions:
    """Testes para as funções públicas do módulo search."""

    @pytest.fixture
    def mock_search_service(self):
        """Mock do SearchService global."""
        with patch('src.services.search.search_service') as mock_service:
            # Mock metadata_economicos
            mock_service.metadata_economicos = pd.DataFrame({
                'CODE': ['ORG001', 'ORG002', 'ORG003'],
                'SOURCE ACRONYM': ['BCB', 'IBGE', 'IPEA'],
                'SOURCE': ['Banco Central', 'Instituto Geografia', 'Instituto Pesquisa'],
                'THEME CODE': [100, 200, 300],
                'LAST UPDATE': ['2023-01-15', '2023-02-20', '2023-03-10']
            })
            
            # Mock get_by_source method
            def mock_get_by_source(sources):
                if not sources:
                    return mock_service.metadata_economicos
                return mock_service.metadata_economicos[
                    mock_service.metadata_economicos['SOURCE ACRONYM'].isin(sources)
                ]
            mock_service.get_by_source.side_effect = mock_get_by_source
            
            # Mock get_by_theme method
            def mock_get_by_theme(themes):
                if not themes:
                    return mock_service.metadata_economicos
                return mock_service.metadata_economicos[
                    mock_service.metadata_economicos['THEME CODE'].isin(themes)
                ]
            mock_service.get_by_theme.side_effect = mock_get_by_theme
            
            yield mock_service

    @patch('src.services.search.temas_df')
    def test_organization_por_acronimo(self, mock_temas_df, mock_search_service):
        """Teste da função organization por acrônimo."""
        result = organization('BCB')
        assert len(result) == 1
        assert result.iloc[0]['SOURCE ACRONYM'] == 'BCB'

    @patch('src.services.search.temas_df')
    def test_organization_por_nome(self, mock_temas_df, mock_search_service):
        """Teste da função organization por nome da fonte."""
        # Quando não encontra por acrônimo, busca por nome
        mock_search_service.get_by_source.return_value = pd.DataFrame()  # Vazio para primeira busca
        
        result = organization('Central')
        # Verifica se foi chamado o filtro por nome na fonte
        assert isinstance(result, pd.DataFrame)

    @patch('src.services.search.temas_df')
    def test_theme_por_nome(self, mock_temas_df, mock_search_service):
        """Teste da função theme por nome."""
        # Mock temas_df
        mock_temas_df.value = pd.DataFrame({
            'THEME CODE': [100, 200],
            'THEME NAME': ['Economia', 'Demografia']
        })
        
        with patch('src.services.search.temas_df', mock_temas_df.value):
            result = theme('Economia')
            assert isinstance(result, pd.DataFrame)

    @patch('src.services.search.temas_df')
    def test_theme_por_codigo(self, mock_temas_df, mock_search_service):
        """Teste da função theme por código."""
        result = theme(100)
        mock_search_service.get_by_theme.assert_called_with([100])

    @patch('src.services.search.temas_df')
    def test_theme_nome_inexistente(self, mock_temas_df, mock_search_service):
        """Teste da função theme com nome inexistente."""
        # Mock temas_df vazio
        mock_temas_df.value = pd.DataFrame({
            'THEME CODE': pd.Series([], dtype='int64'),
            'THEME NAME': pd.Series([], dtype='object')
        })
        
        with patch('src.services.search.temas_df', mock_temas_df.value):
            result = theme('Inexistente')
            assert len(result) == 0

    def test_code_existente(self, mock_search_service):
        """Teste da função code com código existente."""
        result = code('ORG001')
        assert len(result) == 1
        assert result.iloc[0]['CODE'] == 'ORG001'

    def test_code_inexistente(self, mock_search_service):
        """Teste da função code com código inexistente."""
        result = code('INEXISTENTE')
        assert len(result) == 0

    def test_date_sem_filtros(self, mock_search_service):
        """Teste da função date sem filtros de data."""
        result = date()
        assert len(result) == 3  # Todos os registros

    def test_date_com_data_inicial(self, mock_search_service):
        """Teste da função date com data inicial."""
        result = date(data_inicial='2023-02-01')
        assert isinstance(result, pd.DataFrame)

    def test_date_com_data_final(self, mock_search_service):
        """Teste da função date com data final."""
        result = date(data_final='2023-02-01')
        assert isinstance(result, pd.DataFrame)

    def test_date_com_ambas_datas(self, mock_search_service):
        """Teste da função date com ambas as datas."""
        result = date(data_inicial='2023-01-01', data_final='2023-02-28')
        assert isinstance(result, pd.DataFrame)


class TestSearchServiceEdgeCases:
    """Testes para casos extremos do SearchService."""

    def test_load_global_variables_mock(self):
        """Teste da função load_global_variables com mock."""
        with patch('src.services.search.ipea.metadata') as mock_metadata, \
             patch('src.services.search.ipea.themes') as mock_themes:
            
            # Mock metadata com dados que passam pelos filtros
            mock_metadata.return_value = pd.DataFrame({
                'CODE': ['SERIE001', 'SERIE002', 'SERIE003'],
                'NAME': ['Série Ativa 1', 'Série Ativa 2', 'Série INATIVA'],
                'MEASURE': ['R$ milhões', '$ milhões', 'Unidades'],
                'BIG THEME': ['Economia', 'Demografia', 'Regional']
            })
            
            # Mock themes
            mock_themes.return_value = pd.DataFrame({
                'ID': [100, 200],
                'NAME': ['Tema 1', 'Tema 2']
            })
            
            # Import and call the function
            from src.services.search import load_global_variables
            load_global_variables()
            
            mock_metadata.assert_called_once()
            mock_themes.assert_called_once()

    @patch('src.services.search.metadata_economicos')
    @patch('src.services.search.temas_df')
    def test_search_service_with_empty_data(self, mock_temas_df, mock_metadata):
        """Teste SearchService com dados vazios."""
        # Mock com DataFrames vazios mas com estrutura correta
        mock_metadata.value = pd.DataFrame({
            'CODE': pd.Series([], dtype='object'),
            'SOURCE ACRONYM': pd.Series([], dtype='object'),
            'THEME CODE': pd.Series([], dtype='int64'),
            'FREQUENCY': pd.Series([], dtype='object')
        })
        mock_temas_df.value = pd.DataFrame({
            'THEME CODE': pd.Series([], dtype='int64'), 
            'THEME NAME': pd.Series([], dtype='object')
        })
        
        with patch('src.services.search.metadata_economicos', mock_metadata.value), \
             patch('src.services.search.temas_df', mock_temas_df.value):
            service = SearchService()
            assert len(service.metadata_economicos) == 0
            assert len(service.temas_df) == 0
            
            # Testes com dados vazios
            result = service.search('M', ['BCB'], [100])
            assert result == []
            
            result = service.get_available_sources('M')
            assert len(result) == 0
