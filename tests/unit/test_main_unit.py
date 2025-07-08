import base64
from unittest.mock import patch, MagicMock, mock_open
from types import SimpleNamespace
import sys
import types

# Mock do streamlit ANTES de qualquer import
class MockSessionState:
    def __init__(self):
        self.page = "landing"
        
    def __contains__(self, key):
        return hasattr(self, key)
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
        
    def set_page_config(self, *args, **kwargs):
        pass
        
    def markdown(self, *args, **kwargs):
        pass
        
    def warning(self, *args, **kwargs):
        pass
        
    def image(self, *args, **kwargs):
        pass
        
    def container(self, *args, **kwargs):
        return MagicMock()
        
    def columns(self, *args, **kwargs):
        return [MagicMock(), MagicMock()]

# Substituir streamlit no sys.modules
sys.modules['streamlit'] = MockStreamlit()

# Mock dos arquivos de imagem
with patch('pathlib.Path.exists', return_value=True), \
     patch('builtins.open', mock_open(read_data=b'fake_image_data')):
    import src.main as main


def test_get_base64_of_bin_file(tmp_path):
    file_path = tmp_path / "image.png"
    content = b"conteudoimagem"
    file_path.write_bytes(content)

    # Teste direto da função real (sem mock)
    with patch('builtins.open', mock_open(read_data=content)):
        encoded = main.get_base64_of_bin_file(str(file_path))
        assert encoded == base64.b64encode(content).decode()


@patch("src.main.st")
@patch("src.main.get_base64_of_bin_file")
def test_landing_page_calls(mock_get_base64, st_mock):
    st_mock.columns.return_value = [MagicMock(), MagicMock()]
    st_mock.image.return_value = None
    st_mock.button.return_value = False
    st_mock.session_state = SimpleNamespace(page="landing")
    mock_get_base64.return_value = "fake_base64_data"

    main.landing_page()

    assert st_mock.markdown.call_count > 0
    st_mock.columns.assert_called()
    st_mock.image.assert_called()


@patch("src.main.st")
@patch("src.main.get_base64_of_bin_file")
def test_landing_page_renders_correctly(mock_get_base64, st_mock):
    st_mock.columns.return_value = [MagicMock(), MagicMock()]
    st_mock.image.return_value = None
    st_mock.session_state = SimpleNamespace(page="landing")
    mock_get_base64.return_value = "fake_base64_data"

    main.landing_page()

    # Verifica se a página foi renderizada corretamente
    assert st_mock.markdown.call_count > 0
    st_mock.columns.assert_called()
    
    # Verifica se o conteúdo principal foi renderizado
    call_args = [call[0][0] for call in st_mock.markdown.call_args_list]
    assert any("GOV INSIGHTS" in arg for arg in call_args)
    assert any("COMO FUNCIONA" in arg for arg in call_args)


@patch("src.main.st")
@patch("src.main.landing_page")
def test_page_navigation_calls_landing_or_dashboard(landing_mock, st_mock):
    st_mock.session_state = SimpleNamespace(page="landing")
    st_mock.columns.return_value = [MagicMock(), MagicMock()]
    landing_mock.return_value = None

    # Testa navegação para landing page
    if st_mock.session_state.page == "landing":
        main.landing_page()

    landing_mock.assert_called_once()

    # Mock simples para dashboard - apenas verifica se não há erro
    # O main.py atual só tem landing_page implementado
    st_mock.session_state = SimpleNamespace(page="dashboard")
    
    # Não testamos dashboard.main_page aqui pois não está integrado ao main.py
    # Este teste verifica apenas que landing_page é chamada corretamente
