.PHONY: clean clean-test clean-pyc clean-build
bold := $(shell tput bold)
rsttxt := $(shell tput sgr0)


clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@printf '$(bold)Cleaning Artifacts...\n$(rsttxt)'
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr pip-wheel-metadata/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	- rm -fr .tox/
	- rm -f .coverage
	- rm -fr htmlcov/
	find . -name '.pytest_cache' -exec rm -fr {} +
	- rm -f .testmondata
	- rm -rf .tmontmp
	- rm cov.xml test_log.xml

test: ## run tests quickly with the default Python
	pytest

watch-build: clean ## build pytest-testmon db
	pytest --testmon -c pyproject.toml

watch: clean ## watch tests
	- pytest --testmon
	ptw --spool 2000 --onpass "make watch-cov" --clear -- --testmon -vv -c pyproject.toml

watch-cov: ## watch test coverage
	pytest -n'auto' --forked --cov --cov-append --cov-config=pyproject.toml --cov-report=xml:cov.xml --cov-report term

coverage: ## generate coverage
	pytest -n'auto' --cov --cov-config=pyproject.toml

coverage-html: ## generate coverage html
	pytest -n'auto' --cov --cov-config=pyproject.toml --cov-report html

gendoc: ## Generate Docs
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@printf '$(bold)Docs Generated!\n$(rsttxt)'

test-release: dist ## release on pypi-test repo
	@printf '$(bold)Uploading Test Release to TestPyPi...\n$(rsttxt)'
	poetry publish -r test
	@printf '$(bold)Test Released published!\n$(rsttxt)'

release: dist ## package and release
	@printf '$(bold)Uploading package to PyPi...\n$(rsttxt)'
	poetry publish
	git push --tags
	@printf '$(bold)Done! Tags Pushed!\n$(rsttxt)'

dist: clean ## builds package
	@printf '$(bold)Building Source and Wheel...\n$(rsttxt)'
	- rm README.rst
	poetry build
	ls -l dist

install: clean ## install pkg
	python setup.py install
