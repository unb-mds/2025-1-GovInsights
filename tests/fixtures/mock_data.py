"""
Dados mockados para testes unitários e de integração do GovInsights
"""
import pandas as pd
from datetime import datetime, timedelta

# Mock de dados da API do IPEA para testes
MOCK_METADATA_IPEA = pd.DataFrame({
    'CODE': ['BM12_TJOVER12', 'PAN12_IGSTT12', 'SCN52_PIBPMG12', 'ERC280_VENDAS12', 'BM12_ERC280'],
    'NAME': [
        'Taxa de juros - Over/Selic - % a.m.',
        'IGS-M - Variação mensal - %',
        'PIB - Preços de mercado - R$ milhões',
        'Vendas no comércio varejista - Variação mensal - %',
        'Taxa de câmbio - R$/US$ - Média mensal'
    ],
    'MEASURE': ['%', '%', 'R$ milhões', '%', 'R$/US$'],
    'SOURCE ACRONYM': ['BCB', 'FGV', 'IBGE', 'IBGE', 'BCB'],
    'SOURCE': [
        'Banco Central do Brasil',
        'Fundação Getúlio Vargas',
        'Instituto Brasileiro de Geografia e Estatística',
        'Instituto Brasileiro de Geografia e Estatística',
        'Banco Central do Brasil'
    ],
    'LAST UPDATE': ['2025-06-27T18:04:01-03:00'] * 5,
    'THEME CODE': [1, 2, 1, 3, 1],
    'FREQUENCY': ['Mensal', 'Mensal', 'Trimestral', 'Mensal', 'Diária'],
    'BIG THEME': ['Economia', 'Finanças', 'Economia', 'Comércio', 'Economia'],
    'UNIT': ['% a.m.', '%', 'R$ milhões', '%', 'R$/US$'],
    'START': ['1986-03-01', '1989-06-01', '1996-01-01', '2000-01-01', '1995-01-02'],
    'END': ['2025-06-01', '2025-06-01', '2025-03-01', '2025-06-01', '2025-06-27']
})

MOCK_THEMES_IPEA = pd.DataFrame({
    'THEME CODE': [1, 2, 3, 4, 5],
    'THEME NAME': ['Economia', 'Finanças', 'Comércio', 'Indústria', 'Agropecuária']
})

# Mock de dados de série temporal para testes
def generate_mock_timeseries_data(code: str = 'DEFAULT', start_date: str = '2020-01-01', periods: int = 50):
    """Gera dados mockados de série temporal"""
    dates = pd.date_range(start=start_date, periods=periods, freq='ME')
    
    # Simula valores diferentes baseados no código
    if 'TJOVER' in str(code):  # Taxa de juros
        base_value = 10.5
        variation = 0.5
    elif 'PIB' in str(code):  # PIB
        base_value = 2000000
        variation = 50000
    elif 'IGS' in str(code):  # Inflação
        base_value = 0.8
        variation = 0.3
    else:
        base_value = 100
        variation = 10
    
    import numpy as np
    np.random.seed(42)  # Para resultados consistentes nos testes
    values = base_value + np.random.normal(0, variation, periods)
    
    return pd.DataFrame({
        'RAW DATE': dates,
        'VALUE': values,
        'YEAR': dates.year,
        'MONTH': dates.month
    })

# Mock de resposta da API de IA para testes
MOCK_IA_RESPONSE = "Análise econômica: Os dados mostram tendência crescente com volatilidade moderada."

# Mock de configurações do Supabase para testes
MOCK_SUPABASE_CONFIG = {
    "url": "https://test.supabase.co",
    "key": "test_key_123456789",
    "schema": "public",
    "table": "series_test"
}

# Mock de dados do banco para testes
MOCK_DATABASE_SERIES = [
    {
        "id": 1,
        "codigo_serie": "BM12_TJOVER12",
        "email_usuario": "test@example.com",
        "margem": "5.0",
        "ultima_atualizacao": "2025-06-27",
        "created_at": "2025-06-01T10:00:00Z"
    },
    {
        "id": 2,
        "codigo_serie": "PAN12_IGSTT12",
        "email_usuario": "user@test.com",
        "margem": "2.5",
        "ultima_atualizacao": "2025-06-26",
        "created_at": "2025-06-01T11:00:00Z"
    }
]

# Mock de configurações da API Together.ai para testes
MOCK_TOGETHER_CONFIG = {
    "api_key": "test_together_key_123",
    "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    "max_tokens": 4000,
    "temperature": 0.7
}

# Mock de dados para navegação Streamlit
MOCK_SESSION_STATE = {
    "page": "dashboard",
    "frequencia": "Mensal",
    "orgaos": ["IBGE", "BCB"],
    "temas": [{"THEME CODE": 1, "THEME NAME": "Economia"}],
    "serie_estatistica": {
        "CODE": "BM12_TJOVER12",
        "NAME": "Taxa de juros - Over/Selic - % a.m."
    },
    "periodo_analise": "Último ano",
    "current_page": "Dashboard"
}

# Funções auxiliares para testes
def get_mock_search_results(source_filter=None, theme_filter=None, freq_filter=None):
    """Retorna resultados de busca mockados com filtros opcionais"""
    df = MOCK_METADATA_IPEA.copy()
    
    if source_filter:
        df = df[df['SOURCE ACRONYM'].isin(source_filter)]
    if theme_filter:
        theme_codes = [t if isinstance(t, int) else t['THEME CODE'] for t in theme_filter]
        df = df[df['THEME CODE'].isin(theme_codes)]
    if freq_filter:
        df = df[df['FREQUENCY'] == freq_filter]
    
    return df.to_dict('records')

def get_mock_graph_data(code: str, period: str = "Último ano"):
    """Retorna dados mockados para gráficos baseado no período"""
    periods_map = {
        "Últimos 6 meses": 6,
        "Último ano": 12,
        "Últimos 2 anos": 24,
        "Últimos 5 anos": 60
    }
    
    periods = periods_map.get(period, 12)
    return generate_mock_timeseries_data(code, periods=periods)

def get_mock_dataframe(size=100, start_date='2020-01-01'):
    """Gera DataFrame mock para testes - compatível com gerar_pdf"""
    # Limitar o tamanho para evitar datas fora do limite
    safe_size = min(size, 500)  # Máximo 500 períodos (42 anos)
    dates = pd.date_range(start=start_date, periods=safe_size, freq='ME')
    import numpy as np
    np.random.seed(42)
    values = 100 + np.random.normal(0, 10, safe_size)
    
    # Se precisar de mais dados, usar apenas o que foi gerado
    actual_size = min(size, safe_size)
    
    # Formato compatível com a função gerar_pdf (última coluna = valores)
    return pd.DataFrame({
        'RAW DATE': dates[:actual_size],
        'CODE': ['TEST_SERIES'] * actual_size,
        'YEAR': [d.year for d in dates[:actual_size]],
        'MONTH': [d.month for d in dates[:actual_size]], 
        'VALUE': values[:actual_size]  # Última coluna para gerar_pdf
    })

def get_mock_ia_response(test_type='default'):
    """Gera resposta mock da IA baseada no tipo de teste"""
    responses = {
        'default': MOCK_IA_RESPONSE,
        'complete_analysis': """
# Análise Econômica Completa

## Resumo Executivo
Esta análise apresenta um panorama abrangente dos indicadores econômicos...

## Indicadores Principais
- PIB: Crescimento de 2.5% no período
- Inflação: Controlada em 4.2%
- Taxa de juros: Estável em 10.75%

## Projeções
As projeções indicam cenário de estabilidade para os próximos trimestres.
        """,
        'multi_chart': """
# Análise Multi-Dimensional

## Gráficos Analisados
1. Série temporal: Tendência de crescimento
2. Médias anuais: Estabilidade no período
3. Correlação: Forte correlação positiva
4. Distribuição: Normal com leve assimetria

## Conclusões
Os múltiplos gráficos confirmam a robustez dos dados analisados.
        """,
        'large_dataset': """
# Análise de Dataset Extenso

## Volume de Dados
Foram analisados {total_pontos:,} pontos de dados no período {periodo}.

## Estatísticas Principais
- Média: {media:.2f}
- Mediana: {mediana:.2f}
- Desvio padrão: {desvio_padrao:.2f}
- Variação total: {variacao_total:.1f}%

## Insights
O volume substancial de dados permite análises estatísticas robustas.
        """,
        'error_test': "Análise com dados limitados devido a restrições técnicas.",
        'corrupted_data': "Análise prejudicada por inconsistências nos dados de entrada.",
        'styled_report': """
# Relatório com Design Aprimorado

## Introdução
Este relatório utiliza elementos visuais aprimorados para melhor apresentação.

## Metodologia
- Análise quantitativa avançada
- Visualizações otimizadas
- Design responsivo

## Resultados
Os resultados demonstram eficácia da abordagem metodológica adotada.
        """,
        'performance_test': "Análise otimizada para teste de performance e tempo de resposta.",
        'empty_data_vazio': "Análise não realizada devido à ausência de dados.",
        'empty_data_minimo': "Análise limitada devido ao volume mínimo de dados disponíveis.",
        'concurrent_test': "Análise realizada em processamento concorrente."
    }
    
    response = responses.get(test_type, responses['default'])
    
    # Se contém placeholders, tentar formatá-los com dados padrão
    if '{' in response:
        try:
            response = response.format(
                total_pontos=5000,
                periodo="2020-2025",
                media=150.75,
                mediana=149.30,
                desvio_padrao=25.40,
                variacao_total=12.5
            )
        except KeyError:
            pass
    
    return response

def get_mock_ipea_response(test_type='default'):
    """Gera resposta mock da API IPEA"""
    base_response = {
        'value': [
            {
                'SERCODIGO': 'TEST_001',
                'SERNOME': 'Indicador de Teste',
                'SERUNIDADE': '%',
                'SERFREQ': 'Mensal',
                'FNTSIGLA': 'TEST'
            }
        ]
    }
    
    if test_type == 'concurrent_test':
        return {
            'value': [
                {
                    'SERCODIGO': f'CONCURRENT_{test_type}',
                    'SERNOME': f'Teste Concorrente {test_type}',
                    'SERUNIDADE': '%',
                    'SERFREQ': 'Mensal',
                    'FNTSIGLA': 'TEST'
                }
            ]
        }
    
    return base_response

# Constantes adicionais para compatibilidade
MOCK_IPEA_METADATA = MOCK_METADATA_IPEA.to_dict('records')
MOCK_SEARCH_RESULTS = get_mock_search_results()
