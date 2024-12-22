import psycopg2
import pandas as pd

# Configuration de la connexion
DB_HOST = "172.21.0.5"      # Adresse de la base de données
DB_PORT = "5432"           # Port par défaut de PostgreSQL
DB_NAME = "postgres"       # Nom de la base de données
DB_USER = "airflow"       # Nom d'utilisateur PostgreSQL
DB_PASSWORD = "airflow"   # Mot de passe PostgreSQL

def fetch_data(query):
    """
    Connecte à la base de données PostgreSQL, exécute une requête et retourne les résultats.
    """
    try:
        # Connexion à la base de données
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Connexion réussie à la base de données.")

        # Exécution de la requête
        cursor = connection.cursor()
        cursor.execute(query)

        # Récupération des résultats
        columns = [desc[0] for desc in cursor.description]  # Noms des colonnes
        data = cursor.fetchall()  # Données

        # Fermeture du curseur
        cursor.close()

        # Retourne les données dans un DataFrame Pandas
        return pd.DataFrame(data, columns=columns)
    except Exception as e:
        print(f"Erreur lors de la connexion ou de l'exécution de la requête : {e}")
        return None
    finally:
        if connection:
            connection.close()
            print("Connexion à la base de données fermée.")

# Exemple de requête
query = "SELECT * FROM books LIMIT 10;"
df = fetch_data(query)

# Affiche les données
if df is not None:
    print(df)
