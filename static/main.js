// Track which modules the user has toggled on
const selectedModules = new Set();

function toggleModule(btn) {
  const mod = btn.dataset.module;
  if (selectedModules.has(mod)) {
    selectedModules.delete(mod);
    btn.classList.remove('active');
  } else {
    selectedModules.add(mod);
    btn.classList.add('active');
  }
}

async function predict() {
  if (selectedModules.size === 0) {
    // Shake the module grid as a hint
    const grid = document.getElementById('module-grid');
    grid.style.animation = 'none';
    grid.offsetHeight; // reflow
    grid.style.animation = 'shake .4s ease';
    return;
  }

  const btn     = document.getElementById('predict-btn');
  const btnText = document.getElementById('btn-text');
  const spinner = document.getElementById('btn-spinner');

  btn.disabled = true;
  btnText.textContent = 'Analysing…';
  spinner.classList.remove('hidden');

  const prSize  = document.querySelector('input[name="pr_size"]:checked').value;
  const numFiles = document.getElementById('num-files').value;

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        modules:   [...selectedModules],
        pr_size:   parseInt(prSize),
        num_files: parseInt(numFiles),
      }),
    });

    const data = await res.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    renderResults(data);
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Run Prediction';
    spinner.classList.add('hidden');
  }
}

function renderResults(data) {
  // Hide empty state, show results
  document.getElementById('empty-state').classList.add('hidden');
  const resultsEl = document.getElementById('results');
  resultsEl.classList.remove('hidden');

  // Stats row
  document.getElementById('stats-row').innerHTML = `
    <div class="stat-card stat-run">
      <div class="stat-value">${data.stats.to_run}</div>
      <div class="stat-label">Tests to Run</div>
    </div>
    <div class="stat-card stat-skip">
      <div class="stat-value">${data.stats.skipped}</div>
      <div class="stat-label">Tests Skipped</div>
    </div>
    <div class="stat-card stat-save">
      <div class="stat-value">${data.stats.saved_pct}%</div>
      <div class="stat-label">CI Time Saved</div>
    </div>
  `;

  // Must-run list
  const runEl = document.getElementById('run-list');
  runEl.innerHTML = data.run.length
    ? data.run.map((t, i) => `
        <div class="test-card run-card" style="animation-delay:${i * 40}ms">
          <span>${t.test}.py</span>
          <span class="risk-badge risk-high">${t.risk}% risk</span>
        </div>
      `).join('')
    : '<p style="color:var(--muted);font-size:.82rem;padding:.5rem">No tests at risk 🎉</p>';

  // Safe-to-skip list
  const skipEl = document.getElementById('skip-list');
  skipEl.innerHTML = data.skip.length
    ? data.skip.map((t, i) => `
        <div class="test-card skip-card" style="animation-delay:${i * 30}ms">
          <span>${t.test}.py</span>
          <span class="risk-badge risk-low">${t.risk}% risk</span>
        </div>
      `).join('')
    : '<p style="color:var(--muted);font-size:.82rem;padding:.5rem">All tests are flagged</p>';
}

// Add shake animation dynamically
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%,100% { transform: translateX(0); }
    20%,60% { transform: translateX(-6px); }
    40%,80% { transform: translateX(6px); }
  }
`;
document.head.appendChild(style);
