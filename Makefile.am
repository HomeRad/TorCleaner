SUBDIRS = po libjs service docs
TESTS = noop

PYVER := 2.3
PYTHON := python$(PYVER)
VERSION := $(shell python setup.py --version)
HTMLDIR := /home/calvin/public_html/webcleaner.sf.net
SPLINTOPTS := +posixlib \
              -Iwc/parser -Ilibjs -I/usr/include/$(PYTHON) \
	      -nestcomment -ifempty
PYCHECKEROPTS := -F pycheckrc
PYCHECKERFILES := wc/*.py wc/filter/*.py wc/filter/rules/*.py wc/js/*.py \
                  wc/parser/*.py wc/proxy/*.py wc/proxy/auth/*.py \
		  wc/proxy/dns/*.py \
		  wc/webgui/*.py wc/webgui/context/*.py \
		  wc/webgui/simpletal/*.py wc/magic/*.py
#		  test/*.py tests/*.py tests/server/*.py

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
	rm -f MANIFEST _*_configdata.*

# ready for upload, signed with my GPG key
deb_signed: clean
	env CVSROOT=:ext:calvin@cvs.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/home/calvin/projects/cvs-build -Mwebcleaner2 -sgpg -pgpg -k32EC6F3E -r"fakeroot --" -I.cvsignore

# add setup.py generated files to $(distdir)
# note: debian/rules install generates broken links, so delete debian
# package dirs before running sdist
dist-hook:
	rm -rf debian/webcleaner debian/webcleanertools
	$(PYTHON) setup.py sdist --keep-temp --dist-dir=$(distdir) --formats=gztar
	rm -f $(distdir)/webcleaner-$(VERSION).tar.gz
	rm -f $(distdir)/_webcleaner2_configdata.py
	rm -f webcleaner-md5sums.txt

# noop is a script doing nothing, to fool automake check routines
noop: localbuild
	test/run.sh tests/runall.py
	test/run.sh tests/runsimpletaltests.py

md5sums:
	(cd config && md5sum *.zap > filter-md5sums.txt)
	(cd test/filter && md5sum *.zap > filter-md5sums.txt)
	for f in webcleaner-$(VERSION).tar.gz; do \
	  if [ ! -f $$f ]; then break; fi; \
	  md5sum $$f > webcleaner-md5sums.txt; \
	  gpg --detach-sign --armor $$f; \
	done
	(cd config && md5sum blacklists/{ads,aggressive,violence}/*.gz > extern-md5sums.txt)

releasecheck:
	@if grep xxxx ChangeLog; then \
	  echo "Could not release: edit ChangeLog release date"; false; \
	fi

release: releasecheck dist upload homepage
	mozilla -remote "openUrl(http://sourceforge.net/projects/webcleaner, new-tab)"
	@echo "Make SF release and press return..."
	@read
	@echo "Uploading new WebCleaner Homepage..."
	make -C ~/public_html/webcleaner.sf.net upload

upload:
	ncftpput upload.sourceforge.net /incoming webcleaner-$(VERSION).tar.gz

homepage: homepage-zapper
	cp ChangeLog $(HTMLDIR)/htdocs/changes.txt
	-cp webcleaner-md5sums.txt $(HTMLDIR)/htdocs/
	$(MAKE) -C docs homepage
	$(MAKE) -C $(HTMLDIR) chmod

homepage-zapper: md5sums
	cp config/*.dtd config/webcleaner.conf config/filter-md5sums.txt config/extern-md5sums.txt $(HTMLDIR)/htdocs/filter
	cp config/*.zap $(HTMLDIR)/htdocs/filter/
	cp -r config/blacklists/ $(HTMLDIR)/htdocs/filter
	cp config/filter.dtd $(HTMLDIR)/htdocs/filter.dtd.txt
	cp config/adverts.zap $(HTMLDIR)/htdocs/adverts.zap.txt

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
	test/run.sh config/bl2wc.py


.PHONY: localbuild distclean deb_signed update-blacklists
.PHONY: md5sums pycheck ccheck installservice homepage upload doc
