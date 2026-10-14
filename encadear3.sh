#!/bin/bash
# beneficiarios de programas sociais (so dezembro de cada ano) - roda quando o download de despesas 2020-2026 terminar
cd "$(dirname "$0")"
while pgrep -f "despesas-execucao" >/dev/null; do sleep 60; done
P="python3 -I baixar_portal_v2.py portal"
L=dados_portal/log_beneficiarios.txt
$P --conjuntos bpc --de 2019-01 --ate 2026-08 --meses 12 >> $L 2>&1
$P --conjuntos bolsa-familia-pagamentos --de 2016-01 --ate 2020-12 --meses 12 >> $L 2>&1
$P --conjuntos bolsa-familia-pagamentos --de 2021-11 --ate 2021-11 >> $L 2>&1
$P --conjuntos auxilio-brasil --de 2021-12 --ate 2022-12 --meses 12 >> $L 2>&1
$P --conjuntos novo-bolsa-familia --de 2023-12 --ate 2025-12 --meses 12 >> $L 2>&1
$P --conjuntos auxilio-emergencial --de 2020-12 --ate 2020-12 >> $L 2>&1
