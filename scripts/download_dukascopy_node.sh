#!/bin/bash
# Unduh M1 bid+ask via dukascopy-node, SEKUENSIAL PENUH (bukan paralel).
#
# CATATAN JUJUR: dua percobaan paralel (10 stream lalu 5 stream) sama-sama
# bermasalah -- 429 dari rate-limit Dukascopy, DAN subshell yang tidak
# ter-wait dengan benar (kemungkinan interaksi job-control non-interaktif
# bash + nohup + subshell bertingkat -- akar penyebab pasti tidak
# dikonfirmasi, tidak sepadan didebug lebih jauh). Sekuensial jauh lebih
# lambat per-instrumen tapi 100% dapat diprediksi. Estimasi: ~9 menit per
# sisi (bid/ask) x 2 sisi x 5 instrumen = ~90 menit total -- masih jauh di
# bawah target 4-6 jam.
set -uo pipefail

. /opt/nvm/nvm.sh

FROM="2012-01-01"
TO="now"
OUT=/workspace/data/raw_node/csv
LOG=/workspace/logs
mkdir -p "$OUT" "$LOG"
DONE_FILE="$LOG/download_dukascopy_node.DONE"
rm -f "$DONE_FILE"

INSTRUMENTS=(xauusd xagusd eurusd usdjpy lightcmdusd)

for inst in "${INSTRUMENTS[@]}"; do
  for side in bid ask; do
    echo "=== $(date +%H:%M:%S) starting $inst $side ==="
    dukascopy-node -i "$inst" -from "$FROM" -to "$TO" -t m1 -p "$side" -f csv \
      -dir "$OUT" -fn "${inst}_${side}" -r 20 -rp 8000 -bs 5 -bp 3000 \
      > "$LOG/node_${inst}_${side}.log" 2>&1
    code=$?
    echo "EXIT_CODE=$code for ${inst}_${side}" >> "$LOG/node_${inst}_${side}.log"
    f="$OUT/${inst}_${side}.csv"
    if [ -f "$f" ]; then
      echo "=== $(date +%H:%M:%S) done $inst $side: exit=$code, $(wc -l < "$f") lines, $(du -h "$f" | cut -f1) ==="
    else
      echo "=== $(date +%H:%M:%S) done $inst $side: exit=$code, FILE MISSING ==="
    fi
  done
done

echo "ALL_DONE_SEQUENTIAL"
touch "$DONE_FILE"
