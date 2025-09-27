.PHONY: lint pylint flake8 black mypy security test-imports format

# Individual targets first, Will only run black
black:
	black --check SRC Utilities TestDataCommon

flake8:
	flake8 SRC Utilities TestDataCommon

pylint:
	pylint SRC Utilities TestDataCommon --disable=C0411,W0718

mypy:
	mypy SRC Utilities TestDataCommon

# Security
security:
	bandit -r SRC Utilities TestDataCommon

# Test imports
test-imports:
	pytest --collect-only

# Format code
format:
	black SRC Utilities TestDataCommon

# It will run black, flake8, and pylint in sequence
lint: black flake8 pylint