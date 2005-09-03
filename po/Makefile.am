PYTHON=env PYTHONPATH=$(top_srcdir) python2.4
XGETTEXT:=xgettext
MSGFMT:=msgfmt
MSGMERGE:=msgmerge
TALGETTEXT=$(PYTHON) ../wc/webgui/TAL/talgettext.py
POSOURCES=$(shell find ../wc -name \*.py) \
	../webcleaner ../webcleaner-certificates
TEMPLATES=$(shell find ../templates -name \*.html)
PACKAGE=webcleaner
TEMPLATE=$(PACKAGE).pot
MYMAIL:=calvin@users.sourceforge.net
MYNAME:="Bastian Kleineidam <$(MYMAIL)>"
# local share dir
SHAREDIR=$(top_srcdir)/share/locale
# defined language (add new languages here)
LANGUAGES=de
MOFILES=$(patsubst %, %.mo, $(LANGUAGES) )

all: $(MOFILES)

%.mo:	%.po
	$(MSGFMT) -c --statistics -o $@ $<

%.po:	$(TEMPLATE)
	$(MSGMERGE) -U --suffix=.bak $@ $<

.PHONY: template
template: $(TEMPLATE)
$(TEMPLATE): $(POSOURCES) $(TEMPLATES)
	$(XGETTEXT) -w 80 --default-domain=$(PACKAGE) --language=Python \
          --copyright-holder=$(MYNAME) --msgid-bugs-address=$(MYMAIL) \
          --keyword=_n:1,2 -o $(TEMPLATE) $(POSOURCES)
	$(TALGETTEXT) -u $(TEMPLATE) $(TEMPLATES)

# for development: copy the generated .mo files to a local share dir
.PHONY: copymofiles
copymofiles: $(MOFILES)
	for la in $(LANGUAGES); do \
	  if [ ! -d $(SHAREDIR)/$$la/LC_MESSAGES ]; then \
	    mkdir -p $(SHAREDIR)/$$la/LC_MESSAGES; \
	  fi; \
          install -m 0644 $$la.mo $(SHAREDIR)/$$la/LC_MESSAGES/$(PACKAGE).mo; \
        done

clean-local:
	rm -f *.mo *.bak *.poedit
