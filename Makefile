# This Makefile is only used by developers! No need for users to
# call make.
VERSION=$(shell ./setup.py --version)
PACKAGE=webcleaner
DEBS=$(PACKAGE)_$(VERSION)_i386.deb $(PACKAGE)conf_$(VERSION)_all.deb
HTMLDIR=shell1.sourceforge.net:/home/groups/$(PACKAGE)/htdocs
FTPDIR=shell1.sourceforge.net:/home/groups/ftp/pub/$(PACKAGE)/
.PHONY: all
all:
	@echo "Read the file INSTALL to see how to build and install"

.PHONY: clean
clean:
	-./setup.py clean --all #  ignore errors for this command
	$(MAKE) -C po clean
	find . -name '*.py[co]' | xargs rm -f

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
	# clean deb files because distutils chokes on broken symlinks
	# (webcleaner.1 -> undocumented.1)
	$(MAKE) cleandeb
	#fakeroot debian/rules binary
	fakeroot dpkg-buildpackage -sgpg -pgpg -k959C340F


.PHONY: dist
dist:	locale
	./setup.py sdist --formats=gztar,zip bdist_rpm
	# no cross compiler suitable
	#./setup.py bdist_wininst
	$(MAKE) cleandeb
	fakeroot debian/rules binary
	@for i in $(DEBS); do cp -f ../$$i dist; done

# only visual test
.PHONY: test
test:
	#./filtertest filter filtertest.html
	env http_proxy="http://localhost:9090" wget -t1 http://localhost/

.PHONY: test_remote
test_remote:
	env http_proxy="http://localhost:9090" wget -t1 http://freshmeat.net/

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
	scp config/*.zap config/*.dtd config/md5sums $(HTMLDIR)/zapper
	scp config/filter.dtd $(HTMLDIR)/filter.dtd.txt
	scp config/adverts.zap $(HTMLDIR)/adverts.zap.txt

.PHONY: upload
upload: distclean dist VERSION
	scp debian/changelog $(HTMLDIR)/changes.txt
	scp VERSION $(HTMLDIR)/raw/
	scp dist/*.tar.gz $(HTMLDIR)
	scp dist/* $(FTPDIR)
	ssh -C -t shell1.sourceforge.net "cd /home/groups/$(PACKAGE) && make"

.PHONY: locale
locale:
	$(MAKE) -C po

.PHONY: doc
doc:
	rm -f README
	pydoc2 ./webcleaner > README
