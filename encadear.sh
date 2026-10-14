#!/bin/bash
# espera o download dos militares terminar e entao roda o restante, um processo por vez
cd "$(dirname "$0")"
while pgrep -f "baixar_portal.py militares" >/dev/null; do sleep 120; done
python3 -I baixar_portal.py militares --de 2016-01 --ate 2026-08 --saida dados_portal >> dados_portal/log_militares.txt 2>&1   # completa se faltou algo
python3 -I baixar_portal_v2.py portal --conjuntos todos --de 2016-01 --ate 2026-12 >> dados_portal/log_portal_todos.txt 2>&1
python3 -I baixar_portal_v2.py externos --fontes tesouro,camara,senado --de 2016 --ate 2026 >> dados_portal/log_externos.txt 2>&1
