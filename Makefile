SHELL=/bin/bash -euo pipefail

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

install-python:
	poetry install

install-node:
	npm install
	cd sandbox && npm install

.git/hooks/pre-commit:
	cp scripts/pre-commit .git/hooks/pre-commit

install: install-node install-python .git/hooks/pre-commit

lint:
	npm run lint
	find . -name '*.py' -not -path '**/.venv/*' | xargs poetry run flake8

clean:
	rm -rf build
	rm -rf dist

copy-examples-to-sandbox:
	mkdir -p sandbox/responses
	cp specification/components/examples/* sandbox/responses

publish: clean copy-examples-to-sandbox
	mkdir -p build
	npm run publish 2> /dev/null

serve:
	npm run serve

check-licenses:
	npm run check-licenses
	scripts/check_python_licenses.sh

format:
	poetry run black **/*.py

start-sandbox: # starts a local version of the sandbox
	cd sandbox && npm run start

build-proxy:
	scripts/build_proxy.sh

_dist_include="pytest.ini poetry.lock poetry.toml pyproject.toml Makefile build/. tests"

release: clean publish build-proxy
	mkdir -p dist
	for f in $(_dist_include); do cp -r $$f dist; done
	cp ecs-proxies-deploy.yml dist/ecs-deploy-sandbox.yml
	cp ecs-proxies-deploy.yml dist/ecs-deploy-internal-qa-sandbox.yml
	cp ecs-proxies-deploy.yml dist/ecs-deploy-internal-dev-sandbox.yml

dist: release

test: smoketest sandboxtest e2etest

sandboxtest:
	make --no-print-directory -C sandbox test-report

pytest-guards: guard-SERVICE_BASE_PATH guard-APIGEE_ENVIRONMENT guard-SOURCE_COMMIT_ID guard-STATUS_ENDPOINT_API_KEY

smoketest: pytest-guards
	poetry run pytest -vv --junitxml=smoketest-report.xml -s -m smoketest

e2etest: pytest-guards
	poetry run pytest -vv --junitxml=e2e-report.xml -s -m e2e
