# This Makefile is only used by developers! No need for users to
# call make.
VERSION=$(shell ./setup.py --version)
PACKAGE=webcleaner
GROUPDIR=shell1.sourceforge.net:/home/groups
HTMLDIR=$(GROUPDIR)/w/we/$(PACKAGE)/htdocs
FTPDIR=$(GROUPDIR)/ftp/pub/$(PACKAGE)/

.PHONY: all
all:
	@echo "Read the file INSTALL to see how to build and install"

.PHONY: clean
clean:
	-./setup.py clean --all #  ignore errors for this command
	$(MAKE) -C po clean
	find . -name '*.py[co]' | xargs rm -f
	rm -f index.html* test.gif

.PHONY: distclean
distclean:	clean cleandeb
	rm -rf dist build # just to be sure: clean build dir too
	rm -f VERSION MANIFEST _*_configdata.*

.PHONY: cleandeb
cleandeb:
	rm -rf debian/$(PACKAGE) debian/$(PACKAGE)conf debian/tmp
	rm -f debian/*.debhelper debian/{files,substvars}
	rm -f configure-stamp build-stamp

.PHONY: deb
deb:	locale
	debuild binary
	#env CVSROOT=:pserver:anonymous@cvs.webcleaner.sourceforge.net:/cvsroot/webcleaner cvs-buildpackage -W/home/calvin/projects/cvs-build -Mwebcleaner2 -sgpg -pgpg -k959C340F -rfakeroot


.PHONY: dist
dist:	locale
	./setup.py sdist --formats=gztar

# only visual test
.PHONY: test
test:
	./filtertest filter filtertest.html
	./filtertest block "GET http://ads.realmedia.com/ HTTP/1.0"

.PHONY: onlinetest
onlinetest:
	rm -f index.html* test.gif
	# get a standard page with included adverts
	env http_proxy="http://localhost:9090" wget -t1 http://www.heise.de/
	# get own config
	env http_proxy="http://localhost:9090" wget -t1 http://localhost:9090/
	# get a blocked site
	env http_proxy="http://localhost:9090" wget -t1 http://www.heise.de/advert/
	# get a blocked image
	env http_proxy="http://localhost:9090" wget -t1 http://www.heise.de/advert/test.gif

.PHONY: md5sums
md5sums:
	cd config && md5sum *.zap > md5sums

.PHONY: package
package:
	cd dist && dpkg-scanpackages . ../override.txt | gzip --best > Packages.gz

VERSION:
	echo $(VERSION) > VERSION

.PHONY: filterfiles
filterfiles:	md5sums
	scp config/*.zap config/*.dtd config/*.conf config/md5sums $(HTMLDIR)/zapper
	scp config/filter.dtd $(HTMLDIR)/filter.dtd.txt
	scp config/adverts.zap $(HTMLDIR)/adverts.zap.txt

.PHONY: upload
upload: distclean dist VERSION
	scp debian/changelog $(HTMLDIR)/changes.txt
	scp VERSION $(HTMLDIR)/raw/
	scp dist/*.tar.gz $(HTMLDIR)
	scp dist/* $(FTPDIR)
	ssh -C -t shell1.sourceforge.net "cd /home/groups/w/we/$(PACKAGE) && make"

.PHONY: locale
locale:
	$(MAKE) -C po

.PHONY: doc
doc:
	rm -f README
	pydoc2 ./webcleaner > README
