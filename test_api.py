"""
Script de teste para a API DeepSeek-OCR no RunPod
Execute este script para testar se seu endpoint está funcionando corretamente.
"""

import requests
import base64
import json
import sys
from pathlib import Path

def test_runpod_endpoint(image_path, endpoint_url, api_key, prompt=None):
    """
    Testa o endpoint RunPod com uma imagem.

    Args:
        image_path: Caminho para a imagem a ser processada
        endpoint_url: URL do endpoint RunPod (ex: https://api.runpod.ai/v2/SEU_ENDPOINT_ID/runsync)
        api_key: Sua chave de API do RunPod
        prompt: Prompt customizado (opcional)
    """

    # Verifica se a imagem existe
    if not Path(image_path).exists():
        print(f"❌ Erro: Imagem não encontrada: {image_path}")
        return

    print(f"📁 Lendo imagem: {image_path}")

    # Lê e codifica a imagem em base64
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    print(f"✅ Imagem codificada em base64: {len(image_base64)} caracteres")

    # Prepara o payload
    payload = {
        "input": {
            "image_base64": image_base64
        }
    }

    # Adiciona prompt customizado se fornecido
    if prompt:
        payload["input"]["prompt"] = prompt

    # Prepara os headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"\n🚀 Enviando requisição para: {endpoint_url}")
    print(f"📦 Payload: {json.dumps({k: v if k != 'image_base64' else f'{v[:50]}...' for k, v in payload['input'].items()}, indent=2)}")

    # Envia a requisição
    try:
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=300)

        # Verifica o status
        if response.status_code == 200:
            result = response.json()

            print("\n" + "="*80)
            print("✅ SUCESSO!")
            print("="*80)

            # Exibe o resultado
            if "output" in result:
                output = result["output"]

                if "text" in output:
                    print(f"\n📄 Texto extraído ({len(output['text'])} caracteres):")
                    print("-" * 80)
                    print(output["text"])
                    print("-" * 80)

                    # Salva o resultado em um arquivo
                    output_file = Path(image_path).stem + "_output.txt"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(output["text"])
                    print(f"\n💾 Resultado salvo em: {output_file}")

                if "status" in output:
                    print(f"\n📊 Status: {output['status']}")

                if "job_id" in output:
                    print(f"🆔 Job ID: {output['job_id']}")

            else:
                print("\n⚠️ Resposta inesperada:")
                print(json.dumps(result, indent=2))

        else:
            print(f"\n❌ Erro HTTP {response.status_code}")
            print(f"Resposta: {response.text}")

    except requests.exceptions.Timeout:
        print("\n❌ Timeout: A requisição demorou muito tempo (>5 minutos)")
        print("💡 Dica: Tente com uma imagem menor ou aumente o timeout")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro na requisição: {e}")


def main():
    """Função principal - Execute este script diretamente"""

    print("="*80)
    print("🧪 TESTE DO ENDPOINT DEEPSEEK-OCR NO RUNPOD")
    print("="*80)

    # CONFIGURE AQUI SUAS CREDENCIAIS
    # Substitua pelos seus valores reais:

    ENDPOINT_URL = "https://api.runpod.ai/v2/SEU_ENDPOINT_ID/runsync"
    API_KEY = "SUA_API_KEY_AQUI"
    IMAGE_PATH = "exemplo.jpg"  # Coloque o caminho da sua imagem

    # Prompts disponíveis (descomente o que você quiser usar):
    PROMPT = "<image>\n<|grounding|>Convert the document to markdown. "  # Padrão: documentos
    # PROMPT = "<image>\n<|grounding|>OCR this image."  # Outras imagens
    # PROMPT = "<image>\nFree OCR. "  # Sem layouts
    # PROMPT = "<image>\nParse the figure."  # Figuras em documentos
    # PROMPT = "<image>\nDescribe this image in detail."  # Descrição geral

    # Verifica se as credenciais foram configuradas
    if "SEU_ENDPOINT_ID" in ENDPOINT_URL or "SUA_API_KEY" in API_KEY:
        print("\n⚠️  ATENÇÃO: Você precisa configurar suas credenciais primeiro!")
        print("\n📝 Edite este arquivo e preencha:")
        print("   - ENDPOINT_URL: URL do seu endpoint RunPod")
        print("   - API_KEY: Sua chave de API do RunPod")
        print("   - IMAGE_PATH: Caminho para a imagem que você quer testar")
        print("\n💡 Você pode encontrar essas informações no painel do RunPod:")
        print("   https://www.runpod.io/console/serverless")
        return

    # Executa o teste
    test_runpod_endpoint(IMAGE_PATH, ENDPOINT_URL, API_KEY, PROMPT)


if __name__ == "__main__":
    main()
