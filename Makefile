# This Makefile is only used by developers! 
# There is no need for users to call make.
PYVER=2.2
PYTHON=python$(PYVER)
VERSION=$(shell $(PYTHON) setup.py --version)
PACKAGE=webcleaner
#GROUPDIR=shell1.sourceforge.net:/home/groups
#HTMLDIR=$(GROUPDIR)/w/we/$(PACKAGE)/htdocs
HTMLDIR=/home/calvin/public_html/webcleaner.sf.net/htdocs
MD5SUMS=$(PACKAGE)-md5sums.txt
SPLINTOPTS := +posixlib \
              -Iwc/parser -I/usr/include/python2.2 \
	      -nestcomment -ifempty


all:
	@echo "Read the file INSTALL to see how to build and install"

clean:
	-$(PYTHON) setup.py clean --all #  ignore errors for this command
	$(MAKE) -C po clean
	rm -f wc/parser/htmlsax.so wc/js/jslib.so
	find . -name '*.py[co]' | xargs rm -f
	rm -f index.html* test.gif

# to build in the current directory
localbuild:
	$(MAKE) -C wc/parser
	$(PYTHON) setup.py build
	cp -f build/lib.linux-i686-$(PYVER)/wc/parser/htmlsax.so wc/parser/
	cp -f build/lib.linux-i686-$(PYVER)/wc/levenshtein.so wc/
	cp -f build/lib.linux-i686-$(PYVER)/wc/js/jslib.so wc/js/ || true

localtest:
	cd wc/parser && python htmllib.py

distclean:	clean cleandeb
	rm -rf dist build # just to be sure: clean build dir too
	rm -f VERSION MANIFEST _*_configdata.*

cleandeb:
	rm -rf debian/$(PACKAGE) debian/$(PACKAGE)conf debian/tmp
	rm -f debian/*.debhelper debian/{files,substvars}
	rm -f configure-stamp build-stamp

# produce the .deb Debian package
deb_local: distclean locale
	fakeroot debian/rules binary

deb_localsigned: distclean locale
	debuild -sgpg -pgpg -k32EC6F3E -rfakeroot

# ready for upload, signed with my GPG key
deb_signed: distclean locale
	env CVSROOT=:pserver:anonymous@cvs.webcleaner.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/home/calvin/projects/cvs-build -Mwebcleaner2 -sgpg -pgpg -k32EC6F3E -rfakeroot

# same thing, but unsigned (for local archives)
deb_unsigned: distclean locale
	env CVSROOT=:pserver:anonymous@cvs.webcleaner.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/usr/local/src/debian -Mwebcleaner2 -us -uc -rfakeroot

dist:	locale
	$(PYTHON) setup.py sdist --formats=gztar,zip
	rm -f $(MD5SUMS)
	md5sum dist/* > $(MD5SUMS)
	for f in dist/*; do gpg --detach-sign --armor $$f; done

test:
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
	env http_proxy="http://localhost:9090" wget -S -t1 http://localhost:9090/
	cat index.html
	rm -f index.html

md5sums:
	cd config && md5sum *.zap > md5sums

package:
	cd dist && dpkg-scanpackages . ../override.txt | gzip --best > Packages.gz

VERSION:
	echo $(VERSION) > VERSION

filterfiles:	md5sums
	cp config/*.zap config/*.dtd config/*.conf config/md5sums $(HTMLDIR)/zapper
	cp config/filter.dtd $(HTMLDIR)/filter.dtd.txt
	cp config/adverts.zap $(HTMLDIR)/adverts.zap.txt

upload: distclean dist homepage
	ncftpput upload.sourceforge.net /incoming dist/*

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

tar:	distclean
	cd .. && tar cjvf webcleaner.tar.bz2 webcleaner2

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


.PHONY: all clean localbuild distclean cleandeb deb_local deb_signed 
.PHONY: deb_unsigned dist test gentest onlinetest offlinetest md5sums package
.PHONY: filterfiles upload doc tar debug ndebug
