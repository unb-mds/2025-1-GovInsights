import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig # Importar BitsAndBytesConfig
import torch

# --- Configuração e Carregamento do Modelo Mistral 7B ---
@st.cache_resource
def get_tokenizer_and_model():
    # Configuração para quantização em 4-bit (altamente recomendado para Mistral 7B em GPU)
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=False,
    )
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config, # Manter a configuração de quantização
            device_map="auto" # Usar "auto" para que use a GPU se disponível
        )
        model.eval()
        return tokenizer, model
    except Exception as e:
        st.error(f"Erro ao carregar o modelo Mistral 7B: {e}")
        st.info("Verifique se você tem acesso ao modelo no Hugging Face e se o ambiente Colab está com GPU.")
        st.stop()

# Agora, a função `generate_intelligent_report` chamará `get_tokenizer_and_model()` para obter o tokenizer e o modelo.
def generate_intelligent_report(series_name: str, series_data: str, user_prompt: str = "") -> str:
    """
    Gera um relatório inteligente usando o modelo Mistral-7B com base nos dados da série.
    """
    if not series_data:
        return "Nenhum dado de série fornecido para gerar o relatório."

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

    with st.spinner("Mistral 7B está gerando o relatório..."): # Removi "Isso pode demorar bastante na CPU"
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