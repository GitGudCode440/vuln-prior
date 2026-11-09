# VulnPrior: Intelligent Vulnerability Prioritization

**CT-363 Design and Analysis of Algorithms, complex computing problem**
Department of Computer Science and Information Systems, NED University of Engineering and Technology

Organizations usually have more vulnerabilities than they can fix with the time and money available.
VulnPrior takes a list of candidate fixes and a budget, then chooses which fixes to make so the total
estimated risk reduction is as large as possible without going over the budget.

It runs two algorithms on the same data and compares them:

| Algorithm | Idea | Time | Space | Optimal? |
|---|---|---|---|---|
| **Greedy** | Sort fixes by risk reduction per unit cost, take each one that still fits | O(n log n) | O(n) | Not always |
| **Dynamic programming (0/1 knapsack)** | Build a table of the best result for every budget up to B, then trace back the chosen fixes | O(nB) | O(nB) | Always |

*n* is the number of fixes and *B* is the integer budget.

The app is built with [Streamlit](https://streamlit.io). It has a Home page that explains the idea with a live
demo, and a Prioritizer page where you load data, set a budget and compare the two methods.

---

## 1. Requirements

- **Python 3.10 or newer** (developed and tested on Python 3.12)
- An internet connection the first time, to install packages (and so the page can load its Google fonts)

Packages (listed in `requirements.txt`):

| Package | Used for |
|---|---|
| `streamlit>=1.50` | The web app and page navigation |
| `pandas>=2.0` | Reading CSV files and showing tables |
| `numpy>=1.26` | The dynamic programming table |
| `pytest>=8.0` | Running the tests |

## 2. Install

Open a terminal in the project folder (the one that contains `app.py`).

**Recommended: use a virtual environment** so the packages stay inside the project.

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS or Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If PowerShell refuses to activate the environment, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try again.

**Or install straight into your main Python:**
```bash
python -m pip install -r requirements.txt
```

Installing Streamlit on its own looks like this, and `streamlit hello` opens Streamlit's demo app to confirm it works:
```bash
pip install streamlit
streamlit hello
```

Check that everything is installed:
```bash
python -c "import numpy, pandas, streamlit; print('ok')"
```

## 3. Run the app

From the project folder:
```bash
streamlit run app.py
```
Your browser opens at `http://localhost:8501`. If it doesn't, copy that address from the terminal into your browser.
Press `Ctrl+C` in the terminal to stop the app.

If the `streamlit` command is not found, run it through Python instead:
```bash
python -m streamlit run app.py
```

> **After editing code**, stop the app with `Ctrl+C` and start it again. Streamlit can keep using an old copy of
> imported files (such as `ui.py` or anything in `core/`) until it is restarted.

## 4. Run the tests

From the project folder (not from inside `tests/`):
```bash
python -m pytest
```
The tests read files such as `data/edge_cases/empty.csv` using paths relative to the project folder, so running
them from anywhere else makes them fail. They cover validation, both algorithms, edge cases, and check the dynamic
programming result against a brute-force solver on small random inputs.

---

## 5. How to use the app

**Home page.** Explains the problem and includes a "Try it yourself" demo. Drag the budget slider and watch
where Greedy falls behind the best possible answer. Use the top navigation bar to switch pages.

**Prioritizer page.**
1. **Choose your data** in the sidebar: the built-in sample, an uploaded CSV, an edge-case file, or the synthetic generator.
2. **Set your budget** in the sidebar. A suggested value is filled in (40% of the total cost of all fixes).
3. **Read the results** in the tabs:

| Tab | What it shows |
|---|---|
| Your data | Valid records, and rejected records with the reason for each |
| Greedy | Fixes chosen by Greedy, total cost, risk reduction, budget used |
| Dynamic programming | The same for the optimal method |
| Comparison | Plain-English verdict, side-by-side numbers, optimality gap, where the picks differ, "Budget at a glance" bars, and charts for risk reduction, cost, time and memory |
| Scaling | Experiments that time both methods as *n* or the budget grows |

Results update as soon as you change the data or the budget.

## 6. CSV format

Upload a file with these six columns (names are not case-sensitive, column order does not matter, extra columns are ignored):

| Column | Meaning | Rule |
|---|---|---|
| `id` | Unique label, e.g. `V001` | Required, must be unique |
| `name` | Short description | Required |
| `severity` | How serious the weakness is | Number from 0 to 10 |
| `asset_importance` | How much the affected system matters | Whole number from 1 to 5 |
| `cost` | What the fix takes (e.g. engineer-hours) | Whole number, 0 or more |
| `risk_reduction` | Risk removed once the fix is applied | Number, 0 or more |

```csv
id,name,severity,asset_importance,cost,risk_reduction
V001,SQL injection in login form,9.8,5,40,44.1
V002,Outdated OpenSSL on web server,7.5,5,25,31.9
```

The **Download a CSV template** button in the app gives you a ready-made starting file.

### When a record is rejected

A row is rejected, and listed with its reason in the *Your data* tab, if any of these is true:

- a required field is missing or blank
- `severity` is not a number or is outside 0 to 10
- `asset_importance` is not a whole number from 1 to 5
- `cost` is negative, fractional or not a number (`12.0` is accepted, `3.5` is not)
- `risk_reduction` is negative or not a number
- the `id` was already used by an earlier row (the first one is kept)

If a required column is missing from the header, the app names the missing columns and every row is rejected.
An empty file is not an error: the app says there are no valid fixes to prioritize.

### Budget rules

The budget must be a **whole number that is 0 or more**. A budget of 0 can only select free fixes (cost 0).
If every fix costs more than the budget, nothing is selected and the app says so.

---

## 7. How the numbers are calculated

For a chosen set of fixes S and a budget B:

- **Total cost** = sum of `cost` over S, and it never exceeds B
- **Total risk reduction** = sum of `risk_reduction` over S
- **Remaining budget** = B − total cost
- **Budget used** = total cost / B × 100 (shown as 0% when B = 0)
- **Share of all risk covered** = chosen risk reduction / risk reduction of all valid fixes × 100
- **Optimality gap** = (DP − Greedy) / DP × 100, so 0% means Greedy matched the best answer
- **Risk score** = severity × asset importance. This is shown for reference only and does not change the results

**Greedy:** drop fixes that cost more than B or have no benefit, sort by risk reduction ÷ cost (free fixes first),
break ties by higher risk reduction, then lower cost, then id, and take each fix that still fits.

**Dynamic programming:** `dp[i][w]` is the best risk reduction using the first *i* fixes with budget *w*.
If `cost_i > w` it equals `dp[i-1][w]`, otherwise `max(dp[i-1][w], dp[i-1][w - cost_i] + risk_reduction_i)`.
The chosen fixes are found by tracing back through the table. If the table would be larger than 25 million cells
(about 200 MB), the app shows a message instead of freezing and Greedy still runs. You can change this limit with
`DEFAULT_MAX_CELLS` in `core/knapsack.py`.

**Measuring time and memory:** time is the median of several runs using `time.perf_counter()`. Peak memory is
measured with `tracemalloc` in a separate run so it does not slow down the timings.

## 8. Data

Only synthetic or authorized data is used, because the project focuses on defensive remediation.

- `data/sample.csv`: 22 realistic example vulnerabilities
- `data/edge_cases/`: small files for unusual situations. Picking one in the app fills in a matching budget

| File | Budget | What it shows |
|---|---|---|
| `greedy_fails.csv` | 50 | Greedy gets 160, DP gets 220 (a 27.27% gap) |
| `empty.csv` | 100 | An empty file is handled with a friendly message |
| `all_unaffordable.csv` | 50 | Every fix costs more than the budget, so nothing is selected |
| `free_fixes.csv` | 15 | Cost-0 fixes are taken first, a zero-benefit fix is never picked |
| `ties.csv` | 30 | Equal ratios give the same result every time |
| `invalid_rows.csv` | 30 | 3 valid rows and 9 rejected rows, each with a reason |

- **Synthetic generator:** choose the number of fixes and a seed in the app. The same seed always gives the same data.
  Cost loosely follows severity, and `risk_reduction = severity × importance × effectiveness` (effectiveness 0.5 to 1.0).

## 9. Project structure

```
vulnprior/
├── app.py                  Entry point: page config, styling, top navigation
├── ui.py                   Shared CSS and small UI helpers (animated budget bars, footer)
├── views/
│   ├── home.py             Home page with the interactive demo
│   └── prioritizer.py      The tool: sidebar, validation, tabs, comparison, scaling
├── core/
│   ├── models.py           Data classes (Vulnerability, AlgorithmResult, ValidationReport)
│   ├── validator.py        Validation rules and CSV loading
│   ├── greedy.py           Greedy algorithm
│   ├── knapsack.py         0/1 knapsack dynamic programming
│   ├── benchmark.py        Timing, memory, comparison and scaling experiment
│   └── generator.py        Seeded synthetic data
├── data/
│   ├── sample.csv
│   └── edge_cases/         The six edge-case files above
├── tests/
│   ├── test_validator.py
│   └── test_algorithms.py
├── .streamlit/config.toml  Light theme and colours
├── conftest.py             Lets pytest find the core package (can stay empty)
├── requirements.txt
└── README.md
```

Keep this layout. The app looks for `data/sample.csv` and `data/edge_cases/` by these exact names.

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'streamlit'` (or numpy, pandas) | Run `python -m pip install -r requirements.txt`, using the same Python you run the app with |
| `streamlit` is not recognized | Use `python -m streamlit run app.py` |
| Yellow squiggle under `import numpy` in VS Code | Only the editor is confused. Press `Ctrl+Shift+P`, choose **Python: Select Interpreter**, and pick the Python (or `.venv`) you installed into |
| `ImportError: cannot import name ...` from `core` | A file in `core/` has old content. Replace it with the project's version, save, stop Streamlit and start it again |
| Edge-case list is empty, or `sample.csv` not found | Put the files in `data/` and `data/edge_cases/` exactly as shown in the structure above |
| Tests fail with file-not-found errors | Run `python -m pytest` from the project folder, not from inside `tests/` |
| Page still shows old behaviour after an edit | Stop with `Ctrl+C`, start again, and refresh the browser |
| Error about `st.navigation` or `position` | Update Streamlit: `python -m pip install -U streamlit` |

## 11. Team

| Name | Roll number |
|---|---|
| Mustafa Ahmed Siddiqui | CT-24261 |
| Wasif Ahmed Soomro | CT-24269 |
| Muhammad Mahad Hashmi | CT-24287 |
| Muhammad Zaid Khan | CT-24300 |
