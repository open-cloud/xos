NAME = opencloud
SPECFILE = $(NAME).spec
VERSION = $(shell rpm -q --specfile $(SPECFILE) --qf '%{VERSION}\n' | head -n 1)
RELEASE = $(shell rpm -q --specfile $(SPECFILE) --qf '%{RELEASE}\n' | head -n 1)

PWD = $(shell pwd)

dist rpm: $(NAME)-$(VERSION)-$(RELEASE).rpm

$(NAME)-$(VERSION).tar.gz:
	mkdir -p $(NAME)-$(VERSION)
	rsync -av --exclude=.svn --exclude=.git --exclude=*.tar.gz --exclude=__history --exclude=$(NAME)-$(VERSION)/ ./ $(NAME)-$(VERSION)
	tar -czf $@ $(NAME)-$(VERSION)
	rm -fr $(NAME)-$(VERSION)

$(NAME)-$(VERSION)-$(RELEASE).rpm: $(NAME)-$(VERSION).tar.gz
	mkdir -p build
	rpmbuild -bb --define '_sourcedir $(PWD)' \
                --define '_builddir $(PWD)/build' \
                --define '_srcrpmdir $(PWD)' \
                --define '_rpmdir $(PWD)' \
                --define '_build_name_fmt %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
                $(SPECFILE)

srpm: $(NAME)-$(VERSION)-$(RELEASE).src.rpm
$(NAME)-$(VERSION)-$(RELEASE).src.rpm: $(NAME)-$(VERSION).tar.gz
	rpmbuild -bs --define "_sourcedir $$(pwd)" \
                --define "_srcrpmdir $$(pwd)" \
                $(SPECFILE)

clean:
	rm -f $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)-$(RELEASE).src.rpm $(NAME)-$(VERSION)-$(RELEASE).noarch.rpm
	rm -rf build

.PHONY: dist

