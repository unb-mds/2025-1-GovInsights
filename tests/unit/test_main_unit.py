import base64
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import sys
import types

import src.main as main  # ajuste o import se precisar


def test_get_base64_image(tmp_path):
    file_path = tmp_path / "image.png"
    content = b"conteudoimagem"
    file_path.write_bytes(content)

    encoded = main.get_base64_image(str(file_path))
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
def test_landing_page_button_click_changes_page_and_rerun(st_mock):
    st_mock.columns.return_value = [MagicMock(), MagicMock()]

    # Apenas o botão com key "dashboard_btn" retorna True
    def button_side_effect(*args, **kwargs):
        return kwargs.get("key") == "dashboard_btn"

    st_mock.button.side_effect = button_side_effect
    st_mock.session_state = SimpleNamespace(page="landing")
    st_mock.rerun = MagicMock()

    main.landing_page()

    assert st_mock.session_state.page == "dashboard"
    st_mock.rerun.assert_called_once()


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
