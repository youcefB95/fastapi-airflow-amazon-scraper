import pandas as pd

def transform_data(json_data, logger):
    # Charger les données en DataFrame
    df = pd.DataFrame(json_data)

    # Nettoyage des valeurs dans la colonne 'Price' (ou autres colonnes similaires)
    if 'Price' in df.columns:
        df['Price'] = df['Price'].astype(str).str.replace('..', '.', regex=False)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')  # Convertir en numérique, NaN si conversion impossible
    
    # Transformation pour la table author_dim
    author_dim = df[['Author']].drop_duplicates().reset_index(drop=True)
    author_dim['author_id'] = author_dim.index + 1

    # Transformation pour la table date_dim
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Gérer les dates invalides
    date_dim = df[['Date']].drop_duplicates().reset_index(drop=True)
    date_dim['date_id'] = date_dim.index + 1
    date_dim['year'] = date_dim['Date'].dt.year
    date_dim['month'] = date_dim['Date'].dt.month
    date_dim['day'] = date_dim['Date'].dt.day

    # Conversion des dates en chaînes JSON-compatibles
    date_dim['Date'] = date_dim['Date'].dt.strftime('%Y-%m-%d')
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d') 

    # Transformation pour la table books
    books = df.merge(author_dim, how='left', left_on='Author', right_on='Author') \
              .merge(date_dim, how='left', left_on='Date', right_on='Date')

    books = books[['author_id', 'date_id', 'Price', 'Rating', 'Title', 'Image']].copy()
    books.rename(columns={
        'Price': 'price',
        'Rating': 'rating',
        'Title': 'title',
        'Image': 'image'
    }, inplace=True)
    books['book_id'] = books.index + 1

    # Préparation des tables
    tables = ["author_dim", "date_dim", "books"]
    datas = [df.to_dict(orient='records') for df in [author_dim, date_dim, books]]
    
    return {k: v for k, v in zip(tables, datas)}
