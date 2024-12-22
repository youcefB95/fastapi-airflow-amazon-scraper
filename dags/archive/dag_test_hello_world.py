from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Fonction Python qui sera exécutée
def print_hello():
    print("Hello")

# Définition du DAG
dag = DAG(
    dag_id="hello_world_dag",              # Nom du DAG
    start_date=datetime(2023, 12, 1),     # Date de début
    schedule_interval=None,               # Pas de planification automatique
    catchup=False,                        # Ne pas rattraper les exécutions manquées
    tags=["example"]                      # Tags pour catégoriser le DAG
)

    # Définition de la tâche
hello_task = PythonOperator(
        task_id="print_hello_task",        # ID de la tâche
        python_callable=print_hello,
        dag=dag)# Fonction Python à exécuter
    

# Dépendances (dans ce cas, il n'y a qu'une seule tâche)
hello_task
