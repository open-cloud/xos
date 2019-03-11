# Makefile for building CORD docs site, guide.opencord.org
# Building docs requires the following tools:
#  - Gitbook toolchain: https://toolchain.gitbook.com/setup.html
#  - NPM (for Gitbook and Swagger)
#  - Python (for build glossary script)
#  - linkchecker (for test target) http://wummel.github.io/linkchecker/

default: serve

# use bash for pushd/popd, and to fail if commands within  a pipe fail
SHELL = bash -o pipefail

GENERATED_DOCS = 

LINT_STYLE ?= mdl_relaxed.rb

serve: setup
	gitbook serve --log=debug --debug

build: setup
	gitbook build

setup:
	gitbook init
	gitbook install

test: linkcheck lint

linkcheck: build
	linkchecker -a _book/

lint:
	@echo "markdownlint(mdl) version: `mdl --version`"
	@echo "style config:"
	@echo "---"
	@cat $(LINT_STYLE)
	@echo "---"
	mdl -s $(LINT_STYLE) `find -L . ! -path "./_book/*" ! -path "./node_modules/*" -name "*.md"`

# HOW TO
# - load the virtual env (https://guide.opencord.org/xos/dev/local_env.html)
# - run `make`
# - open the browser at `http://127.0.0.1:8080/ui`
# - you'll see the 'core' apis
# - you can see a list of available apis at `http://127.0.0.1:8080/specs/`
# - just replace the swagger file (top bar) with another one to see different APIs (to be improved)

DOCSDIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

swagger: swagger_clean swagger_docs swagger_serve_spec

venv-xosdocs:
	./venv-xosdocs.sh

swagger_docs: venv-xosdocs
	bash -c 'source $(DOCSDIR)venv-xosdocs/bin/activate && python $(DOCSDIR)scripts/swagger_docs.py'

swagger_clean:
	rm -rf swagger/specs/*

venv_clean:
	rm -rf $(DOCSDIR)venv-xosdocs

swagger_serve_spec:
	http-server --cors ./swagger

clean: swagger_clean venv_clean
	rm -rf $(GENERATED_DOCS)
	rm -rf _book
	rm -rf node_modules
