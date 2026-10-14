#!/bin/bash
cd "$(dirname "$0")"
while pgrep -f "despesas-execucao" >/dev/null; do sleep 60; done
./v/bin/python -I desp_agg.py > desp_agg.log 2>&1
