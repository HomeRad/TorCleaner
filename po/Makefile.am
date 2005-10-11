PYVER:=2.4
PYTHON=env PYTHONPATH=$(top_srcdir) python$(PYVER)
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
POFILES=$(patsubst %, %.po, $(LANGUAGES) )

all: $(POFILES)

# The %.mo target is not used, but here for completeness. The setup.py
# build command will generate the needed .mo files with wc/msgfmt.py.
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

clean-local:
	rm -f *.mo *.bak *.poedit
