#!/bin/bash
# Atualiza o site sempre que um novo ano da coleta SICONFI ficar completo
cd "$(dirname "$0")"
last=""
while true; do
  cur=$(python3 -I - <<'E'
import json,collections
c=collections.defaultdict(lambda:collections.Counter())
try:
    for l in open('siconfi_dca.jsonl'):
        r=json.loads(l)
        if r['n']>0 or r['n']==0 or r['n']==-1: c[r['ano']]['t']+=1
except Exception: pass
print(','.join(str(y) for y,v in sorted(c.items()) if v['t']>=5590))
E
)
  if [ "$cur" != "$last" ]; then ./atualizar_site.sh >> auto_update.log 2>&1; last="$cur"; fi
  if ! pgrep -f "siconfi_dca.py" >/dev/null && ! pgrep -f "chain_siconfi2.sh" >/dev/null; then ./atualizar_site.sh >> auto_update.log 2>&1; break; fi
  sleep 300
done
