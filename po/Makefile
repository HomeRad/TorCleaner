# we use the scripts in Tools/i18n of the Python 2.0 distribution
I18NTOOLS=.
GETTEXT=python $(I18NTOOLS)/pygettext.py
MSGFMT=python $(I18NTOOLS)/msgfmt.py
MSGMERGE=msgmerge
SOURCES=\
../webcleaner \
../wc/gui/FXAllowRuleFrame.py \
../wc/gui/FXBlockRuleFrame.py \
../wc/gui/FXRuleTreeList.py \
../wc/gui/FXReplacerRuleFrame.py \
../wc/gui/FXImageRuleFrame.py \
../wc/gui/FXRuleFrameFactory.py \
../wc/gui/FXFolderRuleFrame.py \
../wc/gui/ConfWindow.py \
../wc/gui/FXRewriteRuleFrame.py \
../wc/gui/FXHeaderRuleFrame.py \
../wc/gui/__init__.py \
../wc/gui/FXRuleFrame.py \
../wc/gui/FXNocommentsRuleFrame.py \
../wc/gui/HeaderWindow.py \
../wc/gui/ToolWindow.py \
../wc/debug_levels.py \
../wc/proxy/dns/dnslib.py \
../wc/proxy/dns/dnstype.py \
../wc/proxy/dns/dnsclass.py \
../wc/proxy/dns/dnsopcode.py \
../wc/proxy/dns/__init__.py \
../wc/proxy/UnchunkStream.py \
../wc/proxy/dns_lookups.py \
../wc/proxy/HttpClient.py \
../wc/proxy/GunzipStream.py \
../wc/proxy/LimitQueue.py \
../wc/proxy/winreg.py \
../wc/proxy/ServerPool.py \
../wc/proxy/Listener.py \
../wc/proxy/Interpreter.py \
../wc/proxy/HttpServer.py \
../wc/proxy/ServerHandleDirectly.py \
../wc/proxy/ClientServerMatchmaker.py \
../wc/proxy/Connection.py \
../wc/proxy/Server.py \
../wc/proxy/__init__.py \
../wc/daemon/_nt.py \
../wc/daemon/_other.py \
../wc/daemon/_posix.py \
../wc/daemon/__init__.py \
../wc/filter/BinaryCharFilter.py \
../wc/filter/Rules.py \
../wc/filter/Compress.py \
../wc/filter/GifImage.py \
../wc/filter/Replacer.py \
../wc/filter/Rewriter.py \
../wc/filter/Blocker.py \
../wc/filter/Header.py \
../wc/filter/__init__.py \
../wc/parser/__init__.py \
../wc/parser/htmllib.py \
../wc/__init__.py
LDIR=../locale
LFILE=LC_MESSAGES/$(PACKAGE).mo
MOS=$(LDIR)/de/$(LFILE)
PACKAGE=webcleaner

.PHONY: all
all:
	$(MAKE) de.mo

%.po:	.time.pot
	$(MSGMERGE) $@ $(PACKAGE).pot -o $@

.time.pot:
	rm -f $(PACKAGE).pot
	$(GETTEXT) --default-domain=$(PACKAGE) --no-location $(SOURCES)
	touch .time.pot

%.mo:	%.po
	$(MSGFMT) -o$(LDIR)/$*/$(LFILE) $<

clean:
	rm -f .time.pot $(MOS)
