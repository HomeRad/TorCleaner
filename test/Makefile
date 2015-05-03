# we use the scripts in Tools/i18n of the Python 2.3 distribution
PYTHON := python2.3
I18NTOOLS := ../po
GETTEXT := $(PYTHON) $(I18NTOOLS)/pygettext.py
MSGFMT := $(PYTHON) $(I18NTOOLS)/msgfmt.py
#MSGFMT=msgfmt
MSGMERGE := msgmerge
SOURCES = html/taltest.html test_simpletal.py

LDIR := $(CURDIR)/share/locale
PACKAGE=webcleaner
LFILE = LC_MESSAGES/$(PACKAGE).mo
# defined language (add new languages here)
LANGUAGES=de
MOS=$(patsubst %, %.mo, $(LANGUAGES) )

all:	$(MOS)

%.po:	pot-stamp
	$(MSGMERGE) $@ $(PACKAGE).pot -o $@

pot-stamp: $(SOURCES)
	rm -f $(PACKAGE).pot
	$(GETTEXT) --default-domain=$(PACKAGE) --no-location $(SOURCES)
	touch pot-stamp

%.mo:	%.po
	if [ ! -d $(LDIR)/$*/LC_MESSAGES ]; then \
	  mkdir -p $(LDIR)/$*/LC_MESSAGES; \
	fi
	$(MSGFMT) -o$(LDIR)/$*/$(LFILE) $<

clean:
	for f in $(LANGUAGES); do rm -f $(LDIR)/$$f/$(LFILE); done

distclean:	clean
	rm -f pot-stamp

.PHONY: all clean distclean
