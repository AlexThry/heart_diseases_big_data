FROM python:3.8-slim

# Installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Installer les bibliothèques Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copier le script Python et les autres fichiers nécessaires
WORKDIR /app
COPY . /app

# Définir le script comme point d'entrée
ENTRYPOINT ["python", "fetch.py"]
