SUBDIRS 		= libjs

PYVER := 2.3
PYTHON := python$(PYVER)
WCVERSION := $(shell $(PYTHON) setup.py --version)
WCPACKAGE := webcleaner
#GROUPDIR := shell1.sourceforge.net:/home/groups
#HTMLDIR := $(GROUPDIR)/w/we/$(WCPACKAGE)/htdocs
HTMLDIR := /home/calvin/public_html/webcleaner.sf.net/htdocs
MD5SUMS := $(WCPACKAGE)-md5sums.txt
SPLINTOPTS := +posixlib \
              -Iwc/parser -I/usr/include/$(PYTHON) \
	      -nestcomment -ifempty


clean-local:
	-$(PYTHON) setup.py clean --all #  ignore errors for this command
	$(MAKE) -C po clean
	rm -f wc/parser/htmlsax.so wc/js/jslib.so wc/levenshtein.so
	find . -name '*.py[co]' | xargs rm -f
	rm -f index.html* test.gif

# to build in the current directory
localbuild: all
	$(PYTHON) setup.py build
	cp -f build/lib.linux-i686-$(PYVER)/wc/parser/htmlsax.so wc/parser/
	cp -f build/lib.linux-i686-$(PYVER)/wc/levenshtein.so wc/
	cp -f build/lib.linux-i686-$(PYVER)/wc/js/jslib.so wc/js/ || true

localtest:
	cd wc/parser && python htmllib.py

distclean-local:
	rm -rf dist build # just to be sure: clean build dir too
	rm -f VERSION MANIFEST _*_configdata.*

# ready for upload, signed with my GPG key
deb_signed: clean locale
	env CVSROOT=:ext:calvin@cvs.webcleaner.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/home/calvin/projects/cvs-build -Mwebcleaner2 -sgpg -pgpg -k32EC6F3E -rfakeroot

# add setup.py generated files to $(distdir)
# note: debian/rules install generates broken links, so delete debian
# package dirs before running sdist
dist-hook:	locale
	rm -rf debian/webcleaner debian/webcleanertools
	$(PYTHON) setup.py sdist --keep-temp --dist-dir=$(distdir) --formats=gztar
	rm -f $(distdir)/webcleaner-$(WCVERSION).tar.gz
	rm -f $(MD5SUMS)

mytest:
	env http_proxy="" ftp_proxy="" LANG=C $(PYTHON) test/regrtest.py

gentest:
	$(PYTHON) test/regrtest.py -g

restart:
	$(PYTHON) webcleaner restart
	rm -f index.html* test.gif
	sleep 4

authtest: restart
	env http_proxy="http://localhost:8080" wget -S --proxy-user=wummel --proxy-pass=wummel -t1 http://www.heise.de/


# filter and parse random data
randomtest:
	@echo "parse random data..."
	head -c 20000 /dev/random | $(PYTHON) test/parsefile.py - > /dev/null
	@echo "done."
	@echo "filter random data..."
	head -c 20000 /dev/random | $(PYTHON) test/filterfile.py - > /dev/null
	@echo "done."


#env http_proxy="http://localhost:8080" wget -S -t1 http://www.heise.de/advert/
#env http_proxy="http://localhost:8080" wget -S -t1 http://www.heise.de/advert/test.gif
onlinetest: restart
	env http_proxy="http://localhost:8080" wget -S -t1 http://www.heise.de/
	less index.html

offlinetest: restart
	env http_proxy="http://localhost:8080" wget -S -t1 http://localhost:8080/
	cat index.html
	rm -f index.html

md5sums:
	cd config && md5sum *.zap | bzip2 > md5sums.bz2
	for f in webcleaner-$(WCVERSION).tar.gz; do \
	  if [ ! -f $$f ]; then break; fi; \
	  md5sum $$f > $(MD5SUMS); \
	  gpg --detach-sign --armor $$f; \
	done

package:
	cd dist && dpkg-scanpackages . ../override.txt | gzip --best > Packages.gz

VERSION:
	echo $(WCVERSION) > VERSION

filterfiles:	md5sums
	cp config/*.zap config/*.dtd config/*.conf config/md5sums.bz2 $(HTMLDIR)/zapper
	cp config/filter.dtd $(HTMLDIR)/filter.dtd.txt
	cp config/adverts.zap $(HTMLDIR)/adverts.zap.txt

upload:
	ncftpput upload.sourceforge.net /incoming webcleaner-$(WCVERSION).tar.gz

homepage: VERSION
	cp ChangeLog $(HTMLDIR)/changes.txt
	cp README $(HTMLDIR)/readme.txt
	cp VERSION $(HTMLDIR)/raw/
	cp $(MD5SUMS) $(HTMLDIR)/

locale:
	$(MAKE) -C po

doc:
	rm -f README
	pydoc2 ./webcleaner > README

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

splint:
	rm -f splint.txt; splint $(SPLINTOPTS) wc/parser/htmllex.c > splint.txt

# (re)generate webcleaner rules
update-blacklists:
	$(PYTHON) config/bl2wc.py


.PHONY: localbuild locale distclean deb_signed update-blacklists
.PHONY: gentest onlinetest offlinetest md5sums package splint
.PHONY: filterfiles upload doc tar debug ndebug

