.PHONY: install-deps doctor check lint format test coverage clean zip reload-config run

# requirements
install-deps:
	poetry install

doctor:
	@echo "🔎 Checking Python, passlib, and bcrypt versions..."
	@poetry run python --version | grep -q "3.1" && echo "✅ Python version..." || echo "❌ Warning: Python 3.1x.x is recommended"
	@poetry run python -c "import passlib; assert passlib.__version__ == '1.7.4', '❌ passlib version should be 1.7.4'" && echo "✅ passlib version is correct" || true
	@poetry run python -c "import bcrypt; assert bcrypt.__version__ == '3.2.2', '❌ bcrypt version should be 3.2.2'" && echo "✅ bcrypt version is correct" || true

# quality 
check: doctor
	@echo "🔎 Checking poetry..."
	poetry check

lint: 
	@echo "🔎 Running linters..."
	poetry run ruff check .

format:
	@echo "🔎 Formatting code..."
	poetry run ruff format .

# testing
test:
	@echo "🔎 Running tests..."
	ENV_FILE=.env.test poetry run pytest --cov=src --cov-report html:docs/html

coverage:
	@echo "🔎 Opening coverage report..."
	open docs/html/index.html

# house cleaning
clean:
	@echo "🔎 Cleaning up the project..."
	rm -rf doc/html .coverage .ruff_cache .pytest_cache db/*.db
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '.DS_Store' -delete

# zip and shipping
zip: clean
	cd .. && zip -r portfolio-workbench.zip back/
	@echo "Zipped the backend into portfolio-workbench.zip"

# running
reload-config:
	@echo "🔎 Reloading the files..."
	cd .. && unzip -o portfolio-workbench.zip && cd back

run:
	@echo "🔎 Running the server..."
	ENV_FILE=.env poetry run uvicorn app.main:app --reload
