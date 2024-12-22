CREATE TABLE books_analytics AS
SELECT 
    b.book_id,
    b.title,
    b.price,
    b.rating,
    b.image,
    a.author AS author_name,
    d.date AS publication_date,
    d.year AS publication_year,
    d.month AS publication_month
FROM 
    books b
LEFT JOIN 
    author_dim a ON b.author_id = a.author_id
LEFT JOIN 
    date_dim d ON b.date_id = d.date_id;
