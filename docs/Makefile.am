SUBDIRS = devel misc

RESTFILES = $(wildcard *.txt)
DOCDIR = $(top_builddir)/docs
HTMLDIR := /home/calvin/public_html/webcleaner.sf.net

htmldir = $(prefix)/html
html_DATA = $(patsubst %.txt, %.html, $(RESTFILES) )

%.html: %.txt htmlnav.py bfknav.py
	$(DOCDIR)/rest2htmlnav --stylesheet-path=wc.css --time $< $@

nav: all
	python bfknav.py

apidocs:
	epydoc --html -o devel/api --name "WebCleaner Development" --url ../../devel.html ../wc/ ../test ../tests

homepage: nav apidocs
	cp *.html *.css *.jpg *.png $(HTMLDIR)/htdocs
	cp devel/*.html $(HTMLDIR)/htdocs/devel
	cp misc/*.html $(HTMLDIR)/htdocs/misc
	cp -r devel/api $(HTMLDIR)/htdocs/devel

clean-local:
	rm -f *.html *.nav
