import pandas as pd

def gerar_relatorio_com_busca_externa_stream(codSerie: str, dataframe: pd.DataFrame, callback=None):
    """
    Versão com streaming e busca externa, que utiliza feedparser, da função gerar_relatorio
    
    :param codSerie: Código da série do IPEA
    :param dataframe: DataFrame com os dados da série
    :param callback: Função callback para receber o texto conforme é gerado (opcional)
    :return: Texto completo do relatório
    """
    from together import Together
    import ipeadatapy as ip
    
    if dataframe.empty or codSerie == '':
        raise Exception("Parametros incorretos.")

    # Obter informações detalhadas da série
    try:
        descricaoSerie = ip.describe(codSerie)
        nomeSerie = descricaoSerie.iloc[0,0] if len(descricaoSerie) > 0 else "Série não identificada"
        comentarioSerie = descricaoSerie.iloc[6,0] if len(descricaoSerie) > 6 else "Comentário não disponível"
        
        # Limpar dados vazios ou NaN e limitar comentário a 150 caracteres
        if pd.isna(nomeSerie) or nomeSerie == "":
            nomeSerie = f"Série {codSerie}"
        if pd.isna(comentarioSerie) or comentarioSerie == "":
            comentarioSerie = "Descrição não disponível para esta série"
        else:
            comentarioSerie = comentarioSerie[:150]
            
        print(f"📊 Série: {nomeSerie}")
        print(f"📝 Comentário: {comentarioSerie[:100]}...")
        
    except Exception as e:
        print(f"⚠️ Erro ao obter informações da série: {e}")
        nomeSerie = f"Série {codSerie}"
        comentarioSerie = "Descrição não disponível para esta série"

    dataframe = dataframe.sort_index(ascending=False)
    
    # Extrair apenas a coluna VALUE para otimizar o prompt (índice já contém a data)
    try:
        # Verificar quantas colunas existem
        num_cols = len(dataframe.columns)
        print(f"📊 DataFrame: {dataframe.shape} colunas - {list(dataframe.columns)}")
        
        # Usar a última coluna como VALUE (geralmente é a coluna de valores)
        value_col_idx = num_cols - 1
        
        # Extrair os últimos 300 registros com a coluna de valores
        # O índice já contém a informação de data
        df_otimizado = dataframe.iloc[:300, [value_col_idx]].copy()
        
        # Renomear a coluna para facilitar leitura
        df_otimizado.columns = ['Valor']
        csv_text = df_otimizado.to_csv(index=True)  # Mantém o índice (data)
        print(f"✅ CSV otimizado gerado com {len(df_otimizado)} linhas - apenas coluna Valor + índice de data")
        
    except Exception as e:
        print(f"⚠️ Erro na otimização do CSV: {e}")
        # Fallback seguro: usar todo o DataFrame limitado
        csv_text = dataframe.head(50).to_csv(index=True)
    
    # Busca externa por notícias (mesma lógica da função original)
    def buscar_noticias_google(query):
        try:
            import feedparser
            url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=pt-BR&gl=BR&ceid=BR:pt"
            feed = feedparser.parse(url)
            
            noticias = []
            for entry in feed.entries[:5]:
                noticias.append({
                    'titulo': entry.title,
                    'link': entry.link,
                    'data': entry.published if hasattr(entry, 'published') else 'N/A',
                    'resumo': entry.summary if hasattr(entry, 'summary') else 'N/A'
                })
            
            return noticias
        except Exception as e:
            print(f"Erro ao buscar notícias: {e}")
            return []
    
    # Busca notícias relacionadas
    termos_busca = [
        f"IPEA {codSerie}",
        f"{nomeSerie} Brasil",
        f"economia brasileira {nomeSerie.split()[-1] if nomeSerie else 'indicadores'}",
        "dados econômicos Brasil IPEA",
        f"análise econômica {nomeSerie.split()[0] if nomeSerie else 'atual'}"
    ]
    
    todas_noticias = []
    for termo in termos_busca:
        noticias = buscar_noticias_google(termo)
        todas_noticias.extend(noticias)
    
    # Formata as notícias para incluir no prompt (versão resumida)
    contexto_noticias = ""
    if todas_noticias:
        contexto_noticias = f"\n\nNOTÍCIAS RELACIONADAS À SÉRIE '{nomeSerie}':\n"
        for i, noticia in enumerate(todas_noticias[:5], 1):  # Apenas 5 notícias
            contexto_noticias += f"{i}. {noticia['titulo'][:100]}...\n"  # Título limitado a 100 chars
    else:
        contexto_noticias = f"\n\nNOTA: Análise baseada no contexto econômico brasileiro atual.\n"
    
    prompt = f"""Analise esta série temporal financeira real do IPEA e responda EXCLUSIVAMENTE EM PORTUGUÊS BRASILEIRO:

    SÉRIE: {codSerie} - {nomeSerie}

    Gere uma análise profissional em português brasileiro abordando:
    1. Resumo da série temporal observada
    2. Tendência observada (crescimento, queda, estabilidade)
    3. Principais eventos que influenciaram os dados
    4. Anomalias e possíveis causas
    5. Implicações para investidores/formuladores de políticas
    6. Sugestões de ação
    7. Empresas brasileiras do setor (se aplicável)
    8. Correlação com as notícias fornecidas

    IMPORTANTE: Responda APENAS em português brasileiro, sem usar expressões em inglês.

    Dados da série (CSV):
    {csv_text}
    
    {contexto_noticias}
    """
    
    try:
        client = Together(api_key='31c6c1ddf940cd1ac1ad20db676e21745a49f1975e5913ec4ecfac8969c431ab')
        
        # Fazer streaming da resposta
        stream = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=4000,
            temperature=0.7,
            stream=True  # Habilita streaming
        )
        
        full_text = ""
        thinking_buffer = ""
        in_thinking = False
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                
                # Filtrar tags <think> em tempo real
                for char in content:
                    if char == '<' and not in_thinking:
                        thinking_buffer = '<'
                    elif in_thinking:
                        thinking_buffer += char
                        if thinking_buffer.endswith('</think>'):
                            in_thinking = False
                            thinking_buffer = ""
                    elif thinking_buffer:
                        thinking_buffer += char
                        if thinking_buffer == '<think>':
                            in_thinking = True
                            thinking_buffer = ""
                        elif not thinking_buffer.startswith('<'):
                            # Não é tag <think>, adicionar ao texto
                            text_to_add = thinking_buffer
                            # Escapar $ para evitar modo matemático do Markdown
                            text_to_add = text_to_add.replace('$', '\\$')
                            full_text += text_to_add
                            if callback:
                                callback(text_to_add)
                            thinking_buffer = ""
                            thinking_buffer += char
                    else:
                        # Escapar $ para evitar modo matemático do Markdown
                        escaped_char = char.replace('$', '\\$')
                        full_text += escaped_char
                        if callback:
                            callback(escaped_char)
        
        return full_text.strip()
        
    except Exception as e:
        print(f"Erro detalhado: {e}")
        raise Exception("Conexão com IA falhou.")