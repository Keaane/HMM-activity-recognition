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
report/             the report (report.pdf, report.docx)
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
- **Sampling rate:** the phones log at about 100 Hz (the Samsung at 102 Hz). Everything is resampled to
  **50 Hz** on the recorded timestamps. Windows are 2 s long and overlap by 50 %.
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
| Activity | Link |
|---|---|
| Standing | _<link>_ |
| Walking | _<link>_ |
| Jumping | _<link>_ |
| Still | _<link>_ |

## Method in short
12 features per window (8 time-domain, 4 from the FFT), z-scored with training statistics. The
orientation features (mean of each axis) were tried and dropped: they describe how the phone is held,
not what the person does, and they hurt on a recording where I held it differently. Emissions are
diagonal Gaussians; training starts from the labelled windows; Baum-Welch stops when the average
log-likelihood improves by less than 1e-6. I also trained without labels (10 random starts, keep the best
likelihood, name the states afterwards): 3 of 10 starts find the four activities, the likelihood picks one
of them, and it scores the same as the labelled start on every check.

## Results
Window-level results on recordings never used for training or for choosing features
(95 % Wilson intervals are in the notebook):

| Set | Files | Windows | Accuracy |
|---|---|---|---|
| Test A (friend, school) | 12 | 84 | 1.00 |
| Test B (friends, home, other phones) | 4 | 23 | 1.00 |
| Session held out of training | 1 | 52 | 0.94 |

Sensitivity and specificity are 1.00 for every activity on both test sets. The session check has three
still windows decoded as standing, right where a tap on the table shows up in the signal. Adding as
little as 0.002 g of noise to the test signals breaks the still class completely.
