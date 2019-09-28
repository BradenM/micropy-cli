.PHONY: clean clean-test clean-pyc clean-build
bold := $(shell tput bold)
rsttxt := $(shell tput sgr0)


clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@printf '$(bold)Cleaning Artifacts...\n$(rsttxt)'
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -f .testmondata

lint: ## check style with flake8
	flake8 micropy tests --config=setup.cfg

test: ## run tests quickly with the default Python
	pytest -v

test-all: ## run tests on every Python version with tox
	tox

watch-build: clean ## build pytest-testmon db
	pytest --testmon
	$(MAKE) watch

watch: ## watch tests
	ptw -- --testmon

coverage: ## generate coverage
	pytest --cov --cov-config=setup.cfg

coverage-html:
	pytest --cov --cov-config=setup.cfg --cov-report html


gendoc: ## Generate Docs
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@printf '$(bold)Docs Generated!\n$(rsttxt)'

test-release: dist ## release on pypi-test repo
	@printf '$(bold)Uploading Test Release to TestPyPi...\n$(rsttxt)'
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	@printf '$(bold)Test Released published!\n$(rsttxt)'

release: dist ## package and release
	@printf '$(bold)Uploading package to PyPi...\n$(rsttxt)'
	twine upload dist/*
	git push --tags
	@printf '$(bold)Done! Tags Pushed!\n$(rsttxt)'

dist: clean ## builds package
	@printf '$(bold)Building Source and Wheel...\n$(rsttxt)'
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install pkg
	python setup.py install
