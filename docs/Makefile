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
	gitbook serve

build: setup
	gitbook build

setup: xos-gui xos-tosca
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

# link directories that contain other documentation
xos-gui:
	ln -s ../../xos-gui/docs xos-gui

xos-tosca:
	ln -s ../../xos-tosca/docs xos-tosca


clean:
	rm -rf $(GENERATED_DOCS)
	rm -rf _book
	rm -rf node_modules
	rm -rf xos xos-gui xos-tosca
