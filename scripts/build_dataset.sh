#!/usr/bin/env bash
# Rebuilds data/train, data/test and data/manifest.csv from the raw Sensor Logger exports.
# The raw exports are not in the repo; put them in ./raw (or set RAW=...) and run from the repo root:
#   bash scripts/build_dataset.sh
set -euo pipefail
RAW=${RAW:-raw}
P="python scripts/prepare_sensor_logger.py"
rm -f data/train/*.csv data/test/*.csv data/manifest.csv

# ---- training: iPhone 11 Pro, 8 s files (2 s trimmed at the start, 3 s at the end) ----
$P standing "$RAW/waist_level_-2026-10-26_11-33-31.zip" --out data/train --group train
$P walking  "$RAW/Walking-2026-10-26_11-24-57.zip"      --out data/train --group train
$P still    "$RAW/still_flat_surface_-2026-10-26_11-29-17.zip" --out data/train --group train
$P jumping  "$RAW/jumping_1-2026-10-26_11-13-05.zip" "$RAW/jumping_2-2026-10-26_11-14-55.zip" \
            "$RAW/junping_3-2026-10-26_11-16-24.zip" "$RAW/jumping_4-2026-10-26_11-18-33.zip" \
            "$RAW/jumping_5-2026-10-26_11-11-19.zip" --out data/train --group train
# one multi-activity session; times are seconds from the start, the gaps (picking the phone up) stay unlabelled
$P session "$RAW/session_iphone11pro" --out data/train --group train \
   --segments "still:1-15.5,standing:22-35.5,walking:38.5-56.5,jumping:57.5-71"

# ---- test A: iPhone 11, same day as training; 3 files (24 s) per activity from the middle ----
$P standing "$RAW/standing_iphone11"                  --out data/test --max-chunks 3 --group A
$P walking  "$RAW/Walking-2026-10-26_11-21-52_2.zip" --out data/test --max-chunks 3 --group A
# the first 27 s of this recording overlap training jumping_2 (two phones recorded together), so they are skipped
$P jumping  "$RAW/Jump-2026-10-26_11-14-55.zip"      --out data/test --max-chunks 3 --trim-start 27 --group A
$P still    "$RAW/still_iphone11"                    --out data/test --max-chunks 3 --group A

# ---- test B: next day, other phones (iPhone 16 Pro, Samsung SM-A235F); each short recording is one file ----
$P standing "$RAW/Standing15-2026-10-27_11-57-36.zip" --out data/test --whole --trim-start 2   --trim-end 1   --group B
$P walking  "$RAW/Walking7-2026-10-27_12-07-47.zip"   --out data/test --whole --trim-start 1   --trim-end 1   --group B
$P jumping  "$RAW/2026-10-27_11-24-17.zip"            --out data/test --whole --trim-start 0.5 --trim-end 0.5 --group B
$P still    "$RAW/2026-10-27_11-41-31.zip"            --out data/test --whole --trim-start 1   --trim-end 1   --group B
