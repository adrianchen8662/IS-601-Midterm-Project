# IS-601 Midterm Project - Interactive Calculator

## Project Description

An advanced calculator application with various arithmetic operations, a command-line interface (REPL), and robust error handling for IS-601: Python for Web API Development

**Key features:**

- Infix arithmetic: `1 + 2`, `10 / 4`, `7 * 3`, `9 - 5`
- Operator continuation using the previous result: `+ 5`, `* 2`
- Keyword operations: `power`, `root`, `modulus`, `intdiv`, `percentage`, `absdiff`
- `ans` keyword as a stand-in for the previous result in keyword expressions
- Undo and redo for calculations
- Save and load history to/from a CSV file
- Auto-save on exit
- Observer-based architecture (logging and auto-save observers)
- Fully configurable via environment variables

---

## Installation Instructions

**Prerequisites:** Python 3.11 or higher.

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd IS-601-Midterm-Project
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:

   ```bash
   # Linux / macOS
   source .venv/bin/activate

   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration Setup

The application is configured through environment variables loaded from a `.env` file in the project root. Create the file before running the calculator:

```bash
touch .env
```

Add any of the following variables to override the defaults:

```dotenv
# Base directory for all application data (default: project root)
CALCULATOR_BASE_DIR=/path/to/data

# Directory where history CSV is stored (default: <base_dir>/history)
CALCULATOR_HISTORY_DIR=/path/to/history

# Full path to the history CSV file (default: <history_dir>/calculator_history.csv)
CALCULATOR_HISTORY_FILE=/path/to/history/calculator_history.csv

# Directory where log files are stored (default: <base_dir>/logs)
CALCULATOR_LOG_DIR=/path/to/logs

# Full path to the log file (default: <log_dir>/calculator.log)
CALCULATOR_LOG_FILE=/path/to/logs/calculator.log

# Maximum number of history entries to retain (default: 1000)
CALCULATOR_MAX_HISTORY_SIZE=1000

# Automatically save history on exit (default: true)
CALCULATOR_AUTO_SAVE=true

# Decimal precision for calculations (default: 10)
CALCULATOR_PRECISION=10

# Maximum absolute value accepted as input (default: 1e999)
CALCULATOR_MAX_INPUT_VALUE=1e999

# File encoding for history and logs (default: utf-8)
CALCULATOR_DEFAULT_ENCODING=utf-8
```

All variables are optional. The application runs with defaults when `.env` is absent or empty.

---

## Usage Guide

Start the calculator:

```bash
.venv/bin/python main.py
```

The REPL displays a prompt and accepts one command per line. The prompt shows the current result when one is available:

```
> 1 + 2
3
[3] > * 4
12
[12] >
```

### Supported Commands

| Input | Description | Example |
|---|---|---|
| `<a> <op> <b>` | Full infix expression | `1 + 2`, `10 / 4` |
| `<op> <b>` | Continue from previous result | `+ 5`, `* 2` |
| `power <a> <b>` | Raise `a` to the power `b` | `power 2 8` → `256` |
| `root <a> <b>` | Compute the `b`th root of `a` | `root 27 3` → `3` |
| `modulus <a> <b>` | Remainder of `a ÷ b` | `modulus 10 3` → `1` |
| `intdiv <a> <b>` | Integer quotient of `a ÷ b` | `intdiv 10 3` → `3` |
| `percentage <a> <b>` | `(a / b) × 100` | `percentage 25 200` → `12.5` |
| `absdiff <a> <b>` | Absolute difference `\|a − b\|` | `absdiff 9 4` → `5` |
| `=` or `ans` | Show the current result | `=` → `= 12` |
| `history` or `hist` | Display calculation history | |
| `undo` | Undo the last calculation | |
| `redo` | Redo the last undone calculation | |
| `save` | Save history to file | |
| `load` | Load history from file | |
| `c` or `clear` | Clear result and history | |
| `h` or `help` | Show help text | |
| `e` or `exit` | Save history and exit | |

**Supported infix operators:** `+`, `-`, `*`, `/`, `%`, `//`

**Using `ans` in keyword expressions:** Either operand may be replaced with `ans` to substitute the previous result:

```
> power 2 8
256
[256] > root ans 2
16
```

---

## Testing Instructions

### Run the test suite

```bash
.venv/bin/pytest
```

### Run with verbose output

```bash
.venv/bin/pytest -v
```

### Run tests with coverage

```bash
coverage run -m pytest -v
coverage report
```

If coding from a remote server (like me), a temporary file might need to be created to allow for the coverage report to be generated. The in this case, a `.coveragerc` file should be created to write a data file to `/tmp/.coverage`. 

.coveragerc contents: 
```bash
[run]
data_file = /tmp/.coverage

```

Python automatically creates bytecode cache files in the __pycache__ folder. However, these files cause unit tests like coverage and pytest to not update. To remove __pycache__ folders:
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```

The project targets **100% test coverage**. 

### Test structure

| File | What it tests |
|---|---|
| `tests/test_operations.py` | Individual operation classes (`Addition`, `Division`, `Modulus`, etc.) |
| `tests/test_calculation.py` | `CalculationFactory` and `Calculation` subclasses |
| `tests/test_calculator.py` | `Calculator` class and the REPL (`calculator_repl`) |
| `tests/test_validators.py` | `InputValidator` number parsing and `ans` keyword |
| `tests/test_config.py` | `CalculatorConfig` environment variable handling |
| `tests/test_exceptions.py` | Custom exception types |
| `tests/test_history.py` | Observer classes and history management |

## CI/CD Information

The project uses **GitHub Actions** for continuous integration. The workflow is defined in `.github/workflows/tests.yml`.

**Trigger:** The pipeline runs automatically on every push or pull request targeting the `main` or `master` branch.

**Steps:**

1. **Checkout** - clones the repository.
2. **Set up Python 3.11** - provisions the runtime environment.
3. **Install dependencies** - upgrades `pip` and installs all packages from `requirements.txt`.
4. **Run tests with coverage** - executes the full test suite via `coverage run -m pytest -v` and enforces **100% coverage** with `coverage report --fail-under=100`. The build fails if any test fails or coverage drops below 100%.
5. **Create a release** - creates a GitHub release of the code when pushed to main