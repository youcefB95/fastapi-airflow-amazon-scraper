CREATE TABLE IF NOT EXISTS date_dim (
    date_id SERIAL PRIMARY KEY,  -- Identifiant unique pour chaque date
    date DATE NOT NULL,          -- Date complète
    year INT NOT NULL ,         -- Année (ex. 2024)
    month INT NOT NULL,          -- Mois de l'année (1-12)
    day INT NOT NULL            -- Jour (12)
);
