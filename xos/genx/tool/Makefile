# Replace the line below with the location of xosgen
PREFIX=../
XOSGEN=python $(PREFIX)/tool/xosgen

DJANGO_TARGET=$(PREFIX)/targets/django-split.xtarget
INIT_TARGET=$(PREFIX)/targets/init.xtarget
XPROTOS_TMP := $(shell mktemp)

# Rule to compile Python files
%.py: %.xproto
	$(XOSGEN) --attic attic --target $(DJANGO_TARGET) --output $@ $<

# Rule to produce test results
%.ok: %.py
	PYTHONPATH=$(PYTHONPATH):$(PREFIX)/tool python -m $(subst /,.,$(subst .py,,$<))

# List of xprotos 
xprotos = $(wildcard *.xproto)
pys = $(xprotos:.xproto=.py)

# List of tests
tests = $(wildcard tests/*test.py)
oks = $(tests:.py=.ok)

all: $(pys) __init__.py

__init__.py: $(xprotos)
	cat $(xprotos) > $(XPROTOS_TMP)
	$(XOSGEN) --attic attic --target $(INIT_TARGET) --output $@ $(XPROTOS_TMP) | awk '!seen[$$0]++' > __init__.py

tests: $(oks)
	
.PHONY: clean all init tests
	
clean:
	rm -f $(pys) 
	rm -f $(oks) 
	rm -f __init__.py
