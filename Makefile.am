SUBDIRS = po libjs service
TESTS = unittests

PYVER := 2.3
PYTHON := python$(PYVER)
HTMLDIR := /home/calvin/public_html/webcleaner.sf.net
SPLINTOPTS := +posixlib \
              -Iwc/parser -Ilibjs -I/usr/include/$(PYTHON) \
	      -nestcomment -ifempty
PYCHECKEROPTS := -F pycheckrc
PYCHECKERFILES := wc/*.py wc/filter/*.py wc/filter/rules/*.py wc/js/*.py \
                  wc/parser/*.py wc/proxy/*.py wc/proxy/auth/*.py \
		  wc/webgui/*.py wc/webgui/context/*.py \
		  wc/webgui/simpletal/*.py
SERVICEDIR := /etc/webcleaner/service

clean-local: clean-log
	-$(PYTHON) setup.py clean --all #  ignore errors for this command
	rm -f wc/parser/htmlsax.so wc/js/jslib.so wc/levenshtein.so
	find . -name '*.py[co]' | xargs rm -f
	rm -f index.html* test.gif
	rm -f config/magic.mime.mgc
	rm -f webcleaner-md5sums.txt
	rm -f _webcleaner2_configdata.py
# delete possible aborted dist build
	rm -rf webcleaner-$(VERSION)

clean-log:
	rm -f webcleaner*.log* webcleaner.err*

# to build in the current directory
localbuild: all
	$(PYTHON) setup.py build
	cp -f build/lib.linux-i686-$(PYVER)/wc/parser/htmlsax.so wc/parser/
	cp -f build/lib.linux-i686-$(PYVER)/wc/levenshtein.so wc/
	cp -f build/lib.linux-i686-$(PYVER)/wc/js/jslib.so wc/js/ || true

distclean-local:
	rm -rf dist build # just to be sure: clean build dir too
	rm -f VERSION MANIFEST _*_configdata.*

# ready for upload, signed with my GPG key
deb_signed: clean
	env CVSROOT=:ext:calvin@cvs.webcleaner.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/home/calvin/projects/cvs-build -Mwebcleaner2 -sgpg -pgpg -k32EC6F3E -rfakeroot

# add setup.py generated files to $(distdir)
# note: debian/rules install generates broken links, so delete debian
# package dirs before running sdist
dist-hook:
	rm -rf debian/webcleaner debian/webcleanertools
	$(PYTHON) setup.py sdist --keep-temp --dist-dir=$(distdir) --formats=gztar
	rm -f $(distdir)/webcleaner-$(VERSION).tar.gz
	rm -f $(distdir)/_webcleaner2_configdata.py
	rm -f webcleaner-md5sums.txt

unittests: localbuild
# regression tests
	test/run.sh test/regrtest.py
# python unit framework tests
	@for f in tests/Test*.py; do test/run.sh $$f; done
# filter and parse random data
	@echo "parse random data..."
	head -c 20000 /dev/urandom | test/run.sh test/parsefile.py - > /dev/null
	@echo "done."
	@echo "filter random data..."
	head -c 20000 /dev/urandom | test/run.sh test/filterfile.py - > /dev/null
	@echo "done."

md5sums:
	(cd config && md5sum *.zap > filter-md5sums.txt)
	(cd test/filter && md5sum *.zap > filter-md5sums.txt)
	for f in webcleaner-$(VERSION).tar.gz; do \
	  if [ ! -f $$f ]; then break; fi; \
	  md5sum $$f > webcleaner-md5sums.txt; \
	  gpg --detach-sign --armor $$f; \
	done
	(cd config && md5sum blacklists/{ads,aggressive,violence}/*.gz > extern-md5sums.txt)

VERSION:
	echo $(VERSION) > VERSION

upload:
	ncftpput upload.sourceforge.net /incoming webcleaner-$(VERSION).tar.gz

homepage: VERSION homepage-zapper
	cp ChangeLog $(HTMLDIR)/htdocs/changes.txt
	cp README $(HTMLDIR)/htdocs/readme.txt
	cp VERSION $(HTMLDIR)/htdocs/raw/
	-cp webcleaner-md5sums.txt $(HTMLDIR)/htdocs/
	$(MAKE) -C $(HTMLDIR) chmod

homepage-zapper: md5sums
	cp config/*.dtd config/webcleaner.conf config/filter-md5sums.txt config/extern-md5sums.txt $(HTMLDIR)/htdocs/filter
	cp config/*.zap $(HTMLDIR)/htdocs/filter/
	cp -r config/blacklists/ $(HTMLDIR)/htdocs/filter
	cp config/filter.dtd $(HTMLDIR)/htdocs/filter.dtd.txt
	cp config/adverts.zap $(HTMLDIR)/htdocs/adverts.zap.txt

doc:
	rm -f README
	pydoc$(PYVER) ./webcleaner > README

pycheck:
	-env PYTHONVER=2.3 pychecker $(PYCHECKEROPTS) $(PYCHECKERFILES)

ccheck:
	-splint $(SPLINTOPTS) wc/js/jslib.c

installservice:
	install -d $(SERVICEDIR)/log
	install -m 0755 service/run2 $(SERVICEDIR)/run
	install -m 0755 service/log/run $(SERVICEDIR)/log/
	if [ ! -e /var/service/webcleaner ]; then \
          ln -s /etc/webcleaner/service /var/service/webcleaner; \
	fi

# (re)generate webcleaner rules
update-blacklists:
	$(PYTHON) config/bl2wc.py


.PHONY: localbuild distclean deb_signed update-blacklists
.PHONY: gentest onlinetest offlinetest md5sums syntaxcheck
.PHONY: homepage upload doc tar debug ndebug
