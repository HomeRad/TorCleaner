# use scripts found in Tools/i18n of the Python distribution
PYTHON := python2.3
GETTEXT := $(PYTHON) pygettext.py -k bk.i18n._
#MSGFMT := $(PYTHON) msgfmt.py
MSGFMT := @MSGFMT@ -c
MSGMERGE := @MSGMERGE@
POSOURCES = $(shell find ../wc -name \*.py) \
	$(shell find ../bk -name \*.py) \
	../webcleaner ../webcleaner-service ../webcleaner-certificates \
	$(shell find ../templates -name \*.html)

LDIR = ../share/locale
PACKAGE = webcleaner
LFILE = LC_MESSAGES/$(PACKAGE).mo
# defined language (add new languages here)
LANGUAGES = de
MOS = $(patsubst %, %.mo, $(LANGUAGES) )

all:	$(MOS)

%.po:	webcleaner.pot
	$(MSGMERGE) $@ $(PACKAGE).pot -o $@

webcleaner.pot: $(POSOURCES)
if BUILD_WINDOWS
else
	$(GETTEXT) --default-domain=$(PACKAGE) --no-location $(POSOURCES)
endif

%.mo:	%.po
	if [ ! -d $(LDIR)/$*/LC_MESSAGES ]; then \
	  mkdir -p $(LDIR)/$*/LC_MESSAGES; \
	fi
	$(MSGFMT) -o $(LDIR)/$*/$(LFILE) $<

clean-local:
	for f in $(LANGUAGES); do rm -f $(LDIR)/$$f/$(LFILE); done
	rm -f *.mo
