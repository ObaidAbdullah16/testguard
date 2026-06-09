# TestGuard — ML-Powered CI Test Selector

> Stop running all 14 tests on every PR. Let a trained model decide which ones actually need to run.

## The Problem

In any growing codebase, running the entire test suite on every pull request wastes CI time and developer attention. A change to the `auth` module should never have to run `test_payments` or `test_notifications`.

TestGuard solves this by learning from **historical commit patterns** — if changing `auth + core` together has historically broken `test_integration`, the model will flag it next time.

## How It Works

```
PR Opened
   ↓
Changed Modules: [auth, payments]
   ↓
ML Model (Random Forest, trained on 700 commits)
   ↓
Run:  [test_auth, test_jwt, test_payments, test_checkout, test_integration]
Skip: [test_users, test_profile, test_notifications, test_email, ...]
   ↓
CI saves ~60% time
```

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| ML Model    | scikit-learn — MultiOutput Random Forest |
| Backend     | Flask (Python)                    |
| Frontend    | HTML / CSS / JavaScript           |
| Container   | Docker + Docker Compose           |
| CI/CD       | GitHub Actions                    |
| Hosting     | AWS EC2                           |

## ML Explainability

- **Algorithm**: `MultiOutputClassifier(RandomForestClassifier)`
- **Features**: 6 module flags (0/1) + number of files changed + PR size category
- **Labels**: 14 binary outputs — one per test file (will it fail? yes/no)
- **Training data**: 700 synthetic commit records with realistic module→test relationships
- **Accuracy**: ~91% Hamming Score (measured on 20% held-out test split)

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model (auto-runs on first app start too)
python train.py

# 3. Start the app
python app.py
# → Open http://localhost:5000
```

## Docker

```bash
docker-compose up --build
# → Open http://localhost:5000
```

## Running Tests

```bash
pytest test_app.py -v
```

## Project Structure

```
testguard/
├── generate_data.py      # Synthetic training data
├── train.py              # Model training script
├── app.py                # Flask routes
├── test_app.py           # Pytest tests
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/ci.yml  # GitHub Actions pipeline
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── main.js
```
