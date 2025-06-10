from together import Together
import os
import pandas as pd
import re

def gerar_relatorio(codSerie: str, dataframe: pd.DataFrame):
    """
    :arg codSerie: string contendo o código da série do IPEA
    :arg dataframe: dataframe contendo todos os dados da série do IPEA

    :return retorna uma string com marcações markdown contedo um relatório gerado pela DeepSeek R1 Distill Llama 70B Free sobre as últimas 100 atualizações da série parametrizada
    """
    if dataframe.empty or codSerie == '':
        raise Exception("Parametros incorretos.")

    dataframe = dataframe.sort_index(ascending=False)  # Ordena do mais atual para o mais antigo
    csv_text = dataframe.head(100).to_csv(index=True)  # Limita em <5000 tokens de entrada para que restem ~3200 tokens de saída

    prompt = f"""Você deve analisar a seguinte série temporal financeira do IPEA. Com base nos dados a seguir, gere uma análise em linguagem natural precisa e completa sem limite de caracteres mas em nível profissional em relação a série {codSerie} do IPEA: 
                
                 1. Resumo sobre o que se trata a série temporal financeira observada.
                 2. Uma descrição da tendência observada (crescimento, queda, estabilidade etc.);
                 3. Interpretação dos principais eventos que influenciaram os dados;
                 4. Classificação da anomalia (se presente) e possíveis causas;
                 5. Implicações para investidores e/ou formuladores de políticas públicas;
                 6. Sugestões de ação ou atenção, baseadas na interpretação dos dados;
                 7. Nomes de empresas brasileiras ligadas ao setor (se aplicável).
                
                 A saída deve ser compreensível para um gestor público ou investidor, clara e fundamentada em dados.
                 Evite campos em aberto.
                
                 Segue os dados da série no formato CSV:

                 {csv_text}"""
    try:
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")  # Pega a chave da variável de ambiente
        if not deepseek_api_key:
            raise Exception("Erro: A chave de API do DeepSeek (DEEPSEEK_API_KEY) não foi configurada. Por favor, adicione-a nas 'Secrets' do Streamlit Cloud.")
        client = Together(api_key=deepseek_api_key)  # AGORA USA A CHAVE DA VARIÁVEL DE AMBIENTE
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        text = re.sub(r'<think>.*?</think>', '', response.choices[0].message.content, flags=re.DOTALL).strip() # Regex formata o texto para remover a etapa de thinking retornada pela IA
        return text
    except:
        raise Exception("Conexão com IA falhou.")