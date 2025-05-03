.PHONY: test lint format clean reload zip

test:
	@echo "Running tests..."
	ENV_FILE=.env.test poetry run pytest --cov=src --cov-report html:docs/html

lint:
	@echo "Running linters..."
	poetry run ruff check .

format:
	@echo "Formatting code..."
	poetry run ruff format .

clean:
	@echo "Cleaning up the project..."
	rm -rf docs/html doc/
	find . -type d -name '__pycache__' -exec rm -rf {} \;
	find . -type d -name '.pytest_cache' -exec rm -rf {} \;
	find . -type f -name '.DS_Store' -delete
	find db -type f -name '*.db' -delete

reload:
	@echo "Reloading the files..."
	cd .. && unzip -o portfolio-workbench.zip && cd back

zip: clean
	cd .. && zip -r portfolio-workbench.zip back/
	@echo "Zipped the project into portfolio-workbench.zip"
	@echo "You can now upload it to the server."

run:
	ENV_FILE=.env poetry run uvicorn app.main:app --reload
	ENV_FILE=.env poetry run uvicorn src.app.main:app --reload
