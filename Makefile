CURRENT_SIGN_SETTING := $(shell git config commit.gpgSign)

.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean - run clean-build and clean-pyc"
	@echo "dist - build package and cat contents of the dist directory"
	@echo "lint - fix linting issues with pre-commit"
	@echo "test - run tests quickly with the default Python"
	@echo "benchmark - run benchmark tests"
	@echo "docs - generate docs and open in browser (linux-docs for version on linux)"
	@echo "autobuild-docs - live update docs when changes are saved"
	@echo "package-test - build package and install it in a venv for manual testing"
	@echo "notes - consume towncrier newsfragments and update release notes in docs - requires bump to be set"
	@echo "release - package and upload a release (does not run notes target) - requires bump to be set"

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean: clean-build clean-pyc

dist: clean
	python -m build
	ls -l dist

lint:
	@pre-commit run --all-files --show-diff-on-failure || ( \
		echo "\n\n\n * pre-commit should have fixed the errors above. Running again to make sure everything is good..." \
		&& pre-commit run --all-files --show-diff-on-failure \
	)

test:
	python -m pytest tests/core tests/ens tests/integration

benchmark:
	python -m tox run -e benchmark

# docs commands

docs: check-docs
	open docs/_build/html/index.html

linux-docs: check-docs
	xdg-open docs/_build/html/index.html

autobuild-docs:
	sphinx-autobuild --open-browser docs docs/_build/html

# docs helpers

validate-newsfragments:
	python ./newsfragments/validate_files.py
	towncrier build --draft --version preview

check-docs: build-docs validate-newsfragments

build-docs:
	sphinx-apidoc -o docs/ . "*conftest*" "tests" "web3/tools/*"
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(MAKE) -C docs doctest

check-docs-ci: build-docs build-docs-ci validate-newsfragments

build-docs-ci:
	$(MAKE) -C docs epub

# release commands

package-test: clean
	python -m build
	python scripts/release/test_package.py

notes: check-bump
	# Let UPCOMING_VERSION be the version that is used for the current bump
	$(eval UPCOMING_VERSION=$(shell bump-my-version bump --dry-run $(bump) -v | awk -F"'" '/New version will be / {print $$2}'))
	# Now generate the release notes to have them included in the release commit
	towncrier build --yes --version $(UPCOMING_VERSION)
	# Before we bump the version, make sure that the towncrier-generated docs will build
	make build-docs
	git commit -m "Compile release notes for v$(UPCOMING_VERSION)"

release: check-bump check-git clean
	# verify that notes command ran correctly
	./newsfragments/validate_files.py is-empty
	CURRENT_SIGN_SETTING=$(git config commit.gpgSign)
	git config commit.gpgSign true
	bump-my-version bump $(bump)
	python -m build
	git config commit.gpgSign "$(CURRENT_SIGN_SETTING)"
	git push upstream && git push upstream --tags
	twine upload dist/*

# release helpers

check-bump:
ifndef bump
	$(error bump must be set, typically: major, minor, patch, or devnum)
endif

check-git:
	# require that upstream is configured for ethereum/web3.py
	@if ! git remote -v | grep "upstream[[:space:]]git@github.com:ethereum/web3.py.git (push)\|upstream[[:space:]]https://github.com/ethereum/web3.py (push)"; then \
		echo "Error: You must have a remote named 'upstream' that points to 'web3.py'"; \
		exit 1; \
	fi
