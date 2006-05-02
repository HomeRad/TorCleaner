SUBDIRS			= fdlibm

INCLUDES		= -I$(top_srcdir) -I$(top_builddir)
EXTRA_DIST		= js.msg jskeyword.tbl jsopcode.tbl README

BUILT_SOURCES		= jsautocfg.h jsautokw.h

AM_CFLAGS = @JSDEFS@

noinst_LTLIBRARIES	= libjs.la
libjs_la_SOURCES	= jsapi.c jsapi.h \
			jsarena.c jsarena.h \
			jsarray.c jsarray.h \
			jsatom.c jsatom.h \
			jsbool.c jsbool.h \
			jscntxt.c jscntxt.h \
			jsdate.c jsdate.h \
			jsdbgapi.c jsdbgapi.h \
			jsdhash.c jsdhash.h \
			jsdtoa.c jsdtoa.h \
			jsemit.c jsemit.h \
			jsexn.c jsexn.h \
			jsfun.c jsfun.h \
			jsgc.c jsgc.h \
			jshash.c jshash.h \
			jsinterp.c jsinterp.h \
			jslock.c jslock.h \
			jslog2.c \
			jslong.c jslong.h \
			jsmath.c jsmath.h \
			jsnum.c jsnum.h \
			jsobj.c jsobj.h \
			jsopcode.c jsopcode.h \
			jsparse.c jsparse.h \
			jsprf.c jsprf.h \
			jsregexp.c jsregexp.h \
			jsscan.c jsscan.h \
			jsscope.c jsscope.h \
			jsscript.c jsscript.h \
			jsstr.c jsstr.h \
			jsutil.c jsutil.h \
			jsxdrapi.c jsxdrapi.h \
			jsxml.c jsxml.h \
			prmjtime.c prmjtime.h \
			jsbit.h \
			jsclist.h \
			jscompat.h \
			jsconfig.h \
			jslibmath.h \
			jsosdep.h \
			jsotypes.h \
			jsprvtd.h \
			jspubtd.h \
			jsstddef.h \
			jstypes.h \
			$(CONFIG_HEADER)

jsopcode.h jsinterp.h: jsopcode.tbl

libjs_la_LIBADD		= ./fdlibm/libfdm.la

if CROSS_COMPILE_LINUX
CLEANFILES = jscpucfg jskwgen $(BUILT_SOURCES)
jscpucfg: jscpucfg.c jscpucfg.h prtypes.h protypes.h prcpucfg.h
	gcc $(DEFAULT_INCLUDES) @JSDEFS@ $(CFLAGS) jscpucfg.c -o jscpucfg
jskwgen: jskwgen.c jsstddef.h jsconfig.h
	gcc $(DEFAULT_INCLUDES) @JSDEFS@ $(CFLAGS) jskwgen.c -o jskwgen
else
CLEANFILES = jscpucfg@EXEEXT@ jskwgen@EXEEXT@ $(BUILT_SOURCES)
noinst_PROGRAMS = jscpucfg jskwgen
jscpucfg_SOURCES = jscpucfg.c jscpucfg.h prtypes.h protypes.h prcpucfg.h
jskwgen_SOURCES = jskwgen.c jsstddef.h jsconfig.h
endif

jsautocfg.h: jscpucfg
	./jscpucfg > $@

jsautokw.h: jskwgen jskeyword.tbl
	./jskwgen $@

ORIGBASEDIR:=/home/calvin/src/mozilla
ORIGSRCDIR:=$(ORIGBASEDIR)/js/src
origdiff:
	(for f in *.c *.h *.tbl *.msg; do diff -u $$f $(ORIGSRCDIR)/$$f 2>/dev/null; done) | less

origupdate:
	for f in *.c *.h *.tbl *.msg; do \
	  if ! diff $$f $(ORIGSRCDIR)/$$f > /dev/null 2>&1; then \
	      if [ -e $(ORIGSRCDIR)/$$f ]; then \
	          /bin/cp -vf $(ORIGSRCDIR)/$$f $$f; \
	      fi; \
	  fi; \
	done
