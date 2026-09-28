# Imagem slim do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Impede arquivos .pyc e força saída direta no terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema necessárias para compilação mínima
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências declaradas
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código-fonte da aplicação para o container
COPY . /app/

# Garante que a pasta de banco de dados exista com as permissões corretas
RUN mkdir -p /app/database

# Expõe a porta padrão do Flask
EXPOSE 5000

# Executa a aplicação
CMD ["python", "app.py"]