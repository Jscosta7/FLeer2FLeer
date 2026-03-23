# Usa uma imagem oficial mínima do Python 3.9
FROM python:3.9-slim

# Evita que o instalador do tshark trave pedindo interação do usuário no terminal
ENV DEBIAN_FRONTEND=noninteractive

# Garante que os prints do Python apareçam na tela em tempo real (sem buffer)
ENV PYTHONUNBUFFERED=1

# Atualiza os pacotes, instala o tshark e limpa o cache para manter a imagem pequena
RUN apt-get update && \
    apt-get install -y tshark && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instala o pandas
RUN pip install --no-cache-dir pandas

# Define o diretório de trabalho dentro do container
WORKDIR /app

# O comando padrão ao rodar o container
CMD ["python", "analise_completa.py"]