PYTHON = env PYTHONPATH=$(top_srcdir) python
XGETTEXT = @XGETTEXT@
MSGFMT = @MSGFMT@
MSGMERGE = @MSGMERGE@
TALGETTEXT = $(PYTHON) ../wc/webgui/TAL/talgettext.py
POSOURCES = $(shell find ../wc -name \*.py) \
	../webcleaner ../webcleaner-certificates
TEMPLATES = $(shell find ../templates -name \*.html)
LDIR = ../share/locale
PACKAGE = webcleaner
TEMPLATE = $(PACKAGE).pot
LFILE = LC_MESSAGES/$(PACKAGE).mo
# defined language (add new languages here)
LANGUAGES = de

mofiles:
	for la in $(LANGUAGES); do \
	  if [ ! -d $(LDIR)/$$la/LC_MESSAGES ]; then \
	    mkdir -p $(LDIR)/$$la/LC_MESSAGES; \
	  fi; \
          $(MSGFMT) -c --statistics -o $(LDIR)/$$la/$(LFILE) $$la.po; \
        done

%.po:	$(TEMPLATE)
	$(MSGMERGE) -U --suffix=.bak $@ $<

template: $(TEMPLATE)
$(TEMPLATE): $(POSOURCES)
	$(XGETTEXT) -w 80 --default-domain=$(PACKAGE) --language=Python \
	  --copyright-holder="Bastian Kleineidam <calvin@users.sf.net>" \
	  --msgid-bugs-address=calvin@users.sf.net -o $(TEMPLATE) \
	  $(POSOURCES)
	$(TALGETTEXT) -u $(TEMPLATE) $(TEMPLATES)

%.mo:	%.po
	if [ ! -d $(LDIR)/$*/LC_MESSAGES ]; then \
	  mkdir -p $(LDIR)/$*/LC_MESSAGES; \
	fi
	$(MSGFMT) -c --statistics -o $(LDIR)/$*/$(LFILE) $<

clean-local:
	@for f in $(LANGUAGES); do rm -f $(LDIR)/$$f/$(LFILE); done
	rm -f *.mo *.bak *.poedit
