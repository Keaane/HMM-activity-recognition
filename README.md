# Activity recognition from phone motion with a Hidden Markov Model


I recorded my phone's accelerometer and gyroscope while standing, walking, jumping and leaving it
still, and built a Gaussian HMM from scratch in NumPy (no HMM library) that guesses the activity.
Baum-Welch trains it, Viterbi decodes it.

## Layout
```
data/train/         56 labelled CSVs (<activity>_r<recording>_<nn>.csv, plus session_01.csv)
data/test/          16 CSVs the model never saw (test A: 12 files, test B: 4 files)
data/manifest.csv   for every file: source recording, phone, date, time span, group
notebooks/          hmm_activity_recognition.ipynb   <- the whole analysis
scripts/            prepare_sensor_logger.py, build_dataset.sh (raw exports -> data/)
figures/            figures used in the report
report/             report.docx (the written report), report_outline.md
```

## Run it
```bash
pip install -r requirements.txt
jupyter notebook notebooks/hmm_activity_recognition.ipynb     # Run All
```
The raw Sensor Logger exports are not in the repo. `scripts/build_dataset.sh` shows exactly how the
CSVs in `data/` were made from them.

## The data
- **App and sensors:** Sensor Logger (iOS and Android). Accelerometer including gravity, and gyroscope.
- **Sampling rate:** measured from the timestamps (median interval) of every file:

  | Phone | Recorded by | Used for | Native rate |
  |---|---|---|---|
  | iPhone 11 Pro | me | training | 99.8 Hz |
  | iPhone 11 | friend, at school | test A | 100.1 Hz |
  | iPhone 16 Pro | friend, at home | test B (jumping, still) | 99.6 Hz |
  | Samsung SM-A235F | friend, at home | test B (standing, walking) | 102.1 Hz |

  Everything is resampled to **50 Hz** on the recorded timestamps, so every phone ends up on the same grid.
  Walking repeats at about 1.5 Hz and jumping at about 2 Hz, so 50 Hz keeps everything up to 25 Hz with
  plenty of room; the notebook shows the model still gets every test window right at 10 Hz.
  Windows are 2 s long (100 samples) and overlap by 50 %.
- **Training (iPhone 11 Pro):** long continuous recordings (standing 128 s, walking 122 s, still 122 s,
  five jumping takes of 23 to 39 s), trimmed at both ends and cut into 8 s files, plus one 72 s
  recording that goes still, standing, walking, jumping. In that one the moments where I pick the phone up
  or switch activity are left unlabelled and ignored. Every activity has at least 90 s of data.
- **Test A (a friend's iPhone 11, at school, same day as training):** three 8 s files per activity, taken
  from the middle of separate recordings. The first 27 s of the jumping recording are left out as a precaution:
  it was recorded at the same moment as my training file `jumping_2`.
- **Test B (next day, at home, friends' phones):** iPhone 16 Pro (jumping, still) and Samsung SM-A235F
  (standing, walking). Each short recording is one file. Android logs m/s2 with the opposite sign to
  iPhones, so its accelerometer values are divided by -9.81 to match.
- **Recorded by:** training by me. The test files come from three other people: one friend at school (test A, iPhone 11),
  and two other friends at home (test B, iPhone 16 Pro and Samsung SM-A235F).

### Videos
About 5 s each, recording every activity with the phone in hand (on the table for still). All four are
also in [one Drive folder](https://drive.google.com/drive/folders/1qP9lk4-jdwW2zVzHJfrS-97dwyjKSSTp?usp=sharing).

| Activity | Link |
|---|---|
| Standing | [Standing.MOV](https://drive.google.com/file/d/1JI3AfJLWRhbkHDnTqDMrxgdqgElyL5Xa/view?usp=sharing) |
| Walking | [Walking.MOV](https://drive.google.com/file/d/1hlyufCnN7I3ro7HPdFge_5pGlwM0QypA/view?usp=sharing) |
| Jumping | [Jumping.MOV](https://drive.google.com/file/d/1vLb4cIrxcw4DSrRRj534_pwlhCI7Anm7/view?usp=sharing) |
| Still | [Still.MOV](https://drive.google.com/file/d/1k-YQIuRrEuhhP4bo9Cw2g9SsSArijBaa/view?usp=sharing) |

## Method in short
12 features per window (8 time-domain, 4 from the FFT), z-scored with training statistics. The
orientation features (mean of each axis) were tried and dropped: they describe how the phone is held,
not what the person does, and they hurt on a recording where I held it differently. Emissions are
diagonal Gaussians; training starts from the labelled windows; Baum-Welch stops when the average
log-likelihood improves by less than 1e-6. I also trained without labels (10 random starts, keep the best
likelihood, name the states afterwards): 3 of 10 starts find the four activities, the likelihood picks one
of them, and it scores the same as the labelled start on every check.

## Results
Window-level results. Test A and test B were never used for training, for the z-score statistics or for
choosing features. The session was held out of training too, but I used it to choose the features and the
variance floor, so its number is a validation score and a little optimistic. The 95 % Wilson intervals are
in the notebook.

| Set | Role | Files | Windows | Accuracy |
|---|---|---|---|---|
| Test A (friend, school) | test | 12 | 84 | 1.00 |
| Test B (friends, home, other phones) | test | 4 | 23 | 1.00 |
| Session held out of training | validation | 1 | 52 | 0.94 |

Sensitivity and specificity are 1.00 for every activity on both test sets. The session check has three
still windows decoded as standing, right where a tap on the table shows up in the signal. Scoring each
window on its own, without the transitions, gets 0.92 there, so Viterbi gets one more window right.
Adding as little as 0.002 g of noise to the test signals breaks the still class completely, and still has
only been tested on iPhones (the Samsung recordings are standing and walking), so a phone with a noisier
accelerometer is the most likely place for the model to fail.
