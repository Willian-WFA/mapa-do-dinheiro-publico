#!/bin/bash
cd "$(dirname "$0")"
while pgrep -f "siconfi_dca.py 2022" >/dev/null; do sleep 20; done
python3 -I siconfi_dca.py 2024,2019,2016,2013,2023,2021,2020,2018,2017,2015,2014 > siconfi_rest.log 2>&1
