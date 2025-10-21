# Dockerfile para DeepSeek-OCR no RunPod Serverless
# Base image com CUDA 11.8 e Python 3.10
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Define o diretório de trabalho
WORKDIR /workspace

# Atualiza o sistema e instala dependências básicas
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos primeiro (para aproveitar o cache do Docker)
COPY requirements.txt .

# Instala PyTorch e dependências específicas
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Instala flash-attention (pode demorar um pouco)
RUN pip install --no-cache-dir flash-attn==2.7.3 --no-build-isolation

# Copia todo o código do projeto
COPY . .

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Comando para iniciar o handler do RunPod
CMD ["python", "handler.py"]
