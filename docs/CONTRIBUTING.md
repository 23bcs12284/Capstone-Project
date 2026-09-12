# Contributing Guide

## Welcome

Thank you for your interest in contributing to the Explainable AI Loan Approval Prediction System! This document provides guidelines and best practices for contributing to the project.

---

## Getting Started

### 1. Fork the Repository

```bash
# Fork via GitHub UI, then clone your fork
git clone https://github.com/<your-username>/Capstone_project.git
cd Capstone_project
```

### 2. Set Up Upstream Remote

```bash
git remote add upstream https://github.com/original-owner/Capstone_project.git
git fetch upstream
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

---

## Branching Strategy

### Branch Naming Convention

Use descriptive branch names with the following prefixes:

| Prefix      | Purpose                        | Example                          |
|-------------|--------------------------------|----------------------------------|
| `feature/`  | New features                   | `feature/add-catboost-explainer` |
| `bugfix/`   | Bug fixes                      | `bugfix/fix-shap-additivity`     |
| `docs/`     | Documentation updates          | `docs/update-fairness-metrics`   |
| `refactor/` | Code refactoring               | `refactor/preprocessing-pipeline`|
| `test/`     | Adding or updating tests       | `test/add-api-integration-tests` |

### Creating a Branch

```bash
# Always branch from the latest main
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

---

## Code Style — PEP 8

All Python code must follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.

### Key Rules

1. **Indentation:** 4 spaces (no tabs)
2. **Line length:** Maximum 88 characters (Black formatter default)
3. **Imports:** Group and order imports as:
   - Standard library
   - Third-party packages
   - Local modules
4. **Naming conventions:**
   - `snake_case` for functions and variables
   - `PascalCase` for classes
   - `UPPER_SNAKE_CASE` for constants
5. **Docstrings:** Use Google-style docstrings for all public functions and classes

### Example

```python
"""Module for computing fairness metrics."""

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from fairness.utils import validate_groups


class FairnessEvaluator:
    """Evaluates model fairness across protected attributes.

    Args:
        protected_attributes: List of protected attribute column names.
        threshold: Maximum acceptable disparity (default: 0.10).
    """

    def __init__(self, protected_attributes, threshold=0.10):
        self.protected_attributes = protected_attributes
        self.threshold = threshold

    def compute_demographic_parity(self, y_pred, groups):
        """Compute demographic parity difference.

        Args:
            y_pred: Model predictions (binary array).
            groups: Group membership array.

        Returns:
            float: Demographic parity difference.
        """
        unique_groups = np.unique(groups)
        rates = {g: y_pred[groups == g].mean() for g in unique_groups}
        return max(rates.values()) - min(rates.values())
```

### Linting and Formatting

```bash
# Format code with Black
black . --line-length 88

# Sort imports with isort
isort . --profile black

# Lint with flake8
flake8 . --max-line-length 88 --extend-ignore E203,W503

# Type checking with mypy (optional)
mypy . --ignore-missing-imports
```

---

## Testing Requirements

### All contributions must include tests

- **New features:** Add unit tests covering the new functionality
- **Bug fixes:** Add a regression test that reproduces the bug
- **Refactoring:** Ensure existing tests still pass

### Running Tests

```bash
# Run full test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=./ --cov-report=term-missing

# Run specific test file
pytest tests/test_preprocessing.py -v

# Run in parallel (if pytest-xdist is installed)
pytest tests/ -v -n auto
```

### Coverage Requirements

- Minimum overall coverage: **85%**
- New code must have **≥ 90%** test coverage
- Do not decrease existing coverage

---

## Documentation Requirements

### Code Documentation

- All public functions and classes must have Google-style docstrings
- Complex algorithms should include inline comments explaining the logic
- Type hints are encouraged for function signatures

### Project Documentation

When adding a new feature or modifying existing behavior:

1. Update the relevant `docs/` file
2. Update `README.md` if the change affects setup, usage, or architecture
3. Add entries to `docs/KNOWN_ISSUES.md` if introducing known limitations

---

## Pull Request Process

### Before Submitting

1. **Sync with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks:**
   ```bash
   black . --check
   isort . --check --profile black
   flake8 .
   pytest tests/ -v --cov=./
   ```

3. **Commit with meaningful messages:**
   ```bash
   git add .
   git commit -m "feat: add CatBoost SHAP explainer support

   - Integrate CatBoost with SHAP TreeExplainer
   - Add unit tests for CatBoost explanations
   - Update SHAP documentation with CatBoost section"
   ```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix     | Purpose                  |
|------------|--------------------------|
| `feat:`    | New feature              |
| `fix:`     | Bug fix                  |
| `docs:`    | Documentation only       |
| `style:`   | Formatting (no logic)    |
| `refactor:`| Code refactoring         |
| `test:`    | Adding/updating tests    |
| `chore:`   | Build, CI, tooling       |

### Submitting the PR

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub against the `main` branch

3. Fill in the PR template:
   - **Description:** What does this PR do?
   - **Related Issue:** Link to relevant issue(s)
   - **Type of Change:** Feature / Bug Fix / Docs / Refactor
   - **Testing:** How was this tested?
   - **Checklist:** Confirm all checks pass

### Review Process

- All PRs require at least 1 review approval
- CI pipeline must pass (lint, tests, coverage)
- Address all review comments before merging
- Squash commits if the PR contains many small fixup commits

---

## Code of Conduct

- Be respectful and constructive in all communications
- Focus feedback on the code, not the contributor
- Welcome newcomers and help them get started
- Follow the project's technical decisions unless proposing formal changes

---

## Questions?

If you have questions about contributing, please open a discussion in the repository or contact the maintainers.
