# Report plan (4-5 pages)

1. **Background** - one paragraph: activity recognition in trackers and smart homes, why an HMM.
2. **Data collection and cleaning** - phones, app, 100 Hz -> 50 Hz, 2 s windows, how each set was made,
   the four video links. Say plainly that the training files are 8 s pieces of longer recordings.
   Why the test set has 16 files from 8 recordings: test A is the same-day check, test B is the
   independent one (new day, two other phones, a different operating system), and short
   recordings were kept whole. Figure: sample data.
3. **Features** - the table, z-score and why. Figure: features overview.
4. **Model** - states, observations, pi, A, B; why Baum-Welch and Viterbi; labelled start vs random
   starts; stopping rule. Figures: convergence, transition + emission heatmaps.
5. **Results** - feature choice table, test A and B metrics with intervals, confusion matrices, session
   hold-out, decoded sequences. Figures: confusion_test, decoded_test (and decoded_session_holdout).
6. **Discussion** - easiest/hardest, whether transitions look like real behaviour (no: one session),
   noise and sampling rate, limits (one person per set?, small test B), what to improve.
