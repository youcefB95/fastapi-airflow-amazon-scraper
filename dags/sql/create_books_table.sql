CREATE TABLE IF NOT EXISTS books (
    book_id SERIAL PRIMARY KEY,
    author_id BIGINT REFERENCES author_dim(author_id),
    date_id BIGINT REFERENCES date_dim(date_id),
    price NUMERIC,
    rating VARCHAR,
    title VARCHAR,
    image VARCHAR
);
