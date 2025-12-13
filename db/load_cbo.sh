#!/bin/sh
set -e

echo "🔌 Aguardando Postgres ficar pronto..."
until pg_isready -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; do
  sleep 1
done

echo "✅ Postgres pronto. Garantindo tabela..."
psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS public.table_cbo (
  codigo TEXT PRIMARY KEY,
  titulo TEXT NOT NULL
);
SQL

echo "🔎 Verificando se já tem dados..."
COUNT=$(psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM public.table_cbo;")
COUNT=$(echo "$COUNT" | tr -d '[:space:]')

if [ "$COUNT" = "0" ]; then
  echo "🧹 Normalizando CSV (removendo \\r) para /data/cbo2002-ocupacao.clean.csv ..."
  tr -d '\r' < /src/cbo2002-ocupacao.csv > /data/cbo2002-ocupacao.clean.csv

  echo "📥 Tabela vazia. Carregando CSV limpo..."
  psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c "
    TRUNCATE public.table_cbo;
    COPY public.table_cbo (codigo, titulo)
    FROM '/data/cbo2002-ocupacao.clean.csv'
    WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'WIN1252');
  "

  echo "✅ Carga concluída."
else
  echo "✅ Já existem $COUNT registros. Pulando carga."
fi
