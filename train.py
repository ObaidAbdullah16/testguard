"""
train.py — train and save the TestGuard model.

Algorithm: MultiOutputClassifier wrapping a RandomForestClassifier.
- One RandomForest per test file (14 total), trained simultaneously.
- Input:  8 features (6 module flags + num_files + pr_size)
- Output: 14 binary labels (run test / skip test)

Run: python train.py
"""

import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import hamming_loss

from generate_data import make_dataset, MODULES, TESTS


def train():
    print("Generating training data...")
    df = make_dataset(700)

    X = df[MODULES + ['num_files', 'pr_size']].values
    y = df[TESTS].values

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    # MultiOutputClassifier trains one classifier per label column
    clf = MultiOutputClassifier(
        RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    )
    clf.fit(X_tr, y_tr)

    # Hamming score = 1 - hamming_loss (fraction of labels predicted correctly)
    acc = (1 - hamming_loss(y_te, clf.predict(X_te))) * 100
    print(f"Model accuracy: {acc:.1f}%  (Hamming Score)")

    os.makedirs('model', exist_ok=True)
    with open('model/testguard.pkl', 'wb') as f:
        pickle.dump(clf, f)
    print("Saved -> model/testguard.pkl")
    return clf


if __name__ == '__main__':
    train()
