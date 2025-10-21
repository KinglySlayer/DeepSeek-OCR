# DeepSeek-OCR no RunPod Serverless

Este repositório está configurado para funcionar no ambiente Serverless da RunPod.

## Arquivos Criados

1. **handler.py** - O "garçom" que recebe requisições e processa imagens
2. **Dockerfile** - Instruções para construir o ambiente no RunPod
3. **requirements.txt** - Todas as dependências necessárias (atualizado)

## Como Fazer o Deploy no RunPod Serverless

### Passo 1: Faça Push deste Repositório para o GitHub

```bash
git add .
git commit -m "Add RunPod Serverless support"
git push origin main
```

### Passo 2: Crie um Endpoint Serverless na RunPod

1. Acesse [RunPod Serverless](https://www.runpod.io/console/serverless)
2. Clique em "New Endpoint"
3. Configure:
   - **Name**: DeepSeek-OCR
   - **Select GPU**: RTX A5000 ou superior (recomendado)
   - **Container Image**: Deixe em branco (usará o Dockerfile)
   - **Container Disk**: 20GB (mínimo)
   - **Environment Variables**: Nenhuma necessária
   - **Docker Build**: Marque "Build from GitHub"
   - **GitHub Repository**: `KinglySlayer/DeepSeek-OCR`
   - **Branch**: `main`

4. Clique em "Deploy"

### Passo 3: Aguarde o Build

O build pode levar 10-20 minutos. Você verá:
- Download das dependências
- Instalação do PyTorch
- Instalação do flash-attention (a parte mais demorada)
- Build concluído ✅

## Como Usar a API

### Formato da Requisição

Envie uma requisição POST para o endpoint com o seguinte formato JSON:

```json
{
  "input": {
    "image_base64": "sua_imagem_codificada_em_base64_aqui",
    "prompt": "<image>\n<|grounding|>Convert the document to markdown. "
  }
}
```

### Exemplo em Python

```python
import requests
import base64

# Leia sua imagem e converta para base64
with open("documento.jpg", "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

# Configure sua requisição
url = "https://api.runpod.ai/v2/SEU_ENDPOINT_ID/runsync"
headers = {
    "Authorization": "Bearer SUA_API_KEY",
    "Content-Type": "application/json"
}

payload = {
    "input": {
        "image_base64": image_base64,
        "prompt": "<image>\n<|grounding|>Convert the document to markdown. "
    }
}

# Envie a requisição
response = requests.post(url, json=payload, headers=headers)
result = response.json()

# O texto extraído estará em result["output"]["text"]
print(result["output"]["text"])
```

### Exemplo em cURL

```bash
curl -X POST https://api.runpod.ai/v2/SEU_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "image_base64": "BASE64_STRING_AQUI"
    }
  }'
```

## Prompts Disponíveis

Você pode usar diferentes prompts para diferentes tipos de OCR:

```python
# Documentos (padrão)
"<image>\n<|grounding|>Convert the document to markdown. "

# Outras imagens
"<image>\n<|grounding|>OCR this image."

# Sem layouts
"<image>\nFree OCR. "

# Figuras em documentos
"<image>\nParse the figure."

# Descrição geral
"<image>\nDescribe this image in detail."
```

## Troubleshooting

### Build Falhou?
- Verifique se todos os arquivos (handler.py, Dockerfile, requirements.txt) estão no repositório
- Certifique-se de que o repositório é público ou você configurou credenciais do GitHub

### Timeout?
- Aumente o "Container Disk" para 30GB
- Use uma GPU mais potente (A100 se disponível)

### Erro de Memória?
- Reduza o tamanho da imagem antes de enviar
- Use uma GPU com mais VRAM (A100 tem 40GB)

## Custos Estimados

- **Build**: Gratuito (uma vez)
- **Idle**: $0.00/hora (não cobra quando não está processando)
- **Processamento**: ~$0.16-0.50 por hora de GPU ativa (depende da GPU escolhida)
- **Modelo de cobrança**: Pay-per-second (você só paga pelos segundos que a GPU está processando)

## Testando Localmente (Opcional)

Se você quiser testar localmente antes do deploy:

```bash
# Construa a imagem Docker
docker build -t deepseek-ocr .

# Execute o container
docker run --gpus all -p 8000:8000 deepseek-ocr
```

## Suporte

Para problemas ou dúvidas:
- Issues: https://github.com/KinglySlayer/DeepSeek-OCR/issues
- RunPod Docs: https://docs.runpod.io/serverless/overview
