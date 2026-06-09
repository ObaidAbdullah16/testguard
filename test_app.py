"""
test_app.py — basic tests for TestGuard.
Run with: pytest test_app.py -v
"""

import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_home_page_loads(client):
    """Home page should return 200."""
    res = client.get('/')
    assert res.status_code == 200


def test_predict_requires_modules(client):
    """Predicting with no modules should return 400."""
    res = client.post('/predict', json={'modules': []})
    assert res.status_code == 400


def test_predict_auth_module(client):
    """Predicting auth changes should return auth-related tests in 'run'."""
    res = client.post('/predict', json={
        'modules': ['auth'], 'pr_size': 1, 'num_files': 3
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'run' in data and 'skip' in data and 'stats' in data
    run_names = [r['test'] for r in data['run']]
    # auth module change should flag auth tests
    assert any('auth' in t or 'login' in t or 'jwt' in t for t in run_names)


def test_predict_stats_sum(client):
    """run + skip counts should equal total tests."""
    res = client.post('/predict', json={
        'modules': ['payments', 'users'], 'pr_size': 2, 'num_files': 10
    })
    data = res.get_json()
    assert data['stats']['to_run'] + data['stats']['skipped'] == data['stats']['total']
