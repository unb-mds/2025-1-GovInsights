import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch # Continua sendo necessário para PyTorch
# from bitsandbytes.cuda_setup.main import get_compute_capability # Não é necessário se não usar bnb

# --- Configuração e Carregamento do Modelo Mistral 7B para CPU ---
@st.cache_resource
def load_mistral_model():
    # AQUI VOCÊ REMOVE A CONFIGURAÇÃO DO BITSANDBYTES
    # quantization_config = BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_compute_dtype=torch.bfloat16,
    #     bnb_4bit_use_double_quant=False,
    # )

    model_name = "mistralai/Mistral-7B-Instruct-v0.2" # Versão instrucional do Mistral
    st.spinner(f"Carregando o modelo {model_name} na CPU... Isso pode levar um tempo considerável e muita RAM.")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Carrega o modelo sem quantização, forçando o uso da CPU
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            # remove 'quantization_config=quantization_config',
            device_map="cpu", # Força o carregamento na CPU
            torch_dtype=torch.float32 # Use float32 para maior precisão na CPU, consome mais RAM
        )
        model.eval() # Coloca o modelo em modo de avaliação
        st.success("Modelo Mistral 7B carregado com sucesso na CPU!")
        return tokenizer, model
    except Exception as e:
        st.error(f"Erro ao carregar o modelo Mistral 7B na CPU: {e}")
        st.info("O modelo Mistral 7B requer muita RAM para rodar na CPU (15-25GB). Verifique sua memória RAM disponível.")
        st.stop() # Para a execução da Streamlit se o modelo não carregar

tokenizer, model = load_mistral_model()

# --- Função para Gerar o Relatório Inteligente ---
# Este código permanece o mesmo.
def generate_intelligent_report(series_name: str, series_data: str, user_prompt: str = "") -> str:
    """
    Gera um relatório inteligente usando o modelo Mistral-7B com base nos dados da série.

    Args:
        series_name (str): O nome da série de dados.
        series_data (str): Os dados da série formatados como texto (ex: "Data,Valor\n2023-01-01,100\n...").
        user_prompt (str): Um prompt adicional do usuário para guiar a geração.

    Returns:
        str: O relatório inteligente gerado.
    """
    if not series_data:
        return "Nenhum dado de série fornecido para gerar o relatório."

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