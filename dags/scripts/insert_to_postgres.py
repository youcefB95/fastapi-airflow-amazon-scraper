from airflow.providers.postgres.hooks.postgres import PostgresHook

def insert_to_postgres(table_name, dataframe, postgres_conn_id):
    """
    Insère des données dans une table PostgreSQL en utilisant PostgresHook.

    :param table_name: Nom de la table cible.
    :param dataframe: Pandas DataFrame contenant les données à insérer.
    :param postgres_conn_id: Connexion Airflow à PostgreSQL.
    """
    # Obtenir le hook PostgreSQL
    postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtenir une connexion
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    # Insertion des données
    for _, row in dataframe.iterrows():
        cols = ', '.join(row.index)
        placeholders = ', '.join(['%s'] * len(row))  # Utilisation de placeholders SQL
        query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        values = tuple(row.values)
        cursor.execute(query, values)

    conn.commit()
    cursor.close()
