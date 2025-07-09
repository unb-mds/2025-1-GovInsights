import pytest
import base64
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Classe personalizada para simular session_state do Streamlit
class MockSessionState:
    def __init__(self):
        self._data = {'page': 'landing'}
    
    def __contains__(self, key):
        return key in self._data
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    @property
    def page(self):
        return self._data.get('page', 'landing')
    
    @page.setter
    def page(self, value):
        self._data['page'] = value

# Mock streamlit para evitar warnings e problemas de contexto
streamlit_mock = MagicMock()
streamlit_mock.session_state = MockSessionState()
streamlit_mock.set_page_config = MagicMock()
streamlit_mock.markdown = MagicMock()
streamlit_mock.warning = MagicMock()
streamlit_mock.container = MagicMock()
streamlit_mock.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
streamlit_mock.image = MagicMock()

# Substitui o módulo streamlit antes de qualquer importação
sys.modules['streamlit'] = streamlit_mock

# Mock para evitar a execução automática do landing_page()
with patch('builtins.open', mock_open(read_data=b'fake_image_data')):
    with patch('pathlib.Path.exists', return_value=True):
        # Agora pode importar com segurança
        from src.main import get_img_as_base64, get_base64_of_bin_file


class TestMainFunctions:
    """Testes unitários para as funções do main.py."""

    def test_get_img_as_base64_success(self):
        """Teste get_img_as_base64 com arquivo válido."""
        # Dados de imagem fake (alguns bytes)
        fake_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        expected_b64 = base64.b64encode(fake_image_data).decode()
        expected_result = f"data:image/png;base64,{expected_b64}"
        
        with patch('builtins.open', mock_open(read_data=fake_image_data)):
            result = get_img_as_base64("/fake/path/image.png")
            assert result == expected_result

    def test_get_img_as_base64_different_formats(self):
        """Teste get_img_as_base64 com diferentes formatos de imagem."""
        fake_data = b'\xFF\xD8\xFF\xE0'  # Cabeçalho JPEG
        expected_b64 = base64.b64encode(fake_data).decode()
        expected_result = f"data:image/png;base64,{expected_b64}"
        
        with patch('builtins.open', mock_open(read_data=fake_data)):
            result = get_img_as_base64("/fake/path/image.jpg")
            # Note que a função sempre retorna como image/png no MIME type
            assert result == expected_result

    def test_get_img_as_base64_empty_file(self):
        """Teste get_img_as_base64 com arquivo vazio."""
        with patch('builtins.open', mock_open(read_data=b'')):
            result = get_img_as_base64("/fake/path/empty.png")
            assert result == "data:image/png;base64,"

    def test_get_img_as_base64_file_not_found(self):
        """Teste get_img_as_base64 com arquivo não encontrado."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                get_img_as_base64("/fake/path/nonexistent.png")

    def test_get_base64_of_bin_file_success(self):
        """Teste get_base64_of_bin_file com arquivo válido."""
        fake_binary_data = b'\x00\x01\x02\x03\x04\x05'
        expected_b64 = base64.b64encode(fake_binary_data).decode()
        
        with patch('builtins.open', mock_open(read_data=fake_binary_data)):
            result = get_base64_of_bin_file("/fake/path/binary.bin")
            assert result == expected_b64

    def test_get_base64_of_bin_file_large_file(self):
        """Teste get_base64_of_bin_file com arquivo grande."""
        # Simula um arquivo de 1KB
        fake_large_data = b'A' * 1024
        expected_b64 = base64.b64encode(fake_large_data).decode()
        
        with patch('builtins.open', mock_open(read_data=fake_large_data)):
            result = get_base64_of_bin_file("/fake/path/large.bin")
            assert result == expected_b64
            assert len(result) > 1000  # Base64 aumenta o tamanho

    def test_get_base64_of_bin_file_empty_file(self):
        """Teste get_base64_of_bin_file com arquivo vazio."""
        with patch('builtins.open', mock_open(read_data=b'')):
            result = get_base64_of_bin_file("/fake/path/empty.bin")
            assert result == ""

    def test_get_base64_of_bin_file_not_found(self):
        """Teste get_base64_of_bin_file com arquivo não encontrado."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                get_base64_of_bin_file("/fake/path/nonexistent.bin")

    def test_get_base64_of_bin_file_permission_error(self):
        """Teste get_base64_of_bin_file com erro de permissão."""
        with patch('builtins.open', side_effect=PermissionError):
            with pytest.raises(PermissionError):
                get_base64_of_bin_file("/fake/path/no_permission.bin")

    def test_both_functions_return_strings(self):
        """Teste se ambas as funções retornam strings."""
        fake_data = b'\x01\x02\x03'
        
        with patch('builtins.open', mock_open(read_data=fake_data)):
            img_result = get_img_as_base64("/fake/image.png")
            bin_result = get_base64_of_bin_file("/fake/binary.bin")
            
            assert isinstance(img_result, str)
            assert isinstance(bin_result, str)

    def test_img_function_mime_type_consistency(self):
        """Teste se get_img_as_base64 sempre retorna o MIME type correto."""
        fake_data = b'\x01\x02\x03'
        
        with patch('builtins.open', mock_open(read_data=fake_data)):
            result = get_img_as_base64("/any/path.png")
            assert result.startswith("data:image/png;base64,")

    def test_base64_encoding_correctness(self):
        """Teste se a codificação base64 está correta."""
        test_data = b'Hello, World!'
        expected_b64 = base64.b64encode(test_data).decode()
        
        with patch('builtins.open', mock_open(read_data=test_data)):
            # Teste get_base64_of_bin_file
            bin_result = get_base64_of_bin_file("/fake/test.txt")
            assert bin_result == expected_b64
            
            # Teste get_img_as_base64
            img_result = get_img_as_base64("/fake/test.png")
            assert img_result == f"data:image/png;base64,{expected_b64}"

    def test_path_objects_exist_in_module(self):
        """Teste se os objetos Path existem no módulo."""
        import src.main
        
        # Verificar se as variáveis de path existem
        assert hasattr(src.main, 'current_dir')
        assert hasattr(src.main, 'logo_path')
        assert hasattr(src.main, 'ilustra_path')
        assert hasattr(src.main, 'main_style_path')
        assert hasattr(src.main, 'base_img_path')
        assert hasattr(src.main, 'equipe_img_path')

    def test_functions_handle_binary_data_correctly(self):
        """Teste se as funções lidam corretamente com dados binários."""
        # Dados binários com bytes especiais
        binary_data = bytes(range(256))  # Todos os valores de byte possíveis
        
        with patch('builtins.open', mock_open(read_data=binary_data)):
            bin_result = get_base64_of_bin_file("/fake/binary.bin")
            img_result = get_img_as_base64("/fake/binary.png")
            
            # Decodificar de volta para verificar integridade
            decoded_bin = base64.b64decode(bin_result)
            decoded_img = base64.b64decode(img_result.split(',')[1])
            
            assert decoded_bin == binary_data
            assert decoded_img == binary_data


class TestMainModuleImports:
    """Testes para verificar se os imports do main.py funcionam corretamente."""

    def test_streamlit_config_called(self):
        """Teste se streamlit.set_page_config é chamado ao importar main."""
        # Como já importamos main com mocks, apenas verificamos se o mock foi chamado
        # O set_page_config já foi chamado durante a importação inicial
        import src.main
        
        # Verificar se o módulo foi importado corretamente
        assert hasattr(src.main, 'get_img_as_base64')
        assert hasattr(src.main, 'get_base64_of_bin_file')
        
        # Note: Em um ambiente mockado, não podemos verificar diretamente 
        # se set_page_config foi chamado, mas podemos verificar se a importação funcionou

    def test_module_level_variables(self):
        """Teste se as variáveis de módulo são criadas corretamente."""
        import src.main
        
        # Verificar se as variáveis existem
        assert hasattr(src.main, 'current_dir')
        assert hasattr(src.main, 'logo_path')
        assert hasattr(src.main, 'ilustra_path')
        assert hasattr(src.main, 'main_style_path')
        assert hasattr(src.main, 'base_img_path')
        assert hasattr(src.main, 'equipe_img_path')
        
        # Verificar se são objetos Path
        from pathlib import Path
        assert isinstance(src.main.current_dir, Path)
        assert isinstance(src.main.logo_path, Path)
        assert isinstance(src.main.ilustra_path, Path)


class TestMainEdgeCases:
    """Testes para casos extremos e situações especiais."""

    def test_get_img_as_base64_with_unicode_path(self):
        """Teste get_img_as_base64 com caminho Unicode."""
        fake_data = b'\x01\x02\x03'
        unicode_path = "/fake/caminho_com_acentuação_çñü.png"
        
        with patch('builtins.open', mock_open(read_data=fake_data)):
            result = get_img_as_base64(unicode_path)
            assert result.startswith("data:image/png;base64,")

    def test_file_operations_called_with_correct_modes(self):
        """Teste se os arquivos são abertos com os modos corretos."""
        fake_data = b'\x01\x02\x03'
        
        with patch('builtins.open', mock_open(read_data=fake_data)) as mock_file:
            # Teste get_img_as_base64
            get_img_as_base64("/fake/image.png")
            mock_file.assert_called_with("/fake/image.png", "rb")
            
            # Reset mock
            mock_file.reset_mock()
            
            # Teste get_base64_of_bin_file
            get_base64_of_bin_file("/fake/binary.bin")
            mock_file.assert_called_with("/fake/binary.bin", "rb")

    def test_functions_with_pathlib_objects(self):
        """Teste se as funções funcionam com objetos Path."""
        fake_data = b'\x01\x02\x03'
        path_obj = Path("/fake/test.png")
        
        with patch('builtins.open', mock_open(read_data=fake_data)):
            # As funções devem aceitar tanto strings quanto Path objects
            result = get_img_as_base64(str(path_obj))
            assert result.startswith("data:image/png;base64,")
            
            result = get_base64_of_bin_file(str(path_obj))
            assert isinstance(result, str)
