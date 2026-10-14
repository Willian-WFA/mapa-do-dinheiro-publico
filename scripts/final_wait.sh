#!/bin/bash
cd "$(dirname "$0")"
n=0
while [ $n -lt 2 ]; do
  if pgrep -f "baixar_portal.py militares" >/dev/null; then n=0; else n=$((n+1)); fi
  sleep 40
done
./v/bin/python -I mil_agg.py > mil_agg2.log 2>&1
./v/bin/python -I add_sheets.py > add_sheets2.log 2>&1
