export PYTHONPATH = ./src
export MYPYPATH = ./stubs
export SOURCE_PATH = ./src

ENVIRONMENT := "preprod"

.PHONY: help

help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
	
install:  ## Install dependencies
	poetry install

requirements:  ## Generate requirements.txt from poetry.lock
	@poetry lock && \
	poetry export -f requirements.txt --output requirements.txt

## checks code quality
isort-save: ## Formats imports
	@poetry run isort ${SOURCE_PATH} && \
	echo 'Isort save success!\n'

black-save: ## Formats code
	@poetry run black ${SOURCE_PATH}  && \
	echo 'Black save success!\n'

flake8: ## Runs some checks on code
	@poetry run flake8 ${SOURCE_PATH}  && \
	echo 'Flake8 check success!\n'

mypy: ## Checks python typing
	@poetry run mypy ${SOURCE_PATH}  && \
	echo 'Mypy check success!\n'

checks: blank-line isort-save black-save flake8 mypy ## Runs security checks, format, flake8 and mypy

blank-line:
	@echo

tests: ## Runs unit tests
	@poetry run pytest -xvv ${SOURCE_PATH} -k "$(k)" $(1)

coverage: ## Runs the coverage command
	@echo "Running coverage..." && \
	poetry run coverage report && \
	poetry run coverage xml

report-html: ## Runs the coverage report in HTML
	@echo "Running coverage report in HTML..." && \
	poetry run coverage html

sync-terraform: ## Executa o apply do terraform sem pedir confirmacao
	@ENVIRONMENT=$(ENVIRONMENT) ./scripts/sync_terraform.sh
