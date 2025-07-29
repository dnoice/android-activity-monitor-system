# Makefile for Android Activity Monitor System

.PHONY: help install install-dev test lint format clean docs run-monitor run-dashboard run-query

# Default target
help:
	@echo "Android Activity Monitor System - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code with black"
	@echo "  make type-check   - Run type checking with mypy"
	@echo ""
	@echo "Running:"
	@echo "  make run-monitor  - Start the monitor with default config"
	@echo "  make run-dash     - Start the dashboard"
	@echo "  make run-query    - Start interactive query tool"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Remove build artifacts and cache"
	@echo "  make docs         - Build documentation"

# Installation targets
install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt
	pre-commit install

# Testing targets
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=src --cov=utils --cov-report=html --cov-report=term

# Code quality targets
lint:
	flake8 src/ utils/ tests/
	pylint src/ utils/

format:
	black src/ utils/ tests/

format-check:
	black --check src/ utils/ tests/

type-check:
	mypy src/ utils/

# Run targets
run-monitor:
	python src/android-monitor.py -c configs/default.yaml

run-monitor-minimal:
	python src/android-monitor.py -c configs/minimal.yaml

run-monitor-performance:
	python src/android-monitor.py -c configs/performance.yaml

run-monitor-security:
	python src/android-monitor.py -c configs/security.yaml

run-dash:
	python src/android-dashboard.py

run-dash-live:
	python src/android-dashboard.py --live

run-query:
	python src/android-query.py -i

# Utility targets
diagnose:
	python utils/android-monitor-utils.py diagnose

check-deps:
	python utils/android-monitor-utils.py diagnose --check-deps

validate-config:
	python utils/android-monitor-utils.py validate configs/default.yaml

optimize-db:
	python utils/android-monitor-utils.py optimize monitor_data.db

# Documentation
docs:
	@echo "Building documentation..."
	@mkdir -p docs/_build
	# Add sphinx build commands here if using Sphinx

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/

clean-data:
	rm -f monitor_data.db monitor_data.db-journal
	rm -rf logs/*.log
	rm -rf exports/*

# Development setup
dev-setup: install-dev
	@echo "Setting up development environment..."
	@echo "Creating git hooks..."
	@echo "Development environment ready!"

# Package building
build:
	python setup.py sdist bdist_wheel

# Docker support (if needed in future)
docker-build:
	@echo "Docker support not yet implemented"

# Full test suite
test-all: lint format-check type-check test

---

# .editorconfig
# EditorConfig helps maintain consistent coding styles

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
max_line_length = 88

[*.{yml,yaml}]
indent_style = space
indent_size = 2

[*.{md,rst}]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab

[*.sh]
indent_style = space
indent_size = 4

---

# pyproject.toml
# Python project configuration

[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # Directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = [
    "tests",
]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pylint.messages_control]
disable = "C0330, C0326"

[tool.pylint.format]
max-line-length = "88"
