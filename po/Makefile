# we use the scripts in Tools/i18n of the Python 2.0 distribution
I18NTOOLS=.
PYTHON=python2
GETTEXT=$(PYTHON) $(I18NTOOLS)/pygettext.py
MSGFMT=$(PYTHON) $(I18NTOOLS)/msgfmt.py
MSGMERGE=msgmerge
SOURCES=\
../webcleaner \
../webcleanerconf
TARGETS=de.mo
PACKAGE=webcleaner

all:
	$(MAKE) $(TARGETS)

%.po:	.time.pot
	$(MSGMERGE) $@ $(PACKAGE).pot -o $@

.time.pot:
	rm -f $(PACKAGE).pot
	$(GETTEXT) --default-domain=$(PACKAGE) --no-location $(SOURCES)
	touch .time.pot

%.mo:	%.po
	$(MSGFMT) $< && mkdir -p ../locale/$*/LC_MESSAGES && mv $@ ../locale/$*/LC_MESSAGES/$(PACKAGE).mo

clean:
	rm -f .time.pot
	rm -rf ../locale
