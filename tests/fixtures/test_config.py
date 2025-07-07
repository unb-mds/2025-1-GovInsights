"""
Configurações para ambiente de testes do GovInsights
"""
import os
import pytest
from pathlib import Path

# Configurações de ambiente de teste
TEST_CONFIG = {
    "environment": "test",
    "debug": True,
    "testing": True,
    "api_timeout": 30,
    "max_retries": 3,
    "mock_external_apis": True
}

# Configurações de APIs para testes
API_CONFIG = {
    "ipea": {
        "base_url": "http://ipeadata.gov.br/api/odata4",
        "timeout": 30,
        "mock_enabled": True
    },
    "together_ai": {
        "api_key": os.getenv("DEEPSEEK_API_KEY_TEST", "test_key_123"),
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        "mock_enabled": True,
        "max_tokens": 4000,
        "temperature": 0.7
    },
    "supabase": {
        "url": os.getenv("SUPABASE_URL_TEST", "https://test.supabase.co"),
        "key": os.getenv("SUPABASE_KEY_TEST", "test_key_123"),
        "mock_enabled": True,
        "schema": "public"
    }
}

# Configurações de banco de dados para testes
DATABASE_CONFIG = {
    "test_table_prefix": "test_",
    "auto_cleanup": True,
    "isolation_level": "SERIALIZABLE",
    "test_data_retention_days": 1
}

# Configurações do Streamlit para testes
STREAMLIT_CONFIG = {
    "page_title": "GovInsights - Test",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": None
}

# Caminhos para arquivos de teste
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEST_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = Path(__file__).parent
TEMP_DIR = TEST_ROOT / "temp"

# Criar diretório temporário se não existir
TEMP_DIR.mkdir(exist_ok=True)

# Configurações de logging para testes
LOGGING_CONFIG = {
    "level": "DEBUG",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console"],
    "capture_warnings": True
}

# Configurações de timeout para diferentes tipos de teste
TIMEOUT_CONFIG = {
    "unit_tests": 30,  # segundos
    "integration_tests": 120,  # segundos
    "api_calls": 60,   # segundos
    "database_operations": 30,  # segundos
    "file_operations": 10   # segundos
}

# Fixtures de pytest reutilizáveis
@pytest.fixture(scope="session")
def test_config():
    """Fixture que retorna configurações de teste"""
    return TEST_CONFIG

@pytest.fixture(scope="session") 
def api_config():
    """Fixture que retorna configurações de APIs"""
    return API_CONFIG

@pytest.fixture(scope="session")
def temp_dir():
    """Fixture que retorna diretório temporário para testes"""
    return TEMP_DIR

@pytest.fixture(scope="function")
def clean_temp_dir():
    """Fixture que limpa diretório temporário após cada teste"""
    yield TEMP_DIR
    # Cleanup após o teste
    for file in TEMP_DIR.glob("*"):
        if file.is_file():
            file.unlink()

# Configurações específicas para diferentes tipos de teste
UNIT_TEST_CONFIG = {
    "mock_all_external_apis": True,
    "use_test_database": False,
    "enable_network_calls": False,
    "timeout": TIMEOUT_CONFIG["unit_tests"]
}

INTEGRATION_TEST_CONFIG = {
    "mock_external_apis": False,
    "use_test_database": True,
    "enable_network_calls": True,
    "timeout": TIMEOUT_CONFIG["integration_tests"],
    "cleanup_after_test": True
}

# Configurações de ambiente baseado na variável TEST_MODE
def get_config_for_mode(mode: str = None):
    """Retorna configuração baseada no modo de teste"""
    mode = mode or os.getenv("TEST_MODE", "unit")
    
    if mode == "unit":
        return UNIT_TEST_CONFIG
    elif mode == "integration":
        return INTEGRATION_TEST_CONFIG
    else:
        return TEST_CONFIG

# Validação de ambiente de teste
def validate_test_environment():
    """Valida se o ambiente de teste está configurado corretamente"""
    required_dirs = [PROJECT_ROOT, TEST_ROOT, FIXTURES_DIR, TEMP_DIR]
    
    for directory in required_dirs:
        if not directory.exists():
            raise EnvironmentError(f"Diretório necessário não encontrado: {directory}")
    
    # Verificar se variáveis de ambiente críticas estão definidas
    if not os.getenv("TEST_MODE"):
        os.environ["TEST_MODE"] = "unit"
    
    return True

# Configurações de mock para diferentes serviços
MOCK_SERVICES = {
    "ipea_api": {
        "enabled": True,
        "response_delay": 0.1,  # segundos
        "failure_rate": 0.0,    # 0% de falhas por padrão
        "timeout_rate": 0.0     # 0% de timeouts por padrão
    },
    "together_ai": {
        "enabled": True,
        "response_delay": 0.5,
        "failure_rate": 0.0,
        "timeout_rate": 0.0
    },
    "supabase": {
        "enabled": True,
        "response_delay": 0.1,
        "failure_rate": 0.0,
        "timeout_rate": 0.0
    }
}

# Dados de teste padrão
DEFAULT_TEST_DATA = {
    "valid_series_codes": ["BM12_TJOVER12", "PAN12_IGSTT12", "SCN52_PIBPMG12"],
    "invalid_series_codes": ["INVALID123", "", None],
    "valid_emails": ["test@example.com", "user@test.org"],
    "invalid_emails": ["invalid-email", "", None],
    "valid_frequencies": ["Diária", "Mensal", "Trimestral", "Anual"],
    "invalid_frequencies": ["Invalid", "", None]
}

# Executar validação ao importar o módulo
if __name__ != "__main__":
    validate_test_environment()

# Configuração para forçar uso de mocks em todos os testes de integração
FORCE_MOCK_USAGE = True

# Configurações específicas para evitar SKIPs desnecessários
INTEGRATION_CONFIG = {
    "use_real_apis": False,  # Sempre usar mocks
    "skip_on_error": False,  # Não pular testes em caso de erro
    "mock_external_services": True,  # Simular serviços externos
    "allow_real_database": False,  # Não permitir banco real em testes
}
