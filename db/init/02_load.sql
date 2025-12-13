TRUNCATE TABLE public.table_cbo;

COPY public.table_cbo (codigo, titulo)
FROM '/docker-entrypoint-initdb.d/cbo2002-ocupacao.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'WIN1252');
