SUBDIRS 		= po libjs

PYVER := 2.3
PYTHON := python$(PYVER)
WCVERSION := $(shell $(PYTHON) setup.py --version)
HTMLDIR := /home/calvin/public_html/webcleaner.sf.net
SPLINTOPTS := +posixlib \
              -Iwc/parser -Ilibjs -I/usr/include/$(PYTHON) \
	      -nestcomment -ifempty
PYCHECKEROPTS := -F pycheckrc
PYCHECKERFILES := wc/*.py wc/filter/*.py wc/filter/rules/*.py wc/js/*.py \
                  wc/parser/*.py wc/proxy/*.py wc/proxy/auth/*.py \
		  wc/webgui/*.py wc/webgui/context/*.py \
		  wc/webgui/simpletal/*.py

clean-local:
	-$(PYTHON) setup.py clean --all #  ignore errors for this command
	rm -f wc/parser/htmlsax.so wc/js/jslib.so wc/levenshtein.so
	find . -name '*.py[co]' | xargs rm -f
	rm -f index.html* test.gif
	rm -f webcleaner.log* webcleaner.err*

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
	rm -f $(distdir)/webcleaner-$(WCVERSION).tar.gz
	rm -f webcleaner-md5sums.txt

testwc:
	test/run.sh test/regrtest.py

testgen:
	test/run.sh test/regrtest.py -g

# filter and parse random data
testrandom:
	@echo "parse random data..."
	rm -f randomparse.txt
	head -c 20000 /dev/urandom | test/run.sh test/parsefile.py - > /dev/null 2> randomparse.txt
	@echo "done."
	rm -f randomfilter.txt
	@echo "filter random data..."
	head -c 20000 /dev/urandom | test/run.sh test/filterfile.py - > /dev/null 2> randomfilter.txt
	@echo "done."

testupdate:
	test/run.sh wc/update.py

md5sums:
	(cd config && md5sum *.zap > filter-md5sums.txt)
	(cd test/filter && md5sum *.zap > filter-md5sums.txt)
	for f in webcleaner-$(WCVERSION).tar.gz; do \
	  if [ ! -f $$f ]; then break; fi; \
	  md5sum $$f > webcleaner-md5sums.txt; \
	  gpg --detach-sign --armor $$f; \
	done
	(cd config && md5sum blacklists/{ads,aggressive,violence}/*.gz > extern-md5sums.txt)

VERSION:
	echo $(WCVERSION) > VERSION

upload:
	ncftpput upload.sourceforge.net /incoming webcleaner-$(WCVERSION).tar.gz

homepage: VERSION md5sums
	cp config/*.dtd config/webcleaner.conf config/filter-md5sums.txt config/extern-md5sums.txt $(HTMLDIR)/htdocs/zapper
	cp test/filter/filter-md5sums.txt config/extern-md5sums.txt $(HTMLDIR)/htdocs/test
	(cd config && for f in *.zap; do \
	    cat $$f | gzip --best > $(HTMLDIR)/htdocs/zapper/$${f}.gz; \
	done)
	(cd test/filter && for f in *.zap; do \
	    cat $$f | gzip --best > $(HTMLDIR)/htdocs/test/$${f}.gz; \
	done)
	cp -r config/blacklists/ $(HTMLDIR)/htdocs/zapper
	cp config/filter.dtd $(HTMLDIR)/htdocs/filter.dtd.txt
	cp config/adverts.zap $(HTMLDIR)/htdocs/adverts.zap.txt
	cp ChangeLog $(HTMLDIR)/htdocs/changes.txt
	cp README $(HTMLDIR)/htdocs/readme.txt
	cp VERSION $(HTMLDIR)/htdocs/raw/
	-cp webcleaner-md5sums.txt $(HTMLDIR)/htdocs/
	$(MAKE) -C $(HTMLDIR) chmod

doc:
	rm -f README
	pydoc$(PYVER) ./webcleaner > README

debug:
	@for f in `find . -name \*.py`; do \
	  cat $$f | sed 's/#self._debug(/self._debug(/' > $$f.bak; \
	  mv -f $$f.bak $$f; \
	done

ndebug:
	@for f in `find . -name \*.py`; do \
	  cat $$f | sed 's/self._debug(/#self._debug(/' > $$f.bak; \
	  mv -f $$f.bak $$f; \
	done

pycheck:
	-env PYTHONVER=2.3 pychecker $(PYCHECKEROPTS) $(PYCHECKERFILES)

ccheck:
	-splint $(SPLINTOPTS) wc/js/jslib.c

# (re)generate webcleaner rules
update-blacklists:
	$(PYTHON) config/bl2wc.py


.PHONY: localbuild distclean deb_signed update-blacklists
.PHONY: gentest onlinetest offlinetest md5sums syntaxcheck
.PHONY: homepage upload doc tar debug ndebug
