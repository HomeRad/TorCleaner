RESTFILES = $(wildcard *.txt)
HTMLFILES = $(patsubst %.txt, %.html, $(RESTFILES) )
DOCDIR = $(top_builddir)/docs

htmldir = $(prefix)/html
html_DATA = $(HTMLFILES)

EXTRA_DIST = $(RESTFILES)

%.html: %.txt ../htmlnav.py ../bfknav.py
	-$(DOCDIR)/rest2htmlnav --stylesheet-path=../wc.css --time $< $@

