# Utilisez une image de base officielle de Python
FROM python:3.10-slim

# Définissez le répertoire de travail dans le conteneur
WORKDIR /streamlit

# Copiez les fichiers de votre projet dans le conteneur
COPY ./requirements.txt /streamlit/

# Installez les dépendances à partir du fichier requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install psycopg2-binary --no-cache-dir

# Assurez-vous que Streamlit est installé
RUN pip install streamlit

# Expose le port 8501 pour Streamlit
EXPOSE 8501

# Commande par défaut pour exécuter Streamlit
CMD ["streamlit", "run", "app.py","--server.runOnSave=true"]
