SUBDIRS = libjs service po
DIST_SUBDIRS = $(SUBDIRS) doc
EXTRA_DIST = wc/tests \
	wc/dns/tests \
	wc/filter/tests \
	wc/proxy/tests \
	wc/proxy/auth/tests \
	wc/magic/tests

# python settings
PYVER := 2.4
PYTHON := python$(PYVER)
# homepage directory
HTMLDIR := /home/calvin/public_html/webcleaner.sf.net
# source code checker settings
SPLINTOPTS := +posixlib \
              -Iwc/HtmlParser -Ilibjs -I/usr/include/$(PYTHON) \
	      -nestcomment -ifempty
PYCHECKER := env PYTHONVER=$(PYVER) pychecker
PYCHECKEROPTS := -F test/pycheckrc
PYLINT := env PYTHONPATH=. PYLINTRC=config/pylintrc pylint.$(PYTHON)
PYLINTOPTS :=
PYFILES = $(wildcard wc/*.py wc/filter/*.py wc/filter/rules/*.py \
        wc/filter/rating/*.py wc/js/*.py wc/proxy/*.py wc/proxy/decoder/*.py \
	wc/proxy/auth/*.py wc/webgui/*.py wc/dns/*.py wc/http/*.py \
	wc/webgui/context/*.py wc/magic/*.py)
PYLINTIGNORE = wc/win32start.py
PYLINTFILES = $(filter-out $(PYLINTIGNORE),$(PYFILES))
PYFLAKES:=pyflakes
# test files
TESTFILES := test/*.py
# "runit" service directory
SERVICEDIR := /etc/webcleaner/service
# run unittests on check
TESTS = scripts/test.sh
# Debian settings
DEB_GPG_KEY:=2DE589F5

MANIFEST: MANIFEST.in setup.py
	rm -f share
	$(PYTHON) setup.py sdist --manifest-only

clean-local: clean-log
# ignore errors for python clean
	-$(PYTHON) setup.py clean --all
	rm -f wc/HtmlParser/htmlsax.so wc/js/jslib.so wc/levenshtein.so
	find . -name '*.py[co]' | xargs rm -f
	rm -f index.html* test.gif
	rm -f config/magic.mime.mgc
	rm -f _webcleaner2_configdata.py
	rm -f crossbuild.log localbuild.log
# delete possible aborted dist build
	rm -rf webcleaner-$(VERSION)

.PHONY: cvsclean
cvsclean:
	find . -name \.\#\* -exec rm -f {} \;

.PHONY: clean-log
clean-log:
	rm -f webcleaner*.log* webcleaner.err*

# to build in the current directory
.PHONY: localbuild
localbuild: MANIFEST all
	$(MAKE) -C wc/HtmlParser
	$(PYTHON) setup.py build
	ln -sf build/share share
	cp -f build/lib.linux-i686-$(PYVER)/wc/HtmlParser/htmlsax.so wc/HtmlParser/
	cp -f build/lib.linux-i686-$(PYVER)/wc/levenshtein.so wc/
	cp -f build/lib.linux-i686-$(PYVER)/wc/js/jslib.so wc/js/

.PHONY: crossdist
crossdist: distclean
	./crossbuild.sh

# cross compilation Linux -> Win32 script
.PHONY: crossbuild
crossbuild: all MANIFEST
# build the .exe
	CC=/usr/bin/i586-mingw32msvc-gcc \
	CCSHARED=/usr/bin/i586-mingw32msvc-gcc \
	  CXX=/usr/bin/i586-mingw32msvc-g++ \
	  LDSHARED="/usr/bin/i586-mingw32msvc-gcc --entry _DllMain@12" \
	  PY_HOST_PLATFORM=nt \
	  $(PYTHON) setup.py build -c mingw32 bdist_wininst -b tacho.bmp \
	  2>&1 | tee --append crossbuild.log

distclean-local:
	rm -rf dist build
	rm -f share
	rm -f webcleaner-$(VERSION).tar.gz
	rm -f webcleaner-$(VERSION).tar.gz.asc
	rm -f MANIFEST _*_configdata.*

# add upstream release tag
.PHONY: tag_upstream
tag_upstream:
	cvs tag upstream_version_$(subst .,_,$(VERSION))

# add debian release tag
.PHONY: tag_debian
tag_debian:
	cvs tag debian_version_$(subst .,_,$(shell dpkg-parsechangelog | grep -e "^Version:" | cut -f2 -d" "))

# ready for upload, signed with my GPG key
.PHONY: deb_signed
deb_signed: clean
	env CVSROOT=:ext:calvin@cvs.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/home/calvin/projects/cvs-build -Mwebcleaner2 -sgpg -pgpg -k$(DEB_GPG_KEY) -r"fakeroot --" -I.cvsignore

# add setup.py generated files to $(distdir)
# note: debian/rules install generates broken links, so delete debian
# package dirs before running sdist
dist-hook: MANIFEST
	rm -rf debian/webcleaner debian/webcleanertools
	$(PYTHON) setup.py sdist --keep-temp --dist-dir=$(distdir) --formats=gztar
	rm -f $(distdir)/webcleaner-$(VERSION).tar.gz
	rm -f $(distdir)/_webcleaner2_configdata.py

.PHONY: md5sums
md5sums:
	(cd config && md5sum *.zap > filter-md5sums.txt)
	(cd config && md5sum blacklists/{ads,aggressive,violence}/*.gz > extern-md5sums.txt)

.PHONY: releasecheck
releasecheck:
	@if egrep -i "xx\.|xxxx|\.xx" ChangeLog > /dev/null; then \
	  echo "Could not release: edit ChangeLog release date"; false; \
	fi
	@if ! grep 'adminuser="admin"' config/webcleaner.conf > /dev/null; then \
	  echo "Could not release: add admin user to config"; false; \
	fi

.PHONY: release
release: releasecheck clean dist sign_distfiles homepage
	@echo "Starting releaseforge..."
	@releaseforge
	@echo "Uploading new WebCleaner Homepage..."
	$(MAKE) -C ~/public_html/webcleaner.sf.net upload
	@echo "Register at Python Package Index..."
	$(PYTHON) setup.py register

.PHONY: sign_distfiles
sign_distfiles:
	for f in `ls webcleaner-$(VERSION).tar.gz webcleaner*.exe`; do \
	  if [ ! -f $${f}.asc ]; then \
	    gpg --detach-sign --armor $$f; \
	  fi; \
	done

.PHONY: homepage
homepage: homepage-zapper
	$(MAKE) -C doc/en homepage

.PHONY: homepage-zapper
homepage-zapper: md5sums
	cp config/*.zap config/*.dtd config/filter-md5sums.txt config/extern-md5sums.txt $(HTMLDIR)/htdocs/filter/
	@for d in ads aggressive violence; do \
	  cp config/blacklists/$$d/*.gz $(HTMLDIR)/htdocs/filter/blacklists/$$d/; \
	done

.PHONY: pycheck
pycheck: localbuild
	$(PYCHECKER) $(PYCHECKEROPTS) $(PYFILES) $(TESTFILES)

.PHONY: pylint
pylint: localbuild
	$(PYLINT) $(PYLINTOPTS) $(PYLINTFILES) $(TESTFILES)

.PHONY: pyflakes
pyflakes:
	$(PYFLAKES) *.py test wc config | \
	  grep -v "redefinition of unused 'wc'" | \
	  grep -v "undefined name '_'"

.PHONY: ccheck
ccheck:
	-splint $(SPLINTOPTS) wc/js/jslib.c

.PHONY: installservice
installservice:
	install -d $(SERVICEDIR)/log
	install -m 0755 service/webcleaner/run2 $(SERVICEDIR)/run
	install -m 0755 service/webcleaner/log/run $(SERVICEDIR)/log/
	if [ ! -e /var/service/webcleaner ]; then \
          ln -s /etc/webcleaner/service /var/service/webcleaner; \
	fi

test/test.sh:	localbuild

# (re)generate webcleaner blacklists
.PHONY: update-blacklists
update-blacklists:
	test/run.sh config/bl2wc.py

.PHONY: reindent
reindent:
	$(PYTHON) config/reindent.py -r -v wc

.PHONY: debug
debug:
	@for f in `find wc -name \*.py  | grep -v "tests/"`; do \
	    echo $$f; \
	    sed -i "s/assert not wc\.log\.debug/wc.log.debug/" $$f; \
	done


.PHONY: ndebug
ndebug:
	@for f in `find wc -name \*.py  | grep -v "tests/"`; do \
	    echo $$f; \
	    sed -i 's/wc\.log\.debug/assert not wc.log.debug/' $$f; \
	done

