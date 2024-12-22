import streamlit as st  
import pandas as pd  
import psycopg2  
from psycopg2.extras import RealDictCursor  
import plotly.express as px  
from collections import Counter  

# Fonction pour se connecter à PostgreSQL et charger les données  
@st.cache_data  
def load_data():  
    db_config = {  
        "user": "airflow",  
        "password": "airflow",  
        "host": "postgres_container",  
        "port": "5432",  
        "database": "postgres"  
    }  

    conn = psycopg2.connect(  
        dbname=db_config['database'],  
        user=db_config['user'],  
        password=db_config['password'],  
        host=db_config['host'],  
        port=db_config['port']  
    )  

    cursor = conn.cursor(cursor_factory=RealDictCursor)  
    query = "SELECT book_id, title, author_name, price, rating, image FROM books_analytics;"  
    cursor.execute(query)  
    rows = cursor.fetchall()  
    cursor.close()  
    conn.close()  

    return pd.DataFrame(rows)  

# Charger les données depuis PostgreSQL avec gestion d'erreurs  
try:  
    data = load_data()  
except Exception as e:  
    st.error(f"Impossible de charger les données. Vérifiez la connexion à la base PostgreSQL. Erreur : {e}")  
    st.stop()  

# Préparation des données  
data["rating_num"] = data["rating"].str.replace(" out of 5 stars", "").astype(float)  

# Configuration de la page  
st.set_page_config(page_title="Streamlit Dashboard", page_icon="📊", layout="centered")  

# Dictionnaires pour les textes en plusieurs langues  
texts = {  
    'fr': {  
        'title': "📚 Top 100 Best-Sellers en Data Engineering : Insights Visuels",  
        'welcome': "Bienvenue dans le tableau de bord d'analyse des livres best-sellers en Data Engineering. Naviguez à travers les différentes sections pour explorer les données.",  
        'book_analysis': "Analyse des livres",  
        'top_rated': "🏆 Top 3 des livres les mieux notés",  
        'top_authors': "📚 Top 5 des auteurs les plus populaires",  
        'visualisations': "Visualisations",  
        'frequent_words': "🔍 Mots fréquents dans les titres des livres",  
        'price_rating_correlation': "💰 Corrélation entre le prix et les notes",  
        'footer': "📊 **Dashboard interactif développé avec Streamlit** | Analyse des données de best-sellers",  
        'nav_home': "Accueil",  
        'nav_book_analysis': "Analyse des livres",  
        'nav_visualisations': "Visualisations"  
    },  
    'en': {  
        'title': "📚 Top 100 Best-Sellers in Data Engineering: Visual Insights",  
        'welcome': "Welcome to the best-selling Data Engineering books analysis dashboard. Navigate through different sections to explore the data.",  
        'book_analysis': "Book Analysis",  
        'top_rated': "🏆 Top 3 Rated Books",  
        'top_authors': "📚 Top 5 Most Popular Authors",  
        'visualisations': "Visualisations",  
        'frequent_words': "🔍 Frequent Words in Book Titles",  
        'price_rating_correlation': "💰 Correlation between Price and Ratings",  
        'footer': "📊 **Interactive Dashboard Developed with Streamlit** | Analysis of Best-Selling Data",  
        'nav_home': "Home",  
        'nav_book_analysis': "Book Analysis",  
        'nav_visualisations': "Visualisations"  
    }  
}  

# Sélecteur de langue  
lang = st.sidebar.selectbox("Choisissez la langue / Choose Language", options=["fr", "en"])  
lang_texts = texts[lang]  

# Navigation avec textes traduits  
st.sidebar.title("Navigation")  
page = st.sidebar.radio("Sélectionnez une section :", [lang_texts['nav_home'], lang_texts['nav_book_analysis'], lang_texts['nav_visualisations']])  

if page == lang_texts['nav_home']:  
    st.title(lang_texts['title'])  
    st.markdown(lang_texts['welcome'])  

elif page == lang_texts['nav_book_analysis']:  
    st.title(lang_texts['book_analysis'])  
    
    # 1️⃣ Top 3 des livres les mieux notés  
    st.subheader(lang_texts['top_rated'])  
    col1, col2, col3 = st.columns(3)  

    for i, col in enumerate([col1, col2, col3]):  
        with col:  
            st.markdown(f"### Top {i+1}")  
            st.image(data.iloc[i]["image"], width=200, caption=f"Par: {data.iloc[i]['author_name']}")  
    
    # 2️⃣ Top 5 des auteurs les plus fréquents  
    st.subheader(lang_texts['top_authors'])  
    top_author_name = data['author_name'].value_counts().head(5)  
    fig_author_name = px.bar(  
        x=top_author_name.index,   
        y=top_author_name.values,   
        labels={'x': 'Auteur', 'y': 'Nombre de livres'},  
        title="Auteurs les plus fréquents"  
    )  
    st.plotly_chart(fig_author_name, use_container_width=True)  

elif page == lang_texts['nav_visualisations']:  
    st.title(lang_texts['visualisations'])  

    # 3️⃣ Mots fréquents dans les titres des livres  
    st.subheader(lang_texts['frequent_words'])  
    all_words = " ".join(data["title"])  
    stop_words = {"and", "with", "the", "a", "of", "to", "in", "for", "on", "at", "by", "an", "as", "is", "from", "Edition", "Acquire", "Data", "data", "second", "Second"}  
    filtered_words = [word for word in all_words.split() if word.lower() not in stop_words]  
    word_counts = Counter(filtered_words)  
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

    # 4️⃣ Corrélation entre le prix et les notes  
    st.subheader(lang_texts['price_rating_correlation'])  
    fig_corr = px.scatter(  
        data,   
        x="price",   
        y="rating_num",   
        color="price",   
        title="Relation entre le prix et les notes",  
        labels={"price": "Prix (€)", "rating_num": "Note moyenne"},  
        hover_data=["title", "author_name", "price"]  
    )  
    st.plotly_chart(fig_corr, use_container_width=True)  

# Footer  
st.write(lang_texts['footer'])