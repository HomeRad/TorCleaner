# This Makefile is only used by developers! 
# There is no need for users to call make.
PYTHON=python2.1
VERSION=$(shell $(PYTHON) setup.py --version)
PACKAGE=webcleaner
GROUPDIR=shell1.sourceforge.net:/home/groups
HTMLDIR=$(GROUPDIR)/w/we/$(PACKAGE)/htdocs

all:
	@echo "Read the file INSTALL to see how to build and install"

clean:
	-$(PYTHON) setup.py clean --all #  ignore errors for this command
	$(MAKE) -C po clean
	$(MAKE) -C wc/parser clean
	find . -name '*.py[co]' | xargs rm -f
	rm -f index.html* test.gif

# to build in the current directory (assumes python 2.1)
localbuild:
	$(MAKE) -C wc/parser
	$(PYTHON) setup.py build
	cp -f build/lib.linux-i686-2.1/wc/parser/htmlsax.so wc/parser

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
deb_local:	locale
	# standard for local use
	fakeroot debian/rules binary

deb_localsigned:
	debuild -sgpg -pgpg -k32EC6F3E -rfakeroot

deb_signed:	locale
	# ready for upload, signed with my GPG key
	env CVSROOT=:pserver:anonymous@cvs.webcleaner.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/home/calvin/projects/cvs-build -Mwebcleaner2 -sgpg -pgpg -k32EC6F3E -rfakeroot

deb_unsigned:	locale
	# same thing, but unsigned (for local archives)
	env CVSROOT=:pserver:anonymous@cvs.webcleaner.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/usr/local/src/debian -Mwebcleaner2 -us -uc -rfakeroot

dist:	locale
	$(PYTHON) setup.py sdist --formats=gztar,zip

test:
	$(PYTHON) test/regrtest.py

gentest:
	$(PYTHON) test/regrtest.py -g

restart:
	$(PYTHON) webcleaner restart
	rm -f index.html* test.gif
	sleep 4

authtest: restart
	env http_proxy="http://localhost:9090" wget -S --proxy-user=wummel --proxy-pass=wummel -t1 http://www.heise.de/

onlinetest: restart
	# get a standard page with included adverts
	env http_proxy="http://localhost:9090" wget -S -t1 http://www.heise.de/
	# get a blocked page
	env http_proxy="http://localhost:9090" wget -S -t1 http://www.heise.de/advert/
	# get a blocked image
	env http_proxy="http://localhost:9090" wget -S -t1 http://www.heise.de/advert/test.gif

offlinetest: restart
	# get own config
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
	scp config/*.zap config/*.dtd config/*.conf config/md5sums $(HTMLDIR)/zapper
	scp config/filter.dtd $(HTMLDIR)/filter.dtd.txt
	scp config/adverts.zap $(HTMLDIR)/adverts.zap.txt

upload: distclean dist VERSION
	scp debian/changelog $(HTMLDIR)/changes.txt
	scp VERSION $(HTMLDIR)/raw/
	#scp dist/* $(HTMLDIR)
	ncftpput upload.sourceforge.net /incoming dist/* && read -p "Make new SF file releases and then press Enter:"
	ssh -C -t shell1.sourceforge.net "cd /home/groups/w/we/$(PACKAGE) && make"

locale:
	$(MAKE) -C po

doc:
	rm -f README
	pydoc2 ./webcleaner > README

tar:	distclean
	cd .. && tar cjvf webcleaner.tar.bz2 webcleaner2

debug:
	@for f in `find . -name \*.py`; do \
	  cat $$f | sed 's/#debug(/debug(/' > $$f.bak; \
	  mv -f $$f.bak $$f; \
	done

ndebug:
	@for f in `find . -name \*.py`; do \
	  cat $$f | sed 's/debug(/#debug(/' > $$f.bak; \
	  mv -f $$f.bak $$f; \
	done

.PHONY: all clean localbuild distclean cleandeb deb_local deb_signed 
.PHONY: deb_unsigned dist test gentest onlinetest offlinetest md5sums package
.PHONY: filterfiles upload doc tar debug ndebug
