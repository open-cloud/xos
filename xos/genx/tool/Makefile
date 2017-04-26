# Replace the line below with the location of xosgen
PREFIX=.
XOSGEN=$(PREFIX)/tool/xosgen

DJANGO_TARGET=$(PREFIX)/targets/django-split.xtarget
INIT_TARGET=$(PREFIX)/targets/init.xtarget
XPROTOS_TMP := $(shell mktemp)

%.py: %.xproto
	$(XOSGEN) --attic attic --input $< --target $(DJANGO_TARGET) --output $@ 

xprotos = $(wildcard *.xproto)
pys = $(xprotos:.xproto=.py)

all: $(pys) __init__.py

__init__.py: $(xprotos)
	cat $(xprotos) > $(XPROTOS_TMP)
	$(XOSGEN) --attic attic --input $(XPROTOS_TMP) --target $(INIT_TARGET) --output $@ | awk '!seen[$$0]++' > __init__.py

.PHONY: clean all init
	
clean:
	rm -f $(pys) 
	rm -f __init__.py
