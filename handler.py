"""
RunPod Serverless Handler for DeepSeek-OCR
Este arquivo funciona como uma API que recebe imagens e retorna o texto extraído.
"""

import runpod
from transformers import AutoModel, AutoTokenizer
import torch
import base64
from io import BytesIO
from PIL import Image
import os
import json

# ---------------------------------------------------------------------------- #
#                      Carregamento do Modelo (A Preparação)                     #
# ---------------------------------------------------------------------------- #
# Esta parte do código roda APENAS UMA VEZ, quando o "worker" (a GPU) inicia.
# Ele carrega o modelo na memória para que esteja pronto para os pedidos.

print("="*80)
print("INICIANDO DEEPSEEK-OCR SERVERLESS HANDLER")
print("="*80)

# Verifica se há uma GPU disponível
if not torch.cuda.is_available():
    raise RuntimeError("CUDA is not available. This model requires a GPU.")

print(f"GPU disponível: {torch.cuda.get_device_name(0)}")
print(f"Memória GPU total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

model_name = 'deepseek-ai/DeepSeek-OCR'
print(f"\nCarregando tokenizer de: {model_name}")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
print("Tokenizer carregado com sucesso!")

print(f"\nCarregando modelo de: {model_name}")
print("(Isso pode levar alguns minutos...)")
model = AutoModel.from_pretrained(
    model_name,
    trust_remote_code=True,
    use_safetensors=True
).cuda().to(torch.bfloat16).eval()

print("\n" + "="*80)
print("MODELO CARREGADO COM SUCESSO! PRONTO PARA RECEBER REQUISIÇÕES.")
print("="*80 + "\n")


# ---------------------------------------------------------------------------- #
#                           A Função Principal (O Serviço)                       #
# ---------------------------------------------------------------------------- #
# Esta função é chamada TODA VEZ que você envia uma requisição para a API.
def handler(job):
    """
    Recebe um 'job' com os dados da requisição, processa a imagem e retorna o texto.

    Formato esperado do input:
    {
        "image_base64": "base64_encoded_image_string",
        "prompt": "optional custom prompt" (default: markdown conversion)
    }

    Formato da resposta:
    {
        "text": "extracted text from image"
    }
    """
    print(f"\n{'='*60}")
    print(f"Novo job recebido: {job['id']}")
    print(f"{'='*60}")

    try:
        # Pega os dados de entrada do job
        job_input = job['input']

        # Extrai a imagem codificada em base64 da entrada
        image_base64 = job_input.get('image_base64')
        if not image_base64:
            error_msg = "Nenhuma imagem em base64 foi fornecida. Use a chave 'image_base64'."
            print(f"ERRO: {error_msg}")
            return {"error": error_msg}

        # Decodifica a imagem de base64 para um formato que o Python entende
        print("Decodificando imagem de base64...")
        try:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
            print(f"Imagem decodificada: {image.size[0]}x{image.size[1]} pixels, modo: {image.mode}")

            # Salva a imagem temporariamente, pois o modelo espera um caminho de arquivo
            temp_image_path = f"temp_image_{job['id']}.png"
            image.save(temp_image_path)
            print(f"Imagem salva temporariamente em: {temp_image_path}")

        except Exception as e:
            error_msg = f"Falha ao decodificar a imagem: {str(e)}"
            print(f"ERRO: {error_msg}")
            return {"error": error_msg}

        # Define o prompt para o modelo (usa o padrão para converter documento em markdown)
        prompt = job_input.get('prompt', "<image>\n<|grounding|>Convert the document to markdown. ")
        print(f"Prompt usado: {prompt[:100]}...")

        print("\nIniciando inferência do OCR...")
        print("(Processando imagem com o modelo DeepSeek-OCR...)")

        # Executa o modelo de OCR na imagem
        try:
            resultado_texto = model.infer(
                tokenizer,
                prompt=prompt,
                image_file=temp_image_path
            )
            print("Inferência concluída com sucesso!")
            print(f"Texto extraído: {len(resultado_texto)} caracteres")

        except Exception as e:
            error_msg = f"Erro durante a inferência do modelo: {str(e)}"
            print(f"ERRO: {error_msg}")
            return {"error": error_msg}

        finally:
            # Garante que a imagem temporária seja deletada
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
                print(f"Arquivo temporário {temp_image_path} removido.")

        print(f"{'='*60}")
        print(f"Job {job['id']} concluído com sucesso!")
        print(f"{'='*60}\n")

        # Devolve o resultado em formato JSON
        return {
            "text": resultado_texto,
            "status": "success",
            "job_id": job['id']
        }

    except Exception as e:
        error_msg = f"Erro inesperado no handler: {str(e)}"
        print(f"\nERRO CRÍTICO: {error_msg}\n")
        return {"error": error_msg, "status": "failed"}


# ---------------------------------------------------------------------------- #
#                                 A Inicialização                              #
# ---------------------------------------------------------------------------- #
# Esta linha inicia o serviço e diz para a RunPod qual função usar como "handler".
print("Iniciando RunPod Serverless...")
runpod.serverless.start({"handler": handler})
