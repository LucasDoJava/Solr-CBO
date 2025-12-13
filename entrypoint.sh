#!/bin/sh
set -e

echo "⏳ Aguardando o banco subir..."

python3 - <<'EOF'
import socket, time
while True:
    try:
        s = socket.create_connection(("db", 5432), timeout=1)
        s.close()
        break
    except OSError:
        time.sleep(1)
EOF

echo "🔄 Rodando migrações..."
flask db upgrade || echo "⚠️ Migrações já aplicadas ou erro não crítico."

echo "⏳ Aguardando o Solr subir..."
python3 - <<'EOF'
import time, requests
url = "http://solr:8983/solr/admin/info/system?wt=json"
while True:
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            break
    except Exception:
        pass
    time.sleep(1)
EOF

echo "⏳ Aguardando o core 'cbo' ficar pronto..."
python3 - <<'EOF'
import time, requests

cores_url = "http://solr:8983/solr/admin/cores?action=STATUS&core=cbo&wt=json"
ping_url  = "http://solr:8983/solr/cbo/admin/ping?wt=json"

while True:
    try:
        r = requests.get(cores_url, timeout=2)
        if r.status_code != 200:
            time.sleep(1)
            continue

        data = r.json()

        # Se existir initFailures para cbo, o core está quebrado (schema/config)
        if "initFailures" in data and data["initFailures"].get("cbo"):
            print("❌ Core 'cbo' com initFailures:", data["initFailures"]["cbo"])
            time.sleep(2)
            continue

        status = (data.get("status") or {}).get("cbo")
        if not status:
            time.sleep(1)
            continue

        # Agora confirma que o core está "respondendo" de verdade
        p = requests.get(ping_url, timeout=2)
        if p.status_code == 200:
            print("✔️ Solr/core pronto!")
            break

    except Exception:
        pass

    time.sleep(1)
EOF

echo "🔎 Indexando no Solr (se necessário)..."

# Retry da indexação (pega 503 "loading" ou outros timings)
python3 - <<'EOF'
import time, subprocess

max_tries = 20
sleep_s = 2

for attempt in range(1, max_tries + 1):
    print(f"📌 Tentativa {attempt}/{max_tries} de indexar...")
    code = subprocess.call(["python3", "load_solr.py"])
    if code == 0:
        print("✅ Indexação OK!")
        raise SystemExit(0)

    print(f"⚠️ Falhou (exit code {code}). Aguardando {sleep_s}s e tentando de novo...")
    time.sleep(sleep_s)

print("❌ Indexação falhou após várias tentativas.")
raise SystemExit(1)
EOF

echo "🚀 Iniciando servidor Flask..."
exec flask run --host=0.0.0.0
