import psycopg2
import requests
import json

conn = psycopg2.connect(
    host="db",
    database="CBO",
    user="postgres",
    password="postgres"
)

cur = conn.cursor()
cur.execute("SELECT codigo, titulo FROM table_cbo")
rows = cur.fetchall()

solr_url = "http://solr:8983/solr/cbo/update?commit=true"

docs = []
for codigo, titulo in rows:
    docs.append({
        "codigo": codigo,
        "titulo": titulo,
    })

headers = {"Content-Type": "application/json"}
requests.post(solr_url, data=json.dumps(docs), headers=headers)

print("Dados enviados ao Solr com sucesso!")
