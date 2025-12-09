#!/bin/sh

echo "⏳ Aguardando o banco subir..."

python3 <<EOF
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

echo "🚀 Iniciando servidor Flask..."
flask run --host=0.0.0.0
