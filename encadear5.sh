#!/bin/bash
cd "$(dirname "$0")"
P="python3 -I baixar_portal_v2.py portal"
L=dados_portal/log_pessoas.txt
$P --conjuntos servidores --origens Servidores_SIAPE --meses 12 --de 2013-01 --ate 2025-12 >> $L 2>&1
$P --conjuntos servidores --origens Aposentados_SIAPE,Pensionistas_SIAPE --meses 12 --de 2020-01 --ate 2025-12 >> $L 2>&1
