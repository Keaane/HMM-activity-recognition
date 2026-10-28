"""Turn Sensor Logger exports (zip, or a folder of csv files) into labelled CSVs for the notebook.

Single-activity recordings, cut into fixed pieces:
    python scripts/prepare_sensor_logger.py jumping raw/jump_1.zip --out data/train
  Trims --trim-start / --trim-end seconds, then cuts the rest into --chunk second files named
  <activity>_r<k>_<nn>.csv (k = which recording of that activity in --out).
  --max-chunks N keeps N pieces from the middle; --whole writes the trimmed recording as ONE file.

One multi-activity session (a label column, empty where the phone was being picked up or moved):
    python scripts/prepare_sensor_logger.py session raw/session --out data/train \
        --segments "still:1-15.5,standing:22-35.5,walking:38.5-56.5,jumping:57.5-71"

What it does to the signal:
  * uses AccelerometerUncalibrated (gravity included) and Gyroscope, matched on the accelerometer timestamps
  * Android phones log m/s2 with the opposite sign to iPhones (which log g), so Android accelerometer
    values are divided by -9.80665 to match the iPhone convention
Every file written is listed in data/manifest.csv (device, source, time span, group).
"""
import argparse
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ACTS = ["standing", "walking", "jumping", "still"]
G = 9.80665

ap = argparse.ArgumentParser()
ap.add_argument("label", choices=ACTS + ["session"])
ap.add_argument("inputs", nargs="+", help=".zip exports or folders of csv files")
ap.add_argument("--out", default="data/train")
ap.add_argument("--chunk", type=float, default=8.0, help="piece length in seconds")
ap.add_argument("--trim-start", type=float, default=2.0)
ap.add_argument("--trim-end", type=float, default=3.0)
ap.add_argument("--max-chunks", type=int, default=None, help="keep only N pieces, taken from the middle")
ap.add_argument("--whole", action="store_true", help="one file per recording instead of fixed pieces")
ap.add_argument("--group", default="", help="free-text group name stored in the manifest")
ap.add_argument("--segments", help='session mode, e.g. "still:1-15.5,standing:22-35.5"')
args = ap.parse_args()

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
MANIFEST = out.parent / "manifest.csv"


def read_sensor(src, name):
    p = Path(src)
    if p.is_dir():
        return pd.read_csv(p / f"{name}.csv")
    with zipfile.ZipFile(p) as zf:
        return pd.read_csv(zf.open(f"{name}.csv"))


def load(src):
    """Return (dataframe with time, ax..gz, seconds array, metadata dict)."""
    acc, gyr = read_sensor(src, "AccelerometerUncalibrated"), read_sensor(src, "Gyroscope")
    meta = read_sensor(src, "Metadata").iloc[0]
    t = acc["seconds_elapsed"].to_numpy()
    scale = -1 / G if str(meta["platform"]).lower() == "android" else 1.0
    df = pd.DataFrame({"time": acc["time"], "ax": acc["x"] * scale, "ay": acc["y"] * scale, "az": acc["z"] * scale})
    for c in "xyz":
        df["g" + c] = np.interp(t, gyr["seconds_elapsed"], gyr[c])
    info = dict(device=str(meta["device name"]), platform=str(meta["platform"]),
                recorded=str(meta["recording time"])[:10])
    return df, t, info


def next_recording(label):
    nums = [int(m.group(1)) for f in out.glob(f"{label}_r*_*.csv") if (m := re.match(rf"{label}_r(\d+)_", f.name))]
    return max(nums, default=0) + 1


def log(rows):
    old = pd.read_csv(MANIFEST) if MANIFEST.exists() else pd.DataFrame()
    pd.concat([old, pd.DataFrame(rows)], ignore_index=True).to_csv(MANIFEST, index=False)


def row(file, label, rec, src, info, a, b):
    return dict(split=out.name, group=args.group or out.name, file=file, label=label, recording=rec,
                source=Path(src).name, device=info["device"], platform=info["platform"],
                recorded=info["recorded"], start_s=round(a, 1), end_s=round(b, 1))


if args.label == "session":
    if not args.segments:
        ap.error("session mode needs --segments")
    segs = []
    for part in args.segments.split(","):
        name, rng = part.split(":")
        a, b = (float(x) for x in rng.split("-"))
        assert name in ACTS and a < b, f"bad segment: {part}"
        segs.append((name, a, b))
    n = len(list(out.glob("session_*.csv")))
    for src in args.inputs:
        df, t, info = load(src)
        df["label"] = ""
        for name, a, b in segs:
            df.loc[(t >= a) & (t < b), "label"] = name
        n += 1
        df.to_csv(out / f"session_{n:02d}.csv", index=False)
        log([row(f"session_{n:02d}.csv", "mixed", "session", src, info, 0.0, t[-1])])
        print(f"{Path(src).name}: {t[-1]:.1f}s -> session_{n:02d}.csv ({(df.label != '').mean() * 100:.0f}% labelled)")
else:
    for src in args.inputs:
        df, t, info = load(src)
        rec = next_recording(args.label)
        t0, t1 = t[0] + args.trim_start, t[-1] - args.trim_end
        if args.whole:
            spans = [(t0, t1)]
        else:
            n_all = int((t1 - t0) // args.chunk)
            n_keep = min(n_all, args.max_chunks) if args.max_chunks else n_all
            skip = (n_all - n_keep) // 2                    # keep the middle pieces
            spans = [(t0 + (skip + i) * args.chunk, t0 + (skip + i + 1) * args.chunk) for i in range(n_keep)]
        rows = []
        for i, (a, b) in enumerate(spans, 1):
            name = f"{args.label}_r{rec}_{i:02d}.csv"
            df[(t >= a) & (t < b)].to_csv(out / name, index=False)
            rows.append(row(name, args.label, f"r{rec}", src, info, a, b))
        log(rows)
        print(f"{Path(src).name} ({info['device']}): {t[-1]:.1f}s -> {len(spans)} file(s) {args.label}_r{rec}_*")
