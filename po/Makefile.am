# we use the scripts in Tools/i18n of the Python 2.3 distribution
PYTHON := python2.3
I18NTOOLS := .
GETTEXT := $(PYTHON) $(I18NTOOLS)/pygettext.py -k i18n._
#MSGFMT := $(PYTHON) $(I18NTOOLS)/msgfmt.py
MSGFMT := msgfmt -c
MSGMERGE := msgmerge
SOURCES = $(shell find ../wc -name \*.py) \
../wcheaders \
../webcleaner \
../webcleanerconf \
$(shell find ../templates -name \*.html)

LDIR=../share/locale
PACKAGE=webcleaner
LFILE=LC_MESSAGES/$(PACKAGE).mo
# defined language (add new languages here)
LANGUAGES=de
MOS=$(patsubst %, %.mo, $(LANGUAGES) )

all:	$(MOS)

%.po:	webcleaner.pot
	$(MSGMERGE) $@ $(PACKAGE).pot -o $@

webcleaner.pot: $(SOURCES)
	$(GETTEXT) --default-domain=$(PACKAGE) --no-location $(SOURCES)

%.mo:	%.po
	if [ ! -d $(LDIR)/$*/LC_MESSAGES ]; then \
	  mkdir -p $(LDIR)/$*/LC_MESSAGES; \
	fi
	$(MSGFMT) -o$(LDIR)/$*/$(LFILE) $<

clean-local:
	for f in $(LANGUAGES); do rm -f $(LDIR)/$$f/$(LFILE); done
