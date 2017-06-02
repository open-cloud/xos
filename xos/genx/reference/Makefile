PREFIX=..

# Replace the line below with the location of xosgen
%.ok: %.py
	PYTHONPATH=$(PYTHONPATH):$(PREFIX)/reference python -m $(subst /,.,$(subst .py,,$<))


oks = $(tests:.py=.ok)

tests: $(oks)
	
.PHONY: clean all init tests
	
clean:
	rm -f $(oks) 
