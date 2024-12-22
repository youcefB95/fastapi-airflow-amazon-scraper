from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import pandas as pd
import logging

# Configurez le logger
logger = logging.getLogger(__name__)

# Arguments par défaut pour le DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 15),  # Doit être dans le passé ou une date récente
    'retries': 1,
    'retry_delay': timedelta(minutes=60),
    'catchup': False,  # Evite l'exécution de DAGs pour les dates passées
}

# Fonction Python pour récupérer les livres depuis l'API FastAPI
def fetch_books_from_api(num_books=10, ti=None):
    # URL de l'API FastAPI
    url = f"http://fastapi:8000/get_books?num_books={num_books}"
    logger.warn("First step")
    
    # Faire une requête GET à l'API FastAPI
    response = requests.get(url)
    logger.warn("2nd step : Appel de l'API")
    
    if response.status_code == 200:
        logger.warn("3rd step")

        books = response.json()  # Convertir la réponse JSON en dictionnaire
        logger.info(f"Books fetched: {books}")  # Remplacer print() par logger
        # Convertir la liste de dictionnaires en DataFrame
        df = pd.DataFrame(books)
        
        # Supprimer les doublons en fonction de la colonne 'Title'
        df.drop_duplicates(subset="Title", inplace=True)
        
        # Pousser les données dans XCom
        ti.xcom_push(key='book_data', value=df.to_dict('records'))
    else:
        logger.error(f"Failed to fetch data. Status code: {response.status_code}")
        return []
    
    
def insert_book_data_into_postgres(ti):
    book_data = ti.xcom_pull(key='book_data', task_ids='fetch_books_data')
    if not book_data:
        raise ValueError("No book data found")

    postgres_hook = PostgresHook(postgres_conn_id='books_connection')
    insert_query = """
    INSERT INTO books (title, authors, price, rating)
    VALUES (%s, %s, %s, %s)
    """
    for book in book_data:
        postgres_hook.run(insert_query, parameters=(book['Title'], book['Author'], book['Price'], book['Rating']))


# Définition du DAG
dag = DAG(
    'dag_fetch_amazon_books',
    default_args=default_args,
    description='Fetch books from Amazon using FastAPI and store in Postgres',
    schedule_interval='0 0 * * *',  # Exécution quotidienne à minuit (format CRON)
    catchup=False,  # Ne pas exécuter le DAG pour les dates passées
)

# Tâche Airflow pour récupérer les livres depuis l'API FastAPI
fetch_books_task = PythonOperator(
    task_id='fetch_books_data',
    python_callable=fetch_books_from_api,  # Appel de la fonction pour récupérer les livres
    op_args=[2],  # Nombre de livres à récupérer
    dag=dag
)

create_table_task = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='books_connection',
    sql="""
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        authors TEXT,
        price TEXT,
        rating TEXT
    );
    """,
    dag=dag,
)

insert_book_data_task = PythonOperator(
    task_id='insert_book_data',
    python_callable=insert_book_data_into_postgres,
    dag=dag,
)

# Définition des dépendances
fetch_books_task >> create_table_task >> insert_book_data_task
