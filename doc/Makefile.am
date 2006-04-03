SUBDIRS = en de

EXTRA_DIST = rest2htmlnav $(wildcard *.py) po4a.conf webcleaner.doc.pot

.PHONY: apidocs
apidocs:
	epydoc --html -o api --name "WebCleaner Development" --url ../../devel.html ../wc/

.PHONY: po4a
po4a:
	po4a --localized-charset=ISO-8859-15 po4a.conf
