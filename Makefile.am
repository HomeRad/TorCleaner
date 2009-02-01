SUBDIRS = libjs service po
DIST_SUBDIRS = $(SUBDIRS) doc
EXTRA_DIST = tests scripts \
	wc/tests \
	wc/http/tests \
	wc/dns/tests \
	wc/filter/tests \
	wc/proxy/tests \
	wc/proxy/auth/tests \
	wc/magic/tests \
	wc/rating/tests
MACHINE=$(shell uname -m)
# python settings
PYVER=2.5
PYTHON=python$(PYVER)
# homepage directory
HTMLDIR=/home/calvin/public_html/webcleaner.sf.net
# source code checker settings
SPLINTOPTS=+posixlib \
              -Iwc/HtmlParser -Ilibjs -I/usr/include/$(PYTHON) \
	      -nestcomment -ifempty
# all Python files in the source
PYFILES=webcleaner webcleaner-certificates *.py test/*.py config/*.py wc tests
CHECKFILES=*.py webcleaner webcleaner-certificates test tests wc config
# "runit" service directory
SERVICEDIR=/etc/webcleaner/service
# GPG key for .deb package
GPGKEY=2DE589F5
# build dir for svn-buildpackage
SVNBUILD=/home/calvin/src/build-area
DEB_ORIG_TARGET=$(SVNBUILD)/webcleaner_$(VERSION).orig.tar.gz

MANIFEST: setup.py
	rm -f share
	$(PYTHON) setup.py sdist --manifest-only

clean-local: clean-log
# ignore errors for python clean
	-$(PYTHON) setup.py clean --all
	rm -f wc/HtmlParser/htmlsax.so wc/js/jslib.so wc/levenshtein.so wc/network/_network.so
	find . -name '*.py[co]' | xargs rm -f
	rm -f index.html* test.gif
	rm -f config/magic.mime.mgc
	rm -f _webcleaner2_configdata.py
	rm -f crossbuild.log
	rm -rf coverage
	rm -rf *.prof
# delete possible aborted dist build
	rm -rf webcleaner-$(VERSION)

.PHONY: clean-log
clean-log:
	rm -f webcleaner*.log* webcleaner.err* psyco.log

# to build in the current directory
.PHONY: localbuild
localbuild: MANIFEST all
	$(MAKE) -C wc/HtmlParser
	$(PYTHON) setup.py build
	@if [ ! -e share ]; then ln -sf build/share share; fi
	cp -f build/lib.linux-$(MACHINE)-$(PYVER)/wc/HtmlParser/htmlsax.so wc/HtmlParser/
	cp -f build/lib.linux-$(MACHINE)-$(PYVER)/wc/levenshtein.so wc/
	cp -f build/lib.linux-$(MACHINE)-$(PYVER)/wc/js/jslib.so wc/js/
	cp -f build/lib.linux-$(MACHINE)-$(PYVER)/wc/network/_network.so wc/network/

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
	rm -f MANIFEST _*_configdata.* dist-stamp
	rm -rf autom4te.cache

dist-stamp: dist
	touch $@

.PHONY: deb_orig
deb_orig:
	if [ ! -e $(DEB_ORIG_TARGET) ]; then \
	  $(MAKE) dist-stamp && mv webcleaner-$(VERSION).tar.gz $(DEB_ORIG_TARGET) && rm -f dist-stamp; \
	fi

# ready for upload, signed with my GPG key
.PHONY: deb_signed
deb_signed: clean
	(env -u LANG svn-buildpackage --svn-dont-clean --svn-verbose \
	  --svn-ignore --svn-no-links \
	  --svn-prebuild="$(MAKE) deb_orig" --svn-lintian --svn-linda \
	  -sgpg -pgpg -k$(GPGKEY) -rfakeroot 2>&1) | \
	tee $(SVNBUILD)/webcleaner-$(VERSION).build

# add setup.py generated files to $(distdir)
# note: debian/rules install generates broken links, so delete debian
# package dirs before running sdist
dist-hook: MANIFEST
	rm -rf debian/webcleaner debian/webcleanertools
	$(PYTHON) setup.py sdist --prune --keep-temp --dist-dir=$(distdir) --formats=gztar
	rm -f $(distdir)/webcleaner-$(VERSION).tar.gz
	rm -f $(distdir)/_webcleaner2_configdata.py
	find $(distdir) -depth -name .svn -exec rm -rf {} \;

.PHONY: md5sums
md5sums:
	(cd config && md5sum *.zap > filter-md5sums.txt)
	(cd config && md5sum blacklists/{ads,aggressive,violence}/*.gz > extern-md5sums.txt)

.PHONY: syntaxcheck
syntaxcheck:
	py-verify -v
	py-find-nocoding -v
	check-nosvneolstyle -v
	check-copyright -v
	check-pofiles -v
	py24-tabnanny
	$(MAKE) -C config xmlcheck


.PHONY: releasecheck
releasecheck:	syntaxcheck
	@if egrep -i "xx\.|xxxx|\.xx" ChangeLog > /dev/null; then \
	  echo "Could not release: edit ChangeLog release date"; false; \
	fi
	@if ! grep 'adminuser="admin"' config/webcleaner.conf > /dev/null; then \
	  echo "Could not release: add admin user to config"; false; \
	fi

.PHONY: upload
upload:
	@echo "Starting releaseforge..."
	@releaseforge
#	ncftpput upload.sourceforge.net /incoming webcleaner-$(VERSION).tar.gz webcleaner-$(VERSION).tar.gz.asc
#	-ncftpput upload.sourceforge.net /incoming webcleaner-$(VERSION).win32-py2.4.exe webcleaner-$(VERSION).win32-py2.4.exe.asc
#	mozilla -remote "openUrl(https://sourceforge.net/projects/webcleaner, new-tab)"
#	@echo "Make SF release and press return..."
#	@read

.PHONY: release
release: releasecheck clean dist-stamp sign_distfiles homepage upload
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

.PHONY: pyflakes
pyflakes:
	pyflakes $(CHECKFILES) 2>&1 | \
	  grep -v "undefined name '_'" | \
	  grep -v "undefined name '_n'"

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

# (re)generate webcleaner blacklists
.PHONY: update-blacklists
update-blacklists:
	scripts/run.sh config/bl2wc.py

.PHONY: reindent
reindent:
	$(PYTHON) config/reindent.py -r -v wc

# various python check scripts
.PHONY: various
various:
	py-find-nocoding $(CHECKFILES)
	py-find-nosvneolstyle $(CHECKFILES)

.PHONY: test
test:	localbuild
	nosetests -m "^test_.*" tests/

JSSRCDIR=/home/calvin/src/mozilla-js-cvs
jsdiff:
	(cd libjs && for f in *.c *.h *.tbl *.msg \
	          fdlibm/*.h fdlibm/*.c; do \
	   diff -u $$f $(JSSRCDIR)/$$f 2>/dev/null; \
	 done) | less

jsupdate:
	cd libjs && for f in *.c *.h *.tbl *.msg \
                 fdlibm/*.h fdlibm/*.c; do \
	  if ! diff $$f $(JSSRCDIR)/$$f > /dev/null 2>&1; then \
	      if [ -e $(JSSRCDIR)/$$f ]; then \
	          /bin/cp -vf $(JSSRCDIR)/$$f $$f; \
	      fi; \
	  fi; \
	done
