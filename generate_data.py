"""
generate_data.py — synthetic commit history for TestGuard training.

We simulate a small codebase with 6 modules and 14 test files.
Each synthetic "commit" records which modules changed, and which
tests broke — based on realistic module→test relationships plus
a small amount of random noise (flaky tests).
"""

import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

# The six modules in our imaginary monorepo
MODULES = ['auth', 'payments', 'users', 'notifications', 'api', 'core']

# 14 test files spread across those modules
TESTS = [
    'test_auth',    'test_login',   'test_jwt',
    'test_payments','test_checkout',
    'test_users',   'test_profile',
    'test_notifications', 'test_email',
    'test_api',     'test_routes',
    'test_core',    'test_utils',
    'test_integration',
]

# Ground-truth: if module X changes, these tests tend to fail
RELATIONS = {
    'auth':          ['test_auth', 'test_login', 'test_jwt', 'test_integration'],
    'payments':      ['test_payments', 'test_checkout', 'test_integration'],
    'users':         ['test_users', 'test_profile', 'test_integration'],
    'notifications': ['test_notifications', 'test_email'],
    'api':           ['test_api', 'test_routes', 'test_integration'],
    'core':          ['test_core', 'test_utils', 'test_integration'],
}


def make_dataset(n=700):
    """Return a DataFrame with n synthetic commit records."""
    rows = []
    for _ in range(n):
        changed   = random.sample(MODULES, random.randint(1, 3))
        num_files = random.randint(1, 25)
        pr_size   = random.choice([0, 1, 2])   # 0=small, 1=medium, 2=large

        failed = set()
        for m in changed:
            for t in RELATIONS[m]:
                if random.random() < 0.82:          # 82% — related test breaks
                    failed.add(t)
        for t in TESTS:
            if t not in failed and random.random() < 0.05:   # 5% flaky noise
                failed.add(t)

        row = {m: int(m in changed) for m in MODULES}
        row['num_files'] = num_files
        row['pr_size']   = pr_size
        for t in TESTS:
            row[t] = int(t in failed)
        rows.append(row)

    return pd.DataFrame(rows)


if __name__ == '__main__':
    df = make_dataset()
    print(f"Generated {len(df)} records, {df[TESTS].sum().sum()} total failures")
