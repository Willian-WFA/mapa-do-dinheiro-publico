#!/bin/bash
# roda depois do encadear.sh (um processo por vez no portal)
cd "$(dirname "$0")"
while pgrep -f encadear.sh >/dev/null; do sleep 120; done
python3 -I baixar_portal_v2.py externos --fontes judiciario,rmd,cvm --de 2016 --ate 2026 >> dados_portal/log_externos2.txt 2>&1
