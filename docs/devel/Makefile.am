RESTFILES = $(wildcard *.txt)
DOCDIR = $(top_builddir)/docs

htmldir = $(prefix)/html
html_DATA = $(patsubst %.txt, %.html, $(RESTFILES) )

%.html: %.txt ../htmlnav.py ../bfknav.py
	$(DOCDIR)/rest2htmlnav --stylesheet-path=../wc.css --time --source-link $< $@

apidocs:
	epydoc --html -o api --name WebCleaner --url ../../../index.html ../../wc/

clean-local:
	rm -f *.html *.nav
