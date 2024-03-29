# Makefile for packaging and testing env-asm
#
# This Makefile has the following targets:
#
# package_managers - Sets up python managers and python package managers
# clean_env - Removes the virtuale env
# dependencies - Installs all dependencies for a project
# setup - Sets up the entire development environment and installs dependencies
# clean_docs - Clean the documentation folder
# clean - Clean any generated files (including documentation)
# open_docs - Open any docs generated with "make docs"
# docs - Generated sphinx docs
# lint - Run code linting and static checks
# format - Format code using black
# test - Run tests using pytest

OS = $(shell uname -s)

PACKAGE_NAME=env-asm
MODULE_NAME=env_asm

ifdef CIRCLECI
# Use CircleCIs version
PYTHON_VERSION=
else
PYTHON_VERSION=3.6.5
endif


# Print usage of main targets when user types "make" or "make help"
help:
	@echo "Please choose one of the following targets: \n"\
	      "    setup: Setup development environment and install dependencies\n"\
	      "    test: Run tests\n"\
	      "    lint: Run code linting and static checks\n"\
	      "    docs: Build Sphinx documentation\n"\
	      "    open_docs: Open built documentation\n"\
	      "\n"\
	      "View the Makefile for more documentation"
	@exit 2


# Utility to verify we arent in a virtualenv
.PHONY: check_not_inside_venv
check_not_inside_venv:
ifeq (${OS}, Darwin)
	which pip | grep -q ".pyenv" || (echo "Please deactivate your virtualenv and try again" && exit 1)
endif


# Sets up pyenv, poetry, and any other package/language managers (e.g. NPM)
.PHONY: package_managers
package_managers: check_not_inside_venv
ifndef GEMFURY_API_TOKEN
	@echo "Must set GEMFURY_API_TOKEN environment variable" && exit 1;
endif
ifeq (${OS}, Darwin)
# Install pyenv and ensure we remain up to date with pyenv so that new python
# versions are available for installation
	-brew install pyenv 2> /dev/null
	-brew upgrade pyenv 2> /dev/null
	-pyenv rehash
endif
ifdef PYTHON_VERSION
	pyenv install -s ${PYTHON_VERSION}
endif
# Conditionally install pipx so that we can globally install poetry
	pip install --user --upgrade --force-reinstall pipx
	pipx ensurepath
	-pipx install --force poetry --pip-args="--upgrade"
# Configure poetry to access our private gemfury repository
# "poetry config" currently has a bug where it does not auto-create
# the config file. Manually create it for now
ifeq (${OS}, Darwin)
	-mkdir -p "${HOME}/Library/Application Support/pypoetry/"
	touch "${HOME}/Library/Application Support/pypoetry/config.toml"
else
	-mkdir -p "${HOME}/.config/pypoetry/"
	touch "${HOME}/.config/pypoetry/config.toml"
endif
	poetry config repositories.jyve https://pypi.fury.io/jyve
	@poetry config http-basic.jyve "${GEMFURY_API_TOKEN}" ""


# Remove the virtual environment
.PHONY: clean_env
clean_env:
	-poetry env remove ${PYTHON_VERSION}


# Builds dependencies needed for deploying the package
.PHONY: deploy_dependencies
deploy_dependencies:
ifeq (${OS}, Darwin)
	-brew install libmagic
endif


# Builds all dependencies for a project
.PHONY: dependencies
dependencies:
	poetry install


.PHONY: git_tidy
git_tidy:
	-pipx install --force git-tidy --pip-args="--upgrade"
	git tidy --template -o .gitcommit.tpl
	git config --local commit.template .gitcommit.tpl


.PHONY: pre_commit
pre_commit:
	poetry run pre-commit install


# Sets up environment and installs dependencies
.PHONY: setup
setup: check_not_inside_venv package_managers git_tidy dependencies pre_commit


# Clean the documentation folder
.PHONY: clean_docs
clean_docs:
	-cd docs && poetry run make clean


# Clean any auto-generated files
.PHONY: clean
clean: clean_docs clean_env
	rm -rf dist/*
	rm -rf coverage .coverage .coverage*


# Open the build docs (only works on Mac)
.PHONY: open_docs
open_docs:
ifeq (${OS}, Darwin)
	open docs/_build/html/index.html
else
	@echo "Open 'docs/_build/html/index.html' to view docs"
endif


# Build Sphinx autodocs
.PHONY: docs
docs: clean_docs  # Ensure docs are clean, otherwise weird render errors can result
	cd docs && poetry run make html


# Run code linting and static analysis
.PHONY: lint
lint:
	poetry run black . --check
	poetry run flake8 -v ${MODULE_NAME}/
	poetry run temple update --check
	poetry run make docs  # Ensure docs can be built during validation


# Lint commit messages and show changelog when on circleci
check_changelog:
ifdef CIRCLECI
	git tidy-log :github/pr -o :github/pr
endif
	git tidy-lint :github/pr


# Format code
format:
	poetry run black .


# Run tests
.PHONY: test
test:
	poetry run coverage run -m pytest
	poetry run coverage report


# Show the version and name of the project
.PHONY: version
version:
	-@poetry version | rev | cut -f 1 -d' ' | rev


.PHONY: project_name
project_name:
	-@poetry version | cut -d' ' -f1
