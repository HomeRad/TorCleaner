SUBDIRS = devel misc

RESTFILES = $(wildcard *.txt)
HTMLFILES = $(patsubst %.txt, %.html, $(RESTFILES) )
NAVFILES = $(patsubst %.txt, %.nav, $(RESTFILES) )
DOCDIR = $(top_builddir)/doc
HTMLDIR := /home/calvin/public_html/webcleaner.sf.net

htmldir = $(prefix)/html
html_DATA = $(HTMLFILES)

EXTRA_DIST = $(RESTFILES) \
$(HTMLFILES) \
$(wildcard *.css) \
$(wildcard *.png) \
$(wildcard *.jpg)

%.html: %.txt htmlnav.py bfknav.py
	$(DOCDIR)/rest2htmlnav --stylesheet-path=wc.css --time $< $@

nav: all
	python $(DOCDIR)/bfknav.py

homepage: nav
	cp *.html *.css *.jpg *.png *.ico $(HTMLDIR)/htdocs
	cp devel/*.html $(HTMLDIR)/htdocs/devel
	cp misc/*.html $(HTMLDIR)/htdocs/misc
	cp -r devel/api $(HTMLDIR)/htdocs/devel

