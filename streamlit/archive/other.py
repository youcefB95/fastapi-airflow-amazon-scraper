import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px  # Importation de plotly.express
#from streamlit_card import card
from streamlit.components.v1 import html
from collections import Counter  # Ajout de l'importation de Counter

# Fonction pour se connecter à PostgreSQL et charger les données
@st.cache_data
def load_data():
    # Informations de connexion à PostgreSQL
    db_config = {
        "user": "airflow",  # Remplacez par votre utilisateur
        "password": "airflow",  # Remplacez par votre mot de passe
        "host": "postgres_container",  # Remplacez par l'adresse de votre serveur (par exemple, une IP)
        "port": "5432",  # Port PostgreSQL par défaut
        "database": "postgres"  # Nom de votre base de données
    }

    # Connexion à la base de données PostgreSQL avec psycopg2
    conn = psycopg2.connect(
        dbname=db_config['database'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )
    
    # Création d'un curseur
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Exécution de la requête SQL
    query = "SELECT book_id, title, author_name, price, rating, image FROM books_analytics;"
    cursor.execute(query)
    
    # Récupération des résultats
    rows = cursor.fetchall()

    # Conversion en DataFrame Pandas
    data = pd.DataFrame(rows)

    # Fermeture du curseur et de la connexion
    cursor.close()
    conn.close()

    return data

# Charger les données depuis PostgreSQL
try:
    data = load_data()
except Exception as e:
    st.error(f"Impossible de charger les données. Vérifiez la connexion à la base PostgreSQL. Erreur : {e}")
    st.stop()


data["rating_num"] = data["rating"].map(lambda x: x.replace(" out of 5 stars", ""))

# Convertir la colonne 'rating' en type numérique (float) pour éviter l'erreur
data["rating_num"] = pd.to_numeric(data["rating_num"], errors='coerce')

# Convertir la colonne 'price' en type numérique (float) pour éviter l'erreur
#data['prices'] = round(data['price'].astype(float),2)


import streamlit as st

st.set_page_config(page_title="Streamlit Dashboard", page_icon="📊", layout="centered")









# Titre du dashboard
st.title("📚 Top 100 Best-Sellers en Data Engineering : Insights Visuels")




# 1️⃣ Graphique 1 : Top 3 des livres les mieux notés avec des cartes
st.subheader("Top 3 des livres les mieux notés")
col1, col2, col3 = st.columns(3)

df1 = data.copy()

for i,col in enumerate([col1, col2, col3]):
    with col:
        # Utilisation de HTML dans le markdown pour réduire la taille
        st.markdown(f"<h3 style='font-size:15px;'> Top {i+1}</h3>", unsafe_allow_html=True)
        st.markdown(f"""
<figure style="">
    <img src='{df1.iloc[i]["image"]}' style='width:200px;height:auto;'>
    <figcaption style="margin-top:5px; font-size:10px; color:gray;">Author: {df1.iloc[i]["author_name"]}</figcaption>
</figure>
""", unsafe_allow_html=True)# st.image(df1.iloc[i]['image'],width=200,caption="by Author")

    
    

# 2️⃣ Graphique 2 : Top 5 des auteurs les plus fréquents
st.subheader("Top 5 des auteurs les plus populaires")
top_author_name = data['author_name'].value_counts().head(5)
fig_author_name = px.bar(
    x=top_author_name.index, 
    y=top_author_name.values, 
    labels={'x': 'Auteur', 'y': 'Nombre de livres'},
    title="Auteurs les plus fréquents"
)
st.plotly_chart(fig_author_name, use_container_width=True)

# 3️⃣ Graphique 3 : Mots fréquents dans les titres des livres
st.subheader("Mots fréquents dans les titres des livres")
all_words = " ".join(data["title"])

# Liste des mots vides (stop words) à ignorer
stop_words = {"and", "with", "the", "a", "of", "to", "in", "for", "on", "at", "by", "an", "as", "is", "from","Edition","Acquire","Data",
              "data","second","Second"}

# Filtrage des mots inutiles
filtered_words = [word for word in all_words.split() if word.lower() not in stop_words]

# Comptage des mots
word_counts = Counter(filtered_words)  # Utilisation de Counter pour compter les occurrences
top_words = pd.DataFrame(word_counts.most_common(20), columns=["word", "count"])

fig_bubble = px.scatter(
    top_words, 
    x="word", 
    y="count", 
    size="count", 
    color="word",
    labels={"count": "Fréquence", "word": "Mot"},
    title="Mots les plus fréquents dans les titres des livres"
)
st.plotly_chart(fig_bubble, use_container_width=True)

# 4️⃣ Graphique 4 : Corrélation entre le prix et les notes
st.subheader("Corrélation entre le prix et les notes")
fig_corr = px.scatter(
    data, 
    x="price", 
    y="rating", 
    color="price", 
    title="Relation entre le prix et les notes",
    labels={"price": "Prix (€)", "rating": "Note moyenne"},
    hover_data=["title", "author_name", "price"]  # Affichage des informations du livre au survol
)

st.plotly_chart(fig_corr, use_container_width=True)

# Footer
st.write("📊 **Dashboard interactif développé avec Streamlit** | Analyse des données de best-sellers")
