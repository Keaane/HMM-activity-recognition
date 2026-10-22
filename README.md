# Human Activity Recognition with a Hidden Markov Model

Formative 2: Hidden Markov Models (Machine Learning Techniques II).

I recorded my own phone's accelerometer and gyroscope data while standing, walking, jumping and staying still, then built a Hidden Markov Model from scratch (numpy) to infer which activity was happening from the sensor readings alone.

## Repository structure

```
hmm-activity-recognition/
├── data/
│   ├── train/          # labelled CSV recordings used for training (50 files)
│   └── test/           # unseen recordings, never used in training
├── notebooks/
│   └── hmm_activity_recognition.ipynb
├── figures/            # plots exported for the report (heatmap, decoded sequences, confusion matrix)
├── report/             # final 4-5 page report
├── requirements.txt
└── README.md
```

## Data

- Device and app: _fill in (e.g. phone model, Sensor Logger)_
- Sensors: accelerometer (x, y, z) and gyroscope (x, y, z), with a timestamp column
- Sampling rate: _fill in_ Hz
- Activities: standing, walking, jumping, still
- File naming: `<activity>_<number>.csv`, e.g. `walking_01.csv`
- Training set: _fill in_ files (about 12-13 per activity, 8-10 s each)
- Test set: _fill in_ files, recorded in a separate session

## Demo videos

| Activity | Video link |
|---|---|
| Standing | _add link_ |
| Walking | _add link_ |
| Jumping | _add link_ |
| Still | _add link_ |

## How to run

1. Install the requirements: `pip install -r requirements.txt`
2. Open `notebooks/hmm_activity_recognition.ipynb`
3. Run all cells from top to bottom. The notebook reads the files in `data/train/` and `data/test/`.

## Method summary

1. Load and clean the recordings and bring them to one sampling rate
2. Cut each recording into windows
3. Extract time-domain and frequency-domain features and normalise them
4. Define the HMM: hidden states (activities), observations (feature vectors), transition, emission and starting probabilities
5. Train with Baum-Welch and decode with Viterbi (both implemented in numpy)
6. Evaluate on the unseen test files (sensitivity, specificity, accuracy, confusion matrix)

## Results

_Fill in after evaluation._
