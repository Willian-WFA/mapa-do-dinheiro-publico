#!/bin/bash
# anos anteriores a 2016
cd "$(dirname "$0")"
P="python3 -I baixar_portal_v2.py portal"
L=dados_portal/log_anos_anteriores.txt
$P --conjuntos despesas-execucao --de 2014-01 --ate 2015-12 >> $L 2>&1
$P --conjuntos renuncias --de 2015-01 --ate 2015-12 >> $L 2>&1
$P --conjuntos servidores --origens Militares --meses 12 --de 2013-01 --ate 2015-12 >> $L 2>&1
$P --conjuntos bolsa-familia-pagamentos --meses 12 --de 2013-01 --ate 2015-12 >> $L 2>&1
