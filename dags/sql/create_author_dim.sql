CREATE TABLE IF NOT EXISTS author_dim (
    author_id SERIAL PRIMARY KEY,  -- Identifiant unique pour chaque auteur
    author VARCHAR NOT NULL        -- Nom de l'auteur
);
