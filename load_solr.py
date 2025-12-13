import psycopg2
import requests
import time

PG = dict(host="db", database="CBO", user="postgres", password="postgres")
CORE = "cbo"
SOLR_BASE = f"http://solr:8983/solr/{CORE}"

PING_URL = f"{SOLR_BASE}/admin/ping?wt=json"
COUNT_URL = f"{SOLR_BASE}/select?q=*:*&rows=0&wt=json"
UPDATE_URL = f"{SOLR_BASE}/update/json/docs?commit=true"

def wait_solr_ready(retries=60, delay=1):
    for i in range(retries):
        try:
            r = requests.get(PING_URL, timeout=2)
            if r.status_code == 200:
                print("✔️ Solr/core pronto!")
                return True
        except Exception:
            pass
        print(f"⏳ Aguardando Solr/core... ({i+1}/{retries})")
        time.sleep(delay)
    return False

def solr_count():
    r = requests.get(COUNT_URL, timeout=5)
    r.raise_for_status()
    return r.json()["response"]["numFound"]

def post_with_retry(docs, retries=60, delay=1):
    last = None
    for i in range(retries):
        try:
            resp = requests.post(UPDATE_URL, json=docs, timeout=30)
            if resp.status_code == 503 and "SolrCore is loading" in resp.text:
                print(f"⏳ SolrCore carregando... retry ({i+1}/{retries})")
                time.sleep(delay)
                last = resp
                continue
            return resp
        except Exception as e:
            print(f"⚠️ Erro ao enviar (tentativa {i+1}/{retries}): {e}")
            time.sleep(delay)
    return last

def main():
    if not wait_solr_ready():
        print("❌ Solr não ficou pronto a tempo. Abortando indexação.")
        return

    # Idempotência: se já tem docs, não reindexa
    try:
        count = solr_count()
        print(f"📦 Solr já tem {count} docs.")
        if count > 0:
            print("✅ Indexação já feita. Nada a fazer.")
            return
    except Exception as e:
        print(f"⚠️ Não consegui consultar contagem do Solr: {e} (vou tentar indexar mesmo)")

    print("🔌 Conectando ao Postgres...")
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    cur.execute("SELECT codigo, titulo FROM table_cbo")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"📄 Registros encontrados no Postgres: {len(rows)}")
    if not rows:
        print("⚠️ Nenhum dado encontrado no Postgres. Abortando.")
        return

    docs = [{"id": c, "CODIGO": c, "TITULO": t} for c, t in rows]
    print(f"📤 Enviando {len(docs)} documentos para o Solr...")

    resp = post_with_retry(docs)
    if resp is None:
        raise RuntimeError("Falha total ao enviar para o Solr.")

    print("📡 Status HTTP do Solr:", resp.status_code)
    print("📡 Resposta do Solr:", resp.text)
    resp.raise_for_status()
    print("✅ Dados enviados ao Solr com sucesso!")

if __name__ == "__main__":
    main()
