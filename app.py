"""
app.py — Flask web server for TestGuard.

Routes:
  GET  /          → serve the UI
  POST /predict   → run the model, return JSON results

The model trains itself automatically on first run if
model/testguard.pkl does not exist yet.
"""

import os
import pickle
import numpy as np
from flask import Flask, render_template, request, jsonify

from generate_data import MODULES, TESTS

# ── Auto-train if model is missing ──────────────────────────────────────────
if not os.path.exists('model/testguard.pkl'):
    from train import train
    train()

with open('model/testguard.pkl', 'rb') as f:
    clf = pickle.load(f)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', modules=MODULES, total=len(TESTS))


@app.route('/predict', methods=['POST'])
def predict():
    body    = request.json
    changed = body.get('modules', [])
    n_files = int(body.get('num_files', 5))
    pr_size = int(body.get('pr_size', 1))

    if not changed:
        return jsonify({'error': 'Select at least one module'}), 400

    # 8-feature vector: 6 module flags + num_files + pr_size
    x = np.array(
        [1 if m in changed else 0 for m in MODULES] + [n_files, pr_size]
    ).reshape(1, -1)

    preds = clf.predict(x)[0]          # array of 0/1, one per test
    probs = clf.predict_proba(x)       # list of (1, 2) arrays, one per test

    results = []
    for i, test in enumerate(TESTS):
        # probs[i] shape: (1, n_classes) — take probability of class 1 (fail)
        risk = float(probs[i][0][1]) if probs[i][0].shape[0] > 1 else float(preds[i])
        results.append({'test': test, 'run': bool(preds[i]), 'risk': round(risk * 100, 1)})

    results.sort(key=lambda r: r['risk'], reverse=True)
    to_run  = [r for r in results if r['run']]
    to_skip = [r for r in results if not r['run']]

    return jsonify({
        'run':  to_run,
        'skip': to_skip,
        'stats': {
            'total':     len(TESTS),
            'to_run':    len(to_run),
            'skipped':   len(to_skip),
            'saved_pct': round(len(to_skip) / len(TESTS) * 100)
        }
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
