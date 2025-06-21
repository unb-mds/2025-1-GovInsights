import pytest
from unittest.mock import patch, MagicMock

# Importa a função da sua página de relatórios (o módulo que será testado)
from src.interface.views.relatorios import relatorios_page

# --- Fixture para mockar as funções do Streamlit ---
@pytest.fixture
def mock_streamlit_elements():
    """
    Fixture para mockar as chamadas do Streamlit dentro da relatorios_page.
    Isso impede que o Streamlit tente renderizar fora de um ambiente de aplicativo real.
    """
    with patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.title') as mock_title, \
         patch('streamlit.write') as mock_write, \
         patch('streamlit.columns') as mock_columns, \
         patch('streamlit.selectbox') as mock_selectbox, \
         patch('streamlit.checkbox') as mock_checkbox, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.warning') as mock_warning, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.error') as mock_error:

        # Configuração padrão para mocks que são chamados sempre (ex: st.columns)
        mock_columns.return_value = (MagicMock(), MagicMock(), MagicMock())
        
        # 'yield' permite que você configure side_effects específicos para cada teste
        # no corpo do próprio teste, garantindo o comportamento desejado para cada cenário.
        yield {
            'markdown': mock_markdown,
            'title': mock_title,
            'write': mock_write,
            'columns': mock_columns,
            'selectbox': mock_selectbox,
            'checkbox': mock_checkbox,
            'button': mock_button,
            'warning': mock_warning,
            'success': mock_success,
            'error': mock_error
        }

# --- Testes para relatorios_page ---

# Mocks para as funções de lógica de negócio:
# IMPORTANTE: As funções são patchadas NO MÓDULO ONDE ELAS SÃO DEFINIDAS (src.core.report_logic),
# porque é de lá que 'relatorios_page' as importa. Isso garante que o mock é efetivo.
@patch('src.core.report_logic.get_available_report_periods')
@patch('src.core.report_logic.process_report_export')
def test_relatorios_page_calls_logic_and_displays_success(
    mock_process_report_export, mock_get_available_report_periods, mock_streamlit_elements
):
    """
    Testa se relatorios_page chama as funções de lógica esperadas e exibe sucesso.
    Simula que o usuário seleciona opções e clica no botão "Exportar".
    """
    # Configura o retorno das funções de lógica mockadas
    mock_get_available_report_periods.return_value = ['Maio 2023', 'Junho 2023', 'Julho 2023']
    mock_process_report_export.return_value = {
        "status": "success",
        "message": "Relatório gerado com sucesso para teste.",
        "file_name": "test_report.pdf",
        "content": "Simulated PDF content."
    }

    # Configura o comportamento dos elementos Streamlit mockados para ESTE TESTE
    # Estes side_effects simulam as entradas do usuário
    mock_streamlit_elements['selectbox'].side_effect = ['Maio 2023', 'Julho 2023', 'PDF'] 
    mock_streamlit_elements['checkbox'].side_effect = [True, False, True] # Simula: Receitas=True, Despesas=False, Alertas=True
    mock_streamlit_elements['button'].return_value = True # Simula que o botão "Exportar" foi clicado

    # Chama a função da página que está sendo testada
    relatorios_page()

    # Asserções para a lógica de negócio
    mock_get_available_report_periods.assert_called_once() # Verifica se os períodos foram buscados
    
    # Verifica se process_report_export foi chamado com os argumentos esperados,
    # com base nas seleções simuladas pelos mocks do Streamlit.
    mock_process_report_export.assert_called_once_with(
        'Maio 2023',  # start_period_selected (do mock_selectbox.side_effect[0])
        'Julho 2023', # end_period_selected (do mock_selectbox.side_effect[1])
        ['receitas', 'alertas'], # data_types_selected (baseado no mock_checkbox.side_effect)
        'PDF'         # export_format_selected (do mock_selectbox.side_effect[2])
    )

    # Asserções para a UI (verificar se as mensagens de sucesso são exibidas)
    mock_streamlit_elements['success'].assert_called_once_with("Relatório gerado com sucesso para teste.")
    mock_streamlit_elements['warning'].assert_not_called()
    mock_streamlit_elements['error'].assert_not_called()

@patch('src.core.report_logic.get_available_report_periods')
@patch('src.core.report_logic.process_report_export')
def test_relatorios_page_handles_no_data_types_selected(
    mock_process_report_export, mock_get_available_report_periods, mock_streamlit_elements
):
    """
    Testa se relatorios_page exibe um aviso quando nenhum tipo de dado é selecionado.
    """
    # Configura o retorno das funções de lógica mockadas
    mock_get_available_report_periods.return_value = ['Maio 2023', 'Junho 2023']

    # Configura o comportamento dos elementos Streamlit mockados para ESTE TESTE
    mock_streamlit_elements['selectbox'].side_effect = ['Maio 2023', 'Maio 2023', 'PDF'] # Preenche os selectbox
    mock_streamlit_elements['checkbox'].side_effect = [False, False, False] # Simula NENHUM tipo de dado selecionado
    mock_streamlit_elements['button'].return_value = True # Botão Exportar clicado

    relatorios_page()

    # Asserções
    mock_get_available_report_periods.assert_called_once() # Ainda deve ser chamado para popular o selectbox
    mock_process_report_export.assert_not_called() # NÃO deve tentar processar se não há dados selecionados
    mock_streamlit_elements['warning'].assert_called_once_with("Por favor, selecione pelo menos um tipo de dado para exportar.")
    mock_streamlit_elements['success'].assert_not_called()
    mock_streamlit_elements['error'].assert_not_called()

@patch('src.core.report_logic.get_available_report_periods')
@patch('src.core.report_logic.process_report_export')
def test_relatorios_page_displays_error_on_export_failure(
    mock_process_report_export, mock_get_available_report_periods, mock_streamlit_elements
):
    """
    Testa se relatorios_page exibe um erro se o processamento do relatório falhar.
    """
    # Configura o retorno das funções de lógica mockadas
    mock_get_available_report_periods.return_value = ['Maio 2023']
    mock_process_report_export.return_value = {
        "status": "error",
        "message": "Erro ao gerar relatório."
    }

    # Configura o comportamento dos elementos Streamlit mockados para ESTE TESTE
    mock_streamlit_elements['selectbox'].side_effect = ['Maio 2023', 'Maio 2023', 'PDF'] # Preenche os selectbox
    mock_streamlit_elements['checkbox'].side_effect = [True, False, False] # Simula "Receitas" selecionado
    mock_streamlit_elements['button'].return_value = True # Botão Exportar clicado

    relatorios_page()

    # Asserções
    mock_get_available_report_periods.assert_called_once() # Ainda deve ser chamado
    mock_process_report_export.assert_called_once() # DEVE tentar processar, mesmo que falhe
    mock_streamlit_elements['error'].assert_called_once_with("Erro ao gerar relatório.")
    mock_streamlit_elements['warning'].assert_not_called()
    mock_streamlit_elements['success'].assert_not_called()

@patch('src.core.report_logic.get_available_report_periods')
@patch('src.core.report_logic.process_report_export')
def test_relatorios_page_renders_basic_elements(
    mock_process_report_export, mock_get_available_report_periods, mock_streamlit_elements
):
    """
    Testa se os componentes básicos do Streamlit são chamados para renderizar a página.
    Simula que o botão "Exportar" NÃO foi clicado.
    """
    # Configura o retorno das funções de lógica mockadas
    mock_get_available_report_periods.return_value = ['Maio 2023']

    # Configura o comportamento dos elementos Streamlit mockados para ESTE TESTE
    mock_streamlit_elements['selectbox'].side_effect = ['Maio 2023', 'Maio 2023', 'PDF'] # Preenche os selectbox
    mock_streamlit_elements['checkbox'].side_effect = [False, False, False] # Simula estado inicial (nada selecionado)
    mock_streamlit_elements['button'].return_value = False # Simula que o botão NÃO foi clicado

    relatorios_page()

    # Verifica se os elementos de UI do Streamlit foram chamados para renderizar a página
    mock_streamlit_elements['markdown'].assert_called()
    mock_streamlit_elements['selectbox'].assert_called() # Agora deve ser chamado 3 vezes para os selectboxes
    mock_streamlit_elements['checkbox'].assert_called() # Agora deve ser chamado 3 vezes para os checkboxes
    mock_streamlit_elements['button'].assert_called_once_with("Exportar Relatório") # Verifica o botão é renderizado
    mock_get_available_report_periods.assert_called_once() # Verifica se buscou os períodos

    # Nenhuma mensagem de status deve ser exibida se o botão não foi clicado e nenhum processamento foi feito
    mock_streamlit_elements['warning'].assert_not_called()
    mock_streamlit_elements['success'].assert_not_called()
    mock_streamlit_elements['error'].assert_not_called()
    mock_process_report_export.assert_not_called() # NÃO deve ter processado a exportação se o botão não foi clicado