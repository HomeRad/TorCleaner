# we use the scripts in Tools/i18n of the Python 2.0 distribution
PYTHON=python2.2
I18NTOOLS=.
GETTEXT=$(PYTHON) $(I18NTOOLS)/pygettext.py
MSGFMT=$(PYTHON) $(I18NTOOLS)/msgfmt.py
MSGMERGE=msgmerge
SOURCES=\
../webcleaner \
../wc/gui/ConfWindow.py \
../wc/gui/FXAllowRuleFrame.py \
../wc/gui/FXAllowdomainsRuleFrame.py \
../wc/gui/FXAllowurlsRuleFrame.py \
../wc/gui/FXBlockRuleFrame.py \
../wc/gui/FXBlockdomainsRuleFrame.py \
../wc/gui/FXBlockurlsRuleFrame.py \
../wc/gui/FXFolderRuleFrame.py \
../wc/gui/FXHeaderRuleFrame.py \
../wc/gui/FXImageRuleFrame.py \
../wc/gui/FXNocommentsRuleFrame.py \
../wc/gui/FXRuleTreeList.py \
../wc/gui/FXReplacerRuleFrame.py \
../wc/gui/FXRuleFrameFactory.py \
../wc/gui/FXRewriteRuleFrame.py \
../wc/gui/FXRuleFrame.py \
../wc/gui/HeaderWindow.py \
../wc/gui/ToolApp.py \
../wc/gui/ToolWindow.py \
../wc/gui/__init__.py \
../wc/debug_levels.py \
../wc/proxy/ClientServerMatchmaker.py \
../wc/proxy/Connection.py \
../wc/proxy/DeflateStream.py \
../wc/proxy/GunzipStream.py \
../wc/proxy/HttpClient.py \
../wc/proxy/HttpServer.py \
../wc/proxy/Interpreter.py \
../wc/proxy/LimitQueue.py \
../wc/proxy/Listener.py \
../wc/proxy/Server.py \
../wc/proxy/ServerHandleDirectly.py \
../wc/proxy/ServerPool.py \
../wc/proxy/UnchunkStream.py \
../wc/proxy/__init__.py \
../wc/proxy/dns_lookups.py \
../wc/proxy/winreg.py \
../wc/daemon/_nt.py \
../wc/daemon/_other.py \
../wc/daemon/_posix.py \
../wc/daemon/__init__.py \
../wc/filter/rules/AllowRule.py \
../wc/filter/rules/AllowdomainsRule.py \
../wc/filter/rules/AllowurlsRule.py \
../wc/filter/rules/BlockRule.py \
../wc/filter/rules/BlockdomainsRule.py \
../wc/filter/rules/BlockurlsRule.py \
../wc/filter/rules/ExternfileRule.py \
../wc/filter/rules/FolderRule.py \
../wc/filter/rules/HeaderRule.py \
../wc/filter/rules/ImageRule.py \
../wc/filter/rules/NocommentsRule.py \
../wc/filter/rules/ReplacerRule.py \
../wc/filter/rules/RewriteRule.py \
../wc/filter/rules/Rule.py \
../wc/filter/rules/UrlRule.py \
../wc/filter/rules/__init__.py \
../wc/filter/BinaryCharFilter.py \
../wc/filter/Blocker.py \
../wc/filter/Compress.py \
../wc/filter/GifImage.py \
../wc/filter/Header.py \
../wc/filter/Replacer.py \
../wc/filter/Rewriter.py \
../wc/filter/__init__.py \
../wc/parser/__init__.py \
../wc/parser/htmllib.py \
../wc/__init__.py \
../wc/ip.py \
../wc/webgui/__init__.py \
../wc/webgui/WebConfig.py

LDIR=../locale
LFILE=LC_MESSAGES/$(PACKAGE).mo
MOS=$(LDIR)/de/$(LFILE)
PACKAGE=webcleaner

.PHONY: all
all:
	$(MAKE) de.mo

%.po:	pot-stamp
	$(MSGMERGE) $@ $(PACKAGE).pot -o $@

pot-stamp: $(SOURCES)
	rm -f $(PACKAGE).pot
	$(GETTEXT) --default-domain=$(PACKAGE) --no-location $(SOURCES)
	touch pot-stamp

%.mo:	%.po
	$(MSGFMT) -o$(LDIR)/$*/$(LFILE) $<

clean:
	rm -f pot-stamp $(MOS)
