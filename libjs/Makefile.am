SUBDIRS			= fdlibm

INCLUDES		= -I$(top_srcdir) -I$(top_builddir)
EXTRA_DIST		= js.msg jsopcode.tbl

BUILT_SOURCES		= jsautocfg.h

if WIN32
NEW_DEFS		= @DEFS@ -DEXPORT_JS_API -DXP_WIN
else
NEW_DEFS		= @DEFS@ -DEXPORT_JS_API -DXP_UNIX
endif
DEFS			= $(NEW_DEFS)

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
			jstypes.h
libjs_la_LIBADD		= ./fdlibm/libfdm.la

noinst_PROGRAMS		= jscpucfg
jscpucfg_SOURCES	= jscpucfg.c jscpucfg.h

CLEANFILES		= jscpucfg jsautocfg.h

jsautocfg.h: jscpucfg@EXEEXT@
	./jscpucfg > jsautocfg.h
