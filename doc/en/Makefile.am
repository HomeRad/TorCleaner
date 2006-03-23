SUBDIRS = devel misc

RESTFILES = $(wildcard *.txt)
HTMLFILES = $(patsubst %.txt, %.html, $(RESTFILES) )
NAVFILES = $(patsubst %.txt, %.nav, $(RESTFILES) )
DOCDIR = $(top_builddir)/doc
HTMLDIR := /home/calvin/public_html/webcleaner.sf.net

htmldir = $(prefix)/html
html_DATA = $(HTMLFILES)

EXTRA_DIST = $(RESTFILES) \
$(wildcard *.css) \
$(wildcard *.png) \
$(wildcard *.jpg) \
$(wildcard *.ico)

%.html: %.txt ../htmlnav.py ../bfknav.py
	$(DOCDIR)/rest2htmlnav --stylesheet-path=wc.css --time $< $@

nav: all
	python $(DOCDIR)/bfknav.py

homepage: nav test
	cp *.html *.css *.jpg *.png *.ico $(HTMLDIR)/htdocs
	cp devel/*.html $(HTMLDIR)/htdocs/devel
	cp misc/*.html $(HTMLDIR)/htdocs/misc

.PHONY: test
test:
	xmllint --valid --noout *.html
