platform := $(shell uname)
pkgs := serverless python3

install: install-third-party-tools install-sls-modules install-python-dependencies

ifeq (${platform},Darwin)
install-third-party-tools:
	brew list ${pkgs} || brew install ${pkgs}
else
install-third-party-tools:
	@echo "${platform} is a platform we have no presets for, you'll have to install the third party dependencies manually ${pkgs}"
endif

install-python-dependencies:
	python3.7 -m venv py37
	. py37/bin/activate; \
	pip install --upgrade pip; \
	pip install --no-deps -r requirements.txt; \
	pip install --no-deps --upgrade awscli-local

install-sls-modules:
	npm install

clean:
	rm -rf .build
	rm -rf .serverless
	rm -rf py37

freeze:
	pip freeze --local | grep -v myapp > requirements.txt

.PHONY: install install-sls-modules install-python-dependencies clean
