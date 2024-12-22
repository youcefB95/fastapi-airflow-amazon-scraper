from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import pandas as pd
import logging
from scripts.transform_data import transform_data
from scripts.insert_to_postgres import insert_to_postgres

# Configurez le logger
logger = logging.getLogger(__name__)

# Arguments par défaut pour le DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=60),
    'catchup': False,
}

# Fonction pour récupérer les livres depuis l'API FastAPI
def fetch_books_from_api(num_books=10, ti=None):
    url = f"http://fastapi:8000/get_top_books?num_books={num_books}"
    response = requests.get(url)
    if response.status_code == 200:
        books = response.json()
        logger.info(f"Books fetched: {books}")
        df = pd.DataFrame(books)
        df.drop_duplicates(subset="Title", inplace=True)
        logger.warn(df.to_dict('records'))
        ti.xcom_push(key='book_data', value=df.to_dict('records'))
    else:
        logger.error(f"Failed to fetch data. Status code: {response.status_code}")
        return []

# Fonction pour transformer les données
def transform_books_data(ti):
    book_data = ti.xcom_pull(key='book_data', task_ids='fetch_books_data')
    if not book_data:
        raise ValueError("No book data found")
    transformed_data = transform_data(book_data,logger)
    ti.xcom_push(key='transformed_data', value=transformed_data)

# Fonction pour charger les données transformées dans PostgreSQL
def load_data_to_postgres(ti):
    transformed_data = ti.xcom_pull(key='transformed_data', task_ids='transform_books_data')
    if not transformed_data or not isinstance(transformed_data, dict):
        raise ValueError("Transformed data is missing or not in the expected format")

    
    # Insertion des données dans les tables PostgreSQL
    postgres_conn_id = 'books_connection'
    insert_to_postgres('author_dim', pd.DataFrame(transformed_data['author_dim']), postgres_conn_id)
    insert_to_postgres('date_dim', pd.DataFrame(transformed_data['date_dim']), postgres_conn_id)
    insert_to_postgres('books', pd.DataFrame(transformed_data['books']), postgres_conn_id)
# Fonction pour vérifier si la date existe déjà
def check_date_exists(**kwargs):
    execution_date = kwargs['execution_date'].strftime('%Y%m%d')
    postgres_hook = PostgresHook(postgres_conn_id='books_connection')
    records = postgres_hook.get_first(
        sql="SELECT COUNT(*) FROM date_dim WHERE date = %s;", parameters=(execution_date,)
    )
    if records and records[0] > 0:
        logger.info(f"Date {execution_date} already exists in date_dim. Skipping further tasks.")
        return False
    logger.info(f"Date {execution_date} does not exist in date_dim. Proceeding with data load.")
    return True

# Définition du DAG
dag = DAG(
    'dag_top_best_sellers_books',
    default_args=default_args,
    description='Fetch books from API, transform, and load to PostgreSQL with date check',
    schedule_interval='@weekly',
    catchup=False,
    tags=["DEV"],
    on_failure_callback=lambda context: logger.error(f"DAG failed: {context['dag_run'].dag_id}")  # Optionnel pour log en cas d'échec
)

# Tâches du DAG
fetch_books_task = PythonOperator(
    task_id='fetch_books_data',
    python_callable=fetch_books_from_api,
    op_args=[100],
    dag=dag,
    execution_timeout=timedelta(minutes=1),  # Timeout de 1 minute
    on_failure_callback=lambda context: dag.dagrun.set_state('failed')  # Arrête le DAG si cette tâche échoue
)

create_books_table_task = PostgresOperator(
    task_id='create_books_table',
    postgres_conn_id='books_connection',
    sql='sql/create_books_table.sql',
    dag=dag
)

create_author_dim_task = PostgresOperator(
    task_id='create_author_dim_table',
    postgres_conn_id='books_connection',
    sql='sql/create_author_dim.sql',
    dag=dag
)

create_date_dim_task = PostgresOperator(
    task_id='create_date_dim_table',
    postgres_conn_id='books_connection',
    sql='sql/create_date_dim.sql',
    dag=dag
)

check_date_task = ShortCircuitOperator(
    task_id='check_date_exists',
    python_callable=check_date_exists,
    provide_context=True,
    dag=dag
)

transform_data_task = PythonOperator(
    task_id='transform_books_data',
    python_callable=transform_books_data,
    dag=dag
)

load_data_task = PythonOperator(
    task_id='load_data_to_postgres',
    python_callable=load_data_to_postgres,
    dag=dag
)

drop_books_analytics_task = PostgresOperator(
    task_id='drop_books_analytics_data',
    postgres_conn_id='books_connection',
    sql='sql/drop_existing_data.sql',
    dag=dag
)

create_books_analytics_task = PostgresOperator(
    task_id='create_books_analytics_table',
    postgres_conn_id='books_connection',
    sql='sql/create_books_analytics.sql',
    dag=dag
)

# Dépendances
fetch_books_task >> [create_author_dim_task, create_date_dim_task]
[create_author_dim_task, create_date_dim_task] >> create_books_table_task
create_books_table_task >> check_date_task
check_date_task >> transform_data_task >> load_data_task
load_data_task >> drop_books_analytics_task >> create_books_analytics_task
