#!/bin/bash
cd "$(dirname "$0")"
while pgrep -f "siconfi_dca.py 2022" >/dev/null; do sleep 20; done
python3 -I siconfi_dca.py 2023,2021,2024,2019,2017,2015,2020,2018,2016,2014,2013 > siconfi_rest.log 2>&1
