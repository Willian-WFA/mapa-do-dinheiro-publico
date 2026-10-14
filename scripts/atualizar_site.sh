#!/bin/bash
# Regera dados do site a partir do que ja foi coletado e republica em /media/hitsuzen/Novo volume/money/site
cd "$(dirname "$0")"
python3 -I subnational_agg.py > /dev/null 2>&1
python3 -I compare_data.py > /dev/null 2>&1
python3 -I export_data.py > /dev/null 2>&1
python3 -I entenda_esfera.py > /dev/null 2>&1
DEST="/media/hitsuzen/Novo volume/money/site"
mkdir -p "$DEST"
cp site/*.html site/*.js site/*.css "$DEST/" 2>/dev/null
cd "/media/hitsuzen/Novo volume/money" && rm -f site.zip && python3 -c "
import zipfile,os
z=zipfile.ZipFile('site.zip','w',zipfile.ZIP_DEFLATED)
for root,_,fs in os.walk('site'):
    for f in fs:
        p=os.path.join(root,f); z.write(p,os.path.relpath(p,'site'))
z.close()"
echo "site atualizado $(date)"
