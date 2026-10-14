#!/bin/bash
cd "$(dirname "$0")"
while pgrep -f encadear3.sh >/dev/null; do sleep 60; done
./v/bin/python -I ben_agg.py > ben_agg.log 2>&1
./v/bin/python -I add_areas.py >> ben_agg.log 2>&1
