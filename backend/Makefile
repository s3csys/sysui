# Makefile for backend development and operations

.PHONY: setup run test test-cov lint migrate migrate-up migrate-down init-db clean check benchmark cert help

# Default target
help:
	@echo "Available commands:"
	@echo "  setup       - Install dependencies"
	@echo "  run         - Run the application"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  lint        - Run linting"
	@echo "  migrate     - Generate a new migration"
	@echo "  migrate-up  - Apply migrations"
	@echo "  migrate-down- Rollback migrations"
	@echo "  init-db     - Initialize database with default data"
	@echo "  check       - Check system dependencies"
	@echo "  benchmark   - Run authentication system benchmark"
	@echo "  cert        - Generate self-signed SSL certificate"
	@echo "  clean       - Remove cache and temporary files"

# Install dependencies
setup:
	pip install -r requirements.txt

# Run the application
run:
	python run.py

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=app --cov-report=term-missing --cov-report=xml

# Run linting
lint:
	flake8 app tests

# Generate a new migration
migrate:
	alembic revision --autogenerate -m "$(message)"

# Apply migrations
migrate-up:
	alembic upgrade head

# Rollback migrations
migrate-down:
	alembic downgrade -1

# Initialize database with default data
init-db:
	python -m scripts.init_db

# Check system dependencies
check:
	python -m scripts.check_dependencies

# Run authentication system benchmark
benchmark:
	python -m scripts.benchmark

# Generate self-signed SSL certificate
cert:
	python -m scripts.generate_cert

# Clean cache and temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete