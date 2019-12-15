SELECT 'CREATE DATABASE kaggle'
WHERE NOT EXISTS (
    SELECT
FROM pg_database
WHERE datname = 'kaggle')
\gexec