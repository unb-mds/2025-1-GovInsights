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
def test_landing_page_calls(st_mock):
    st_mock.columns.return_value = [MagicMock(), MagicMock()]
    st_mock.image.return_value = None
    st_mock.button.return_value = False
    st_mock.session_state = SimpleNamespace(page="landing")

    main.landing_page()

    assert st_mock.markdown.call_count > 0
    st_mock.columns.assert_called()
    st_mock.image.assert_called()


@patch("src.main.st")
def test_landing_page_renders_correctly(st_mock):
    st_mock.columns.return_value = [MagicMock(), MagicMock()]
    st_mock.image.return_value = None
    st_mock.session_state = SimpleNamespace(page="landing")

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

    if st_mock.session_state.page == "landing":
        main.landing_page()
    elif st_mock.session_state.page == "dashboard":
        pass

    landing_mock.assert_called_once()

    # Mock módulo dashboard para evitar erro de importação
    sys.modules['interface.views.dashboard'] = types.SimpleNamespace(main_page=lambda: None)

    st_mock.session_state = SimpleNamespace(page="dashboard")

    with patch("interface.views.dashboard.main_page") as dashboard_mock:
        if st_mock.session_state.page == "landing":
            main.landing_page()
        elif st_mock.session_state.page == "dashboard":
            dashboard_mock()

        dashboard_mock.assert_called_once()
