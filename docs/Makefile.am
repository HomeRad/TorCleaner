SUBDIRS = devel misc

RESTFILES = $(wildcard *.txt)
DOCDIR = $(top_builddir)/docs

htmldir = $(prefix)/html
html_DATA = $(patsubst %.txt, %.html, $(RESTFILES) )

%.html: %.txt htmlnav.py bfknav.py
	$(DOCDIR)/rest2htmlnav --stylesheet-path=wc.css --time --source-link $< $@

nav: $(html_DATA)
	python bfknav.py

clean-local:
	rm -f *.html *.nav
