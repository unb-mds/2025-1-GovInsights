import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# REMOVA estas duas linhas daqui. Elas serão movidas para dentro da função load_mistral_model.
# tokenizer, model = load_mistral_model()

# --- Configuração e Carregamento do Modelo Mistral 7B para CPU ---
# O @st.cache_resource já garante que só será carregado uma vez,
# mas as chamadas Streamlit dentro dela precisam ser feitas APÓS set_page_config.
@st.cache_resource
def get_tokenizer_and_model(): # Renomeado para maior clareza
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # AQUI ESTAVAM st.spinner e st.success. Elas serão chamadas APENAS quando get_tokenizer_and_model
    # for realmente invocada pela primeira vez, o que acontecerá DEPOIS de set_page_config no app.py.
    
    # Adicione uma mensagem de carregamento inicial que não seja um st.spinner
    # st.write("Aguarde o carregamento do modelo de IA (apenas na primeira execução).") # Opção alternativa de feedback visual

    try:
        # st.spinner e st.success podem ser adicionados AQUI se for a PRIMEIRA VEZ que a função é executada,
        # mas como está dentro de @st.cache_resource, a mensagem apareceria apenas na primeira carga.
        # O problema é a chamada `st.spinner` etc. quando o módulo é importado.
        
        # Vamos usar um padrão que não quebre o set_page_config
        # As mensagens de spinner e success agora serão gerenciadas pela função que chama este cache.
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="cpu",
            torch_dtype=torch.float32
        )
        model.eval()
        return tokenizer, model
    except Exception as e:
        # Mantemos o tratamento de erro aqui para o caso de falha de carregamento
        st.error(f"Erro ao carregar o modelo Mistral 7B na CPU: {e}")
        st.info("O modelo Mistral 7B requer muita RAM para rodar na CPU (15-25GB). Verifique sua memória RAM disponível.")
        st.stop()

# Agora, a função `generate_intelligent_report` precisará chamar `get_tokenizer_and_model()` para obter o tokenizer e o modelo.
def generate_intelligent_report(series_name: str, series_data: str, user_prompt: str = "") -> str:
    """
    Gera um relatório inteligente usando o modelo Mistral-7B com base nos dados da série.
    """
    if not series_data:
        return "Nenhum dado de série fornecido para gerar o relatório."

    # Carrega o tokenizer e o modelo DENTRO da função que os utiliza.
    # O @st.cache_resource garante que eles só serão carregados uma vez.
    tokenizer, model = get_tokenizer_and_model() # AQUI é onde eles são realmente obtidos

    formatted_data = f"Nome da Série: {series_name}\nDados:\n{series_data}\n"

    messages = [
        {"role": "user", "content": f"""Com base nos seguintes dados de série histórica, gere um relatório inteligente, detalhado e conciso. Inclua:
        1. Uma breve descrição do que os dados representam.
        2. Principais tendências observadas (crescimento, declínio, estabilidade).
        3. Pontos de destaque ou anomalias (picos, vales, mudanças abruptas).
        4. Possíveis insights ou conclusões sobre o comportamento da série.

        Formate o relatório em Markdown para facilitar a leitura.

        {formatted_data}
        {user_prompt}
        """}
    ]

    encodings = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to(model.device)

    with st.spinner("Mistral 7B está gerando o relatório... Isso pode demorar bastante na CPU."):
        generated_ids = model.generate(
            encodings,
            max_new_tokens=700,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )

    generated_text = tokenizer.decode(generated_ids[0][encodings.shape[1]:], skip_special_tokens=True)

    return generated_text

if __name__ == "__main__":
    st.title("Teste de Geração de Relatório com Mistral 7B")
    test_series_name = "Exemplo de Vendas Mensais"
    test_series_data = """Data,Valor
2023-01-01,100
2023-02-01,105
2023-03-01,110
2023-04-01,120
2023-05-01,115
2023-06-01,130
2023-07-01,140
2023-08-01,135
2023-09-01,150
2023-10-01,160
2023-11-01,155
2023-12-01,170
"""
    test_user_prompt = "Foque nas tendências de final de ano."

    report = generate_intelligent_report(test_series_name, test_series_data, test_user_prompt)
    st.subheader("Relatório Gerado:")
    st.markdown(report)