/* -*- Mode: C; tab-width: 8; indent-tabs-mode: nil; c-basic-offset: 4 -*-
 *
 * ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is SpiderMonkey E4X code, released August, 2004.
 *
 * The Initial Developer of the Original Code is
 * Netscape Communications Corporation.
 * Portions created by the Initial Developer are Copyright (C) 1998
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either of the GNU General Public License Version 2 or later (the "GPL"),
 * or the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

#include "jsstddef.h"
#include "jsconfig.h"

#if JS_HAS_XML_SUPPORT

#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "jstypes.h"
#include "jsbit.h"
#include "jsprf.h"
#include "jsutil.h"
#include "jsapi.h"
#include "jsarray.h"
#include "jsatom.h"
#include "jsbool.h"
#include "jscntxt.h"
#include "jsfun.h"
#include "jsgc.h"
#include "jsinterp.h"
#include "jslock.h"
#include "jsnum.h"
#include "jsobj.h"
#include "jsopcode.h"
#include "jsparse.h"
#include "jsscan.h"
#include "jsscope.h"
#include "jsscript.h"
#include "jsstr.h"
#include "jsxml.h"

#ifdef DEBUG
#include <string.h>     /* for #ifdef DEBUG memset calls */
#endif

/*
 * NOTES
 * - in the js shell, you must use the -x command line option, or call
 *   options('xml') before compiling anything that uses XML literals
 *
 * TODO
 * - XXXbe patrol
 * - JSCLASS_DOCUMENT_OBSERVER support -- live two-way binding to Gecko's DOM!
 * - JS_TypeOfValue sure could use a cleaner interface to "types"
 */

#ifdef DEBUG_brendan
#define METERING        1
#endif

#ifdef METERING
static struct {
    jsrefcount  qname;
    jsrefcount  qnameobj;
    jsrefcount  liveqname;
    jsrefcount  liveqnameobj;
    jsrefcount  namespace;
    jsrefcount  namespaceobj;
    jsrefcount  livenamespace;
    jsrefcount  livenamespaceobj;
    jsrefcount  xml;
    jsrefcount  xmlobj;
    jsrefcount  livexml;
    jsrefcount  livexmlobj;
} xml_stats;

#define METER(x)        JS_ATOMIC_INCREMENT(&(x))
#define UNMETER(x)      JS_ATOMIC_DECREMENT(&(x))
#else
#define METER(x)        /* nothing */
#define UNMETER(x)      /* nothing */
#endif

/*
 * Random utilities and global functions.
 */
const char js_AnyName_str[]       = "AnyName";
const char js_AttributeName_str[] = "AttributeName";
const char js_isXMLName_str[]     = "isXMLName";
const char js_Namespace_str[]     = "Namespace";
const char js_QName_str[]         = "QName";
const char js_XML_str[]           = "XML";
const char js_XMLList_str[]       = "XMLList";
const char js_localName_str[]     = "localName";
const char js_prefix_str[]        = "prefix";
const char js_toXMLString_str[]   = "toXMLString";
const char js_uri_str[]           = "uri";

const char js_amp_entity_str[]    = "&amp;";
const char js_gt_entity_str[]     = "&gt;";
const char js_lt_entity_str[]     = "&lt;";
const char js_quot_entity_str[]   = "&quot;";

#define IS_EMPTY(str) (JSSTRING_LENGTH(str) == 0)
#define IS_STAR(str)  (JSSTRING_LENGTH(str) == 1 && *JSSTRING_CHARS(str) == '*')

static JSBool
xml_isXMLName(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
              jsval *rval)
{
    *rval = BOOLEAN_TO_JSVAL(js_IsXMLName(cx, argv[0]));
    return JS_TRUE;
}

/*
 * Namespace class and library functions.
 */
enum namespace_tinyid {
    NAMESPACE_PREFIX = -1,
    NAMESPACE_URI = -2
};

static JSBool
namespace_getProperty(JSContext *cx, JSObject *obj, jsval id, jsval *vp)
{
    JSXMLNamespace *ns;

    if (!JSVAL_IS_INT(id))
        return JS_TRUE;

    ns = (JSXMLNamespace *)
         JS_GetInstancePrivate(cx, obj, &js_NamespaceClass.base, NULL);
    if (!ns)
        return JS_TRUE;

    switch (JSVAL_TO_INT(id)) {
      case NAMESPACE_PREFIX:
        *vp = ns->prefix ? STRING_TO_JSVAL(ns->prefix) : JSVAL_VOID;
        break;
      case NAMESPACE_URI:
        *vp = STRING_TO_JSVAL(ns->uri);
        break;
    }
    return JS_TRUE;
}

static void
namespace_finalize(JSContext *cx, JSObject *obj)
{
    JSXMLNamespace *ns;
    JSRuntime *rt;

    ns = (JSXMLNamespace *) JS_GetPrivate(cx, obj);
    if (!ns)
        return;
    JS_ASSERT(ns->object == obj);
    ns->object = NULL;
    if (ns->markflag == JSXML_MARK_CLEAR) {
        /* Not marked by obj or any other owner, so flag ns as doomed. */
        ns->markflag = JSXML_MARK_DOOMED;
        rt = cx->runtime;
        ns->object = (JSObject *) rt->gcDoomedNamespaces;
        rt->gcDoomedNamespaces = ns;
    }
    UNMETER(xml_stats.livenamespaceobj);
}

static void
namespace_mark_private(JSContext *cx, JSXMLNamespace *ns, void *arg)
{
    if (ns->markflag != JSXML_MARK_CLEAR)
        return;
    ns->markflag = JSXML_MARK_LIVE;
    JS_MarkGCThing(cx, ns->prefix, js_prefix_str, arg);
    JS_MarkGCThing(cx, ns->uri, js_uri_str, arg);
}

static void
namespace_mark_vector(JSContext *cx, JSXMLNamespace **vec, uint32 len,
                      void *arg)
{
    uint32 i;
    JSXMLNamespace *ns;

    for (i = 0; i < len; i++) {
        ns = vec[i];
        if (ns->object) {
#ifdef GC_MARK_DEBUG
            char buf[100];

            JS_snprintf(buf, sizeof buf, "%s=%s",
                        ns->prefix ? JS_GetStringBytes(ns->prefix) : "",
                        JS_GetStringBytes(ns->uri));
#else
            const char *buf = NULL;
#endif
            JS_MarkGCThing(cx, ns->object, buf, arg);
        } else {
            namespace_mark_private(cx, ns, arg);
        }
    }
}

static uint32
namespace_mark(JSContext *cx, JSObject *obj, void *arg)
{
    JSXMLNamespace *ns;

    ns = (JSXMLNamespace *) JS_GetPrivate(cx, obj);
    namespace_mark_private(cx, ns, arg);
    return 0;
}

static JSBool
namespace_equality(JSContext *cx, JSObject *obj, jsval v, JSBool *bp)
{
    JSXMLNamespace *ns, *ns2;
    JSObject *obj2;

    ns = (JSXMLNamespace *) JS_GetPrivate(cx, obj);
    JS_ASSERT(JSVAL_IS_OBJECT(v));
    obj2 = JSVAL_TO_OBJECT(v);
    if (!obj2 || OBJ_GET_CLASS(cx, obj2) != &js_NamespaceClass.base) {
        *bp = JS_FALSE;
    } else {
        ns2 = (JSXMLNamespace *) JS_GetPrivate(cx, obj2);
        *bp = !js_CompareStrings(ns->uri, ns2->uri);
    }
    return JS_TRUE;
}

JSExtendedClass js_NamespaceClass = {
  { "Namespace",
    JSCLASS_HAS_PRIVATE | JSCLASS_CONSTRUCT_PROTOTYPE | JSCLASS_IS_EXTENDED,
    JS_PropertyStub,   JS_PropertyStub,   namespace_getProperty, NULL,
    JS_EnumerateStub,  JS_ResolveStub,    JS_ConvertStub,    namespace_finalize,
    NULL,              NULL,              NULL,              NULL,
    NULL,              NULL,              namespace_mark,    NULL },
    namespace_equality,
    JSCLASS_NO_RESERVED_MEMBERS
};

#define NAMESPACE_ATTRS                                                       \
    (JSPROP_ENUMERATE | JSPROP_READONLY | JSPROP_PERMANENT | JSPROP_SHARED)

static JSPropertySpec namespace_props[] = {
    {js_prefix_str,    NAMESPACE_PREFIX,  NAMESPACE_ATTRS,   0, 0},
    {js_uri_str,       NAMESPACE_URI,     NAMESPACE_ATTRS,   0, 0},
    {0,0,0,0,0}
};

static JSBool
namespace_toString(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                   jsval *rval)
{
    JSXMLNamespace *ns;

    ns = (JSXMLNamespace *)
         JS_GetInstancePrivate(cx, obj, &js_NamespaceClass.base, argv);
    if (!ns)
        return JS_FALSE;

    *rval = STRING_TO_JSVAL(ns->uri);
    return JS_TRUE;
}

static JSFunctionSpec namespace_methods[] = {
    {js_toString_str,  namespace_toString,        0,0,0},
    {0,0,0,0,0}
};

JSXMLNamespace *
js_NewXMLNamespace(JSContext *cx, JSString *prefix, JSString *uri,
                   JSBool declared)
{
    JSXMLNamespace *ns;

    ns = (JSXMLNamespace *) JS_malloc(cx, sizeof(JSXMLNamespace));
    if (!ns)
        return NULL;
    ns->object = NULL;
    ns->prefix = prefix;
    ns->uri = uri;
    ns->markflag = JSXML_MARK_SINGLE_OWNER;
    ns->declared = declared;
    METER(xml_stats.namespace);
    METER(xml_stats.livenamespace);
    return ns;
}

void
js_DestroyXMLNamespace(JSContext *cx, JSXMLNamespace *ns)
{
    if (ns->markflag > JSXML_MARK_SINGLE_OWNER)
        return;
    JS_free(cx, ns);
    UNMETER(xml_stats.livenamespace);
}

JSObject *
js_NewXMLNamespaceObject(JSContext *cx, JSString *prefix, JSString *uri,
                         JSBool declared)
{
    JSXMLNamespace *ns;
    JSObject *obj;

    ns = js_NewXMLNamespace(cx, prefix, uri, declared);
    if (!ns)
        return NULL;
    obj = js_GetXMLNamespaceObject(cx, ns);
    if (!obj)
        js_DestroyXMLNamespace(cx, ns);
    return obj;
}

JSObject *
js_GetXMLNamespaceObject(JSContext *cx, JSXMLNamespace *ns)
{
    JSObject *obj;

    obj = ns->object;
    if (obj) {
        JS_ASSERT(JS_GetPrivate(cx, obj) == ns);
        JS_ASSERT(ns->markflag == JSXML_MARK_CLEAR);
        return obj;
    }
    obj = js_NewObject(cx, &js_NamespaceClass.base, NULL, NULL);
    if (!obj || !JS_SetPrivate(cx, obj, ns)) {
        cx->newborn[GCX_OBJECT] = NULL;
        return NULL;
    }
    ns->object = obj;
    ns->markflag = JSXML_MARK_CLEAR;
    METER(xml_stats.namespaceobj);
    METER(xml_stats.livenamespaceobj);
    return obj;
}

/*
 * QName class and library functions.
 */
enum qname_tinyid {
    QNAME_URI = -1,
    QNAME_LOCALNAME = -2
};

static JSBool
qname_getProperty(JSContext *cx, JSObject *obj, jsval id, jsval *vp)
{
    JSXMLQName *qn;

    if (!JSVAL_IS_INT(id))
        return JS_TRUE;

    qn = (JSXMLQName *)
         JS_GetInstancePrivate(cx, obj, &js_QNameClass.base, NULL);
    if (!qn)
        return JS_TRUE;

    switch (JSVAL_TO_INT(id)) {
      case QNAME_URI:
        *vp = qn->uri ? STRING_TO_JSVAL(qn->uri) : JSVAL_NULL;
        break;
      case QNAME_LOCALNAME:
        *vp = STRING_TO_JSVAL(qn->localName);
        break;
    }
    return JS_TRUE;
}

static void
qname_finalize(JSContext *cx, JSObject *obj)
{
    JSXMLQName *qn;
    JSRuntime *rt;

    qn = (JSXMLQName *) JS_GetPrivate(cx, obj);
    if (!qn)
        return;
    JS_ASSERT(qn->object == obj);
    qn->object = NULL;
    if (qn->markflag == JSXML_MARK_CLEAR) {
        /* Not marked by obj or any other owner, so flag qn as doomed. */
        qn->markflag = JSXML_MARK_DOOMED;
        rt = cx->runtime;
        qn->object = (JSObject *) rt->gcDoomedQNames;
        rt->gcDoomedQNames = qn;
    }
    UNMETER(xml_stats.liveqnameobj);
}

static void
qname_mark_private(JSContext *cx, JSXMLQName *qn, void *arg)
{
    if (qn->markflag != JSXML_MARK_CLEAR)
        return;
    qn->markflag = JSXML_MARK_LIVE;
    JS_MarkGCThing(cx, qn->uri, js_uri_str, arg);
    JS_MarkGCThing(cx, qn->prefix, js_prefix_str, arg);
    JS_MarkGCThing(cx, qn->localName, js_localName_str, arg);
}

static uint32
qname_mark(JSContext *cx, JSObject *obj, void *arg)
{
    JSXMLQName *qn;

    qn = (JSXMLQName *) JS_GetPrivate(cx, obj);
    qname_mark_private(cx, qn, arg);
    return 0;
}

static JSBool
qname_identity(JSXMLQName *qna, JSXMLQName *qnb)
{
    if (!qna->uri ^ !qnb->uri)
        return JS_FALSE;
    if (qna->uri && js_CompareStrings(qna->uri, qnb->uri))
        return JS_FALSE;
    return !js_CompareStrings(qna->localName, qnb->localName);
}

static JSBool
qname_equality(JSContext *cx, JSObject *obj, jsval v, JSBool *bp)
{
    JSXMLQName *qn, *qn2;
    JSObject *obj2;

    qn = (JSXMLQName *) JS_GetPrivate(cx, obj);
    JS_ASSERT(JSVAL_IS_OBJECT(v));
    obj2 = JSVAL_TO_OBJECT(v);
    if (!obj2 || OBJ_GET_CLASS(cx, obj2) != &js_QNameClass.base) {
        *bp = JS_FALSE;
    } else {
        qn2 = (JSXMLQName *) JS_GetPrivate(cx, obj2);
        *bp = qname_identity(qn, qn2);
    }
    return JS_TRUE;
}

JSExtendedClass js_QNameClass = {
  { "QName",
    JSCLASS_HAS_PRIVATE | JSCLASS_CONSTRUCT_PROTOTYPE | JSCLASS_IS_EXTENDED,
    JS_PropertyStub,   JS_PropertyStub,   qname_getProperty, NULL,
    JS_EnumerateStub,  JS_ResolveStub,    JS_ConvertStub,    qname_finalize,
    NULL,              NULL,              NULL,              NULL,
    NULL,              NULL,              qname_mark,        NULL },
    qname_equality,
    JSCLASS_NO_RESERVED_MEMBERS
};

/*
 * Classes for the ECMA-357-internal types AttributeName and AnyName, which
 * are like QName, except that they have no property getters.  They share the
 * qname_toString method, and therefore are exposed as constructable objects
 * in this implementation.
 */
JSClass js_AttributeNameClass = {
    js_AttributeName_str, JSCLASS_HAS_PRIVATE | JSCLASS_CONSTRUCT_PROTOTYPE,
    JS_PropertyStub,   JS_PropertyStub,   JS_PropertyStub,   JS_PropertyStub,
    JS_EnumerateStub,  JS_ResolveStub,    JS_ConvertStub,    qname_finalize,
    NULL,              NULL,              NULL,              NULL,
    NULL,              NULL,              qname_mark,        NULL
};

JSClass js_AnyNameClass = {
    js_AnyName_str,    JSCLASS_HAS_PRIVATE | JSCLASS_CONSTRUCT_PROTOTYPE,
    JS_PropertyStub,   JS_PropertyStub,   JS_PropertyStub,   JS_PropertyStub,
    JS_EnumerateStub,  JS_ResolveStub,    JS_ConvertStub,    qname_finalize,
    NULL,              NULL,              NULL,              NULL,
    NULL,              NULL,              qname_mark,        NULL
};

#define QNAME_ATTRS                                                           \
    (JSPROP_ENUMERATE | JSPROP_READONLY | JSPROP_PERMANENT | JSPROP_SHARED)

static JSPropertySpec qname_props[] = {
    {js_uri_str,       QNAME_URI,         QNAME_ATTRS,       0, 0},
    {js_localName_str, QNAME_LOCALNAME,   QNAME_ATTRS,       0, 0},
    {0,0,0,0,0}
};

static JSBool
qname_toString(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
               jsval *rval)
{
    JSClass *clasp;
    JSXMLQName *qn;
    JSString *str, *qualstr;
    size_t length;
    jschar *chars;

    clasp = OBJ_GET_CLASS(cx, obj);
    if (clasp == &js_AttributeNameClass || clasp == &js_AnyNameClass) {
        qn = (JSXMLQName *) JS_GetPrivate(cx, obj);
    } else {
        qn = (JSXMLQName *)
             JS_GetInstancePrivate(cx, obj, &js_QNameClass.base, argv);
        if (!qn)
            return JS_FALSE;
    }

    if (!qn->uri) {
        /* No uri means wildcard qualifier. */
        str = ATOM_TO_STRING(cx->runtime->atomState.starQualifierAtom);
    } else if (IS_EMPTY(qn->uri)) {
        /* Empty string for uri means localName is in no namespace. */
        str = cx->runtime->emptyString;
    } else {
        qualstr = ATOM_TO_STRING(cx->runtime->atomState.qualifierAtom);
        str = js_ConcatStrings(cx, qn->uri, qualstr);
        if (!str)
            return JS_FALSE;
    }
    str = js_ConcatStrings(cx, str, qn->localName);
    if (!str)
        return JS_FALSE;

    if (str && clasp == &js_AttributeNameClass) {
        length = JSSTRING_LENGTH(str);
        chars = (jschar *) JS_malloc(cx, (length + 2) * sizeof(jschar));
        if (!chars)
            return JS_FALSE;
        *chars = '@';
        js_strncpy(chars + 1, JSSTRING_CHARS(str), length);
        chars[++length] = 0;
        str = js_NewString(cx, chars, length, 0);
        if (!str) {
            JS_free(cx, chars);
            return JS_FALSE;
        }
    }

    *rval = STRING_TO_JSVAL(str);
    return JS_TRUE;
}

static JSFunctionSpec qname_methods[] = {
    {js_toString_str,  qname_toString,    0,0,0},
    {0,0,0,0,0}
};

JSXMLQName *
js_NewXMLQName(JSContext *cx, JSString *uri, JSString *prefix,
               JSString *localName)
{
    JSXMLQName *qn;

    qn = (JSXMLQName *) JS_malloc(cx, sizeof(JSXMLQName));
    if (!qn)
        return NULL;
    qn->object = NULL;
    qn->uri = uri;
    qn->prefix = prefix;
    qn->localName = localName;
    qn->markflag = JSXML_MARK_SINGLE_OWNER;
    METER(xml_stats.qname);
    METER(xml_stats.liveqname);
    return qn;
}

void
js_DestroyXMLQName(JSContext *cx, JSXMLQName *qn)
{
    if (qn->markflag > JSXML_MARK_SINGLE_OWNER)
        return;
    JS_free(cx, qn);
    UNMETER(xml_stats.liveqname);
}

JSObject *
js_NewXMLQNameObject(JSContext *cx, JSString *uri, JSString *prefix,
                     JSString *localName)
{
    JSXMLQName *qn;
    JSObject *obj;

    qn = js_NewXMLQName(cx, uri, prefix, localName);
    if (!qn)
        return NULL;
    obj = js_GetXMLQNameObject(cx, qn);
    if (!obj)
        js_DestroyXMLQName(cx, qn);
    return obj;
}

JSObject *
js_GetXMLQNameObject(JSContext *cx, JSXMLQName *qn)
{
    JSObject *obj;

    obj = qn->object;
    if (obj) {
        JS_ASSERT(JS_GetPrivate(cx, obj) == qn);
        JS_ASSERT(qn->markflag == JSXML_MARK_CLEAR);
        return obj;
    }
    obj = js_NewObject(cx, &js_QNameClass.base, NULL, NULL);
    if (!obj || !JS_SetPrivate(cx, obj, qn)) {
        cx->newborn[GCX_OBJECT] = NULL;
        return NULL;
    }
    qn->object = obj;
    qn->markflag = JSXML_MARK_CLEAR;
    METER(xml_stats.qnameobj);
    METER(xml_stats.liveqnameobj);
    return obj;
}

JSObject *
js_GetAttributeNameObject(JSContext *cx, JSXMLQName *qn)
{
    JSXMLQName *origqn;
    JSObject *obj;

    origqn = qn;
    obj = qn->object;
    if (obj) {
        if (OBJ_GET_CLASS(cx, obj) == &js_AttributeNameClass)
            return obj;
        qn = js_NewXMLQName(cx, qn->uri, qn->prefix, qn->localName);
        if (!qn)
            return NULL;
    }

    obj = js_NewObject(cx, &js_AttributeNameClass, NULL, NULL);
    if (!obj || !JS_SetPrivate(cx, obj, qn)) {
        cx->newborn[GCX_OBJECT] = NULL;
        if (qn != origqn)
            js_DestroyXMLQName(cx, qn);
        return NULL;
    }

    qn->object = obj;
    qn->markflag = JSXML_MARK_CLEAR;
    METER(xml_stats.qnameobj);
    METER(xml_stats.liveqnameobj);
    return obj;
}

JSObject *
js_ConstructXMLQNameObject(JSContext *cx, jsval nsval, jsval lnval)
{
    jsval argv[2];

    /*
     * ECMA-357 11.1.2,
     * The _QualifiedIdentifier : PropertySelector :: PropertySelector_
     * production, step 2.
     */
    if (!JSVAL_IS_PRIMITIVE(nsval) &&
        OBJ_GET_CLASS(cx, JSVAL_TO_OBJECT(nsval)) == &js_AnyNameClass) {
        nsval = JSVAL_NULL;
    }

    argv[0] = nsval;
    argv[1] = lnval;
    return js_ConstructObject(cx, &js_QNameClass.base, NULL, NULL, 2, argv);
}

static JSBool
IsXMLName(const jschar *cp, size_t n)
{
    JSBool rv;
    jschar c;

    rv = JS_FALSE;
    if (n != 0 && JS_ISXMLNSSTART(*cp)) {
        while (--n != 0) {
            c = *++cp;
            if (!JS_ISXMLNS(c))
                return rv;
        }
        rv = JS_TRUE;
    }
    return rv;
}

JSBool
js_IsXMLName(JSContext *cx, jsval v)
{
    JSClass *clasp;
    JSXMLQName *qn;
    JSString *name;
    JSErrorReporter older;

    /*
     * Inline specialization of the QName constructor called with v passed as
     * the only argument, to compute the localName for the constructed qname,
     * without actually allocating the object or computing its uri and prefix.
     * See ECMA-357 13.1.2.1 step 1 and 13.3.2.
     */
    if (!JSVAL_IS_PRIMITIVE(v) &&
        (clasp = OBJ_GET_CLASS(cx, JSVAL_TO_OBJECT(v)),
         clasp == &js_QNameClass.base ||
         clasp == &js_AttributeNameClass ||
         clasp == &js_AnyNameClass)) {
        qn = (JSXMLQName *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
        name = qn->localName;
    } else {
        older = JS_SetErrorReporter(cx, NULL);
        name = js_ValueToString(cx, v);
        JS_SetErrorReporter(cx, older);
        if (!name) {
            JS_ClearPendingException(cx);
            return JS_FALSE;
        }
    }

    return IsXMLName(JSSTRING_CHARS(name), JSSTRING_LENGTH(name));
}

static JSBool
Namespace(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    jsval urival, prefixval;
    JSObject *uriobj;
    JSBool isNamespace, isQName;
    JSClass *clasp;
    JSString *empty, *prefix;
    JSXMLNamespace *ns, *ns2;
    JSXMLQName *qn;

    urival = argv[argc > 1];
    isNamespace = isQName = JS_FALSE;
    if (!JSVAL_IS_PRIMITIVE(urival)) {
        uriobj = JSVAL_TO_OBJECT(urival);
        clasp = OBJ_GET_CLASS(cx, uriobj);
        isNamespace = (clasp == &js_NamespaceClass.base);
        isQName = (clasp == &js_QNameClass.base);
    }
#ifdef __GNUC__         /* suppress bogus gcc warnings */
    else uriobj = NULL;
#endif

    if (!(cx->fp->flags & JSFRAME_CONSTRUCTING)) {
        /* Namespace called as function. */
        if (argc == 1 && isNamespace) {
            /* Namespace called with one Namespace argument is identity. */
            *rval = urival;
            return JS_TRUE;
        }

        /* Create and return a new QName object exactly as if constructed. */
        obj = js_NewObject(cx, &js_NamespaceClass.base, NULL, NULL);
        if (!obj)
            return JS_FALSE;
        *rval = OBJECT_TO_JSVAL(obj);
    }
    METER(xml_stats.namespaceobj);
    METER(xml_stats.livenamespaceobj);

    /*
     * Create and connect private data to rooted obj early, so we don't have
     * to worry about rooting string newborns hanging off of the private data
     * further below.
     */
    empty = cx->runtime->emptyString;
    ns = js_NewXMLNamespace(cx, empty, empty, JS_FALSE);
    if (!ns)
        return JS_FALSE;
    if (!JS_SetPrivate(cx, obj, ns)) {
        js_DestroyXMLNamespace(cx, ns);
        return JS_FALSE;
    }
    ns->object = obj;
    ns->markflag = JSXML_MARK_CLEAR;

    if (argc == 1) {
        if (isNamespace) {
            ns2 = (JSXMLNamespace *) JS_GetPrivate(cx, uriobj);
            ns->uri = ns2->uri;
            ns->prefix = ns2->prefix;
        } else if (isQName &&
                   (qn = (JSXMLQName *) JS_GetPrivate(cx, uriobj))->uri) {
            ns->uri = qn->uri;
            ns->prefix = qn->prefix;
        } else {
            ns->uri = js_ValueToString(cx, urival);
            if (!ns->uri)
                return JS_FALSE;

            /* NULL here represents *undefined* in ECMA-357 13.2.2 3(c)iii. */
            if (!IS_EMPTY(ns->uri))
                ns->prefix = NULL;
        }
    } else if (argc == 2) {
        if (isQName &&
            (qn = (JSXMLQName *) JS_GetPrivate(cx, uriobj))->uri) {
            ns->uri = qn->uri;
        } else {
            ns->uri = js_ValueToString(cx, urival);
            if (!ns->uri)
                return JS_FALSE;
        }

        prefixval = argv[0];
        if (IS_EMPTY(ns->uri)) {
            if (!JSVAL_IS_VOID(prefixval)) {
                prefix = js_ValueToString(cx, prefixval);
                if (!prefix)
                    return JS_FALSE;
                if (!IS_EMPTY(prefix)) {
                    JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                                         JSMSG_BAD_XML_NAMESPACE,
                                         js_ValueToPrintableString(cx,
                                             STRING_TO_JSVAL(prefix)));
                    return JS_FALSE;
                }
            }
        } else if (JSVAL_IS_VOID(prefixval) || !js_IsXMLName(cx, prefixval)) {
            /* NULL here represents *undefined* in ECMA-357 13.2.2 4(d) etc. */
            ns->prefix = NULL;
        } else {
            prefix = js_ValueToString(cx, prefixval);
            if (!prefix)
                return JS_FALSE;
            ns->prefix = prefix;
        }
    }

    return JS_TRUE;
}

static JSBool
QName(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    jsval nameval, nsval;
    JSBool isQName, isNamespace;
    JSXMLQName *qn;
    JSString *uri, *prefix, *name;
    JSObject *nsobj;
    JSClass *clasp;
    JSXMLNamespace *ns;

    nameval = argv[argc > 1];
    isQName =
        !JSVAL_IS_PRIMITIVE(nameval) &&
        OBJ_GET_CLASS(cx, JSVAL_TO_OBJECT(nameval)) == &js_QNameClass.base;

    if (!(cx->fp->flags & JSFRAME_CONSTRUCTING)) {
        /* QName called as function. */
        if (argc == 1 && isQName) {
            /* QName called with one QName argument is identity. */
            *rval = nameval;
            return JS_TRUE;
        }

        /*
         * Create and return a new QName object exactly as if constructed.
         * Use the constructor's clasp so we can be shared by AttributeName
         * (see below after this function).
         */
        obj = js_NewObject(cx,
                           argv
                           ? JS_ValueToFunction(cx, argv[-2])->clasp
                           : &js_QNameClass.base,
                           NULL, NULL);
        if (!obj)
            return JS_FALSE;
        *rval = OBJECT_TO_JSVAL(obj);
    }
    METER(xml_stats.qnameobj);
    METER(xml_stats.liveqnameobj);

    if (isQName) {
        /* If namespace is not specified and name is a QName, clone it. */
        qn = (JSXMLQName *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(nameval));
        if (argc == 1) {
            uri = qn->uri;
            prefix = qn->prefix;
            name = qn->localName;
            goto out;
        }

        /* Namespace and qname were passed -- use the qname's localName. */
        nameval = STRING_TO_JSVAL(qn->localName);
    }

    if (argc == 0) {
        name = cx->runtime->emptyString;
    } else {
        name = js_ValueToString(cx, nameval);
        if (!name)
            return JS_FALSE;

        /* Use argv[1] as a local root for name, even if it was not passed. */
        argv[1] = STRING_TO_JSVAL(name);
    }

    nsval = argv[0];
    if (argc == 1 || JSVAL_IS_VOID(nsval)) {
        if (IS_STAR(name)) {
            nsval = JSVAL_NULL;
        } else {
            if (!js_GetDefaultXMLNamespace(cx, &nsval))
                return JS_FALSE;
        }
    }

    if (JSVAL_IS_NULL(nsval)) {
        /* NULL prefix represents *undefined* in ECMA-357 13.3.2 5(a). */
        uri = prefix = NULL;
    } else {
        /*
         * Inline specialization of the Namespace constructor called with
         * nsval passed as the only argument, to compute the uri and prefix
         * for the constructed namespace, without actually allocating the
         * object or computing other members.  See ECMA-357 13.3.2 6(a) and
         * 13.2.2.
         */
        isNamespace = isQName = JS_FALSE;
        if (!JSVAL_IS_PRIMITIVE(nsval)) {
            nsobj = JSVAL_TO_OBJECT(nsval);
            clasp = OBJ_GET_CLASS(cx, nsobj);
            isNamespace = (clasp == &js_NamespaceClass.base);
            isQName = (clasp == &js_QNameClass.base);
        }
#ifdef __GNUC__         /* suppress bogus gcc warnings */
        else nsobj = NULL;
#endif

        if (isNamespace) {
            ns = (JSXMLNamespace *) JS_GetPrivate(cx, nsobj);
            uri = ns->uri;
            prefix = ns->prefix;
        } else if (isQName &&
                   (qn = (JSXMLQName *) JS_GetPrivate(cx, nsobj))->uri) {
            uri = qn->uri;
            prefix = qn->prefix;
        } else {
            uri = js_ValueToString(cx, nsval);
            if (!uri)
                return JS_FALSE;

            /* NULL here represents *undefined* in ECMA-357 13.2.2 3(c)iii. */
            prefix = IS_EMPTY(uri) ? cx->runtime->emptyString : NULL;
        }
    }

out:
    qn = js_NewXMLQName(cx, uri, prefix, name);
    if (!qn)
        return JS_FALSE;
    if (!JS_SetPrivate(cx, obj, qn)) {
        js_DestroyXMLQName(cx, qn);
        return JS_FALSE;
    }
    qn->object = obj;
    qn->markflag = JSXML_MARK_CLEAR;
    return JS_TRUE;
}

static JSBool
AnyName(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    /* Return the one true AnyName instance. */
    return js_GetAnyName(cx, rval);
}

static JSBool
AttributeName(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
              jsval *rval)
{
    /*
     * Since js_AttributeNameClass was initialized, obj will have that as its
     * class, not js_QNameClass.
     */
    return QName(cx, obj, argc, argv, rval);
}

/*
 * XMLArray library functions.
 */
static JSBool
namespace_identity(const void *a, const void *b)
{
    const JSXMLNamespace *nsa = (const JSXMLNamespace *) a;
    const JSXMLNamespace *nsb = (const JSXMLNamespace *) b;

    if (nsa->prefix && nsb->prefix) {
        if (js_CompareStrings(nsa->prefix, nsb->prefix))
            return JS_FALSE;
    } else {
        if (nsa->prefix || nsb->prefix)
            return JS_FALSE;
    }
    return !js_CompareStrings(nsa->uri, nsb->uri);
}

static JSBool
attr_identity(const void *a, const void *b)
{
    const JSXML *xmla = (const JSXML *) a;
    const JSXML *xmlb = (const JSXML *) b;

    return qname_identity(xmla->name, xmlb->name);
}

static void
XMLArrayCursorInit(JSXMLArrayCursor *cursor, JSXMLArray *array)
{
    JSXMLArrayCursor *next;

    cursor->array = array;
    cursor->index = 0;
    next = cursor->next = array->cursors;
    if (next)
        next->prevp = &cursor->next;
    cursor->prevp = &array->cursors;
    array->cursors = cursor;
}

static void
XMLArrayCursorFinish(JSXMLArrayCursor *cursor)
{
    JSXMLArrayCursor *next;

    if (!cursor->array)
        return;
    next = cursor->next;
    if (next)
        next->prevp = cursor->prevp;
    *cursor->prevp = cursor->next;
    cursor->array = NULL;
}

/* NB: called with null cx from the GC, via xml_mark => XMLArrayTrim. */
static JSBool
XMLArraySetCapacity(JSContext *cx, JSXMLArray *array, uint32 capacity)
{
    void **vector;

    if (capacity == 0) {
        /* We could let realloc(p, 0) free this, but purify gets confused. */
        if (array->vector)
            free(array->vector);
        vector = NULL;
    } else {
        if ((size_t)capacity > ~(size_t)0 / sizeof(void *) ||
            !(vector = (void **)
                       realloc(array->vector, capacity * sizeof(void *)))) {
            if (cx)
                JS_ReportOutOfMemory(cx);
            return JS_FALSE;
        }
    }
    array->capacity = capacity;
    array->vector = vector;
    return JS_TRUE;
}

static void
XMLArrayTrim(JSXMLArray *array)
{
    if (array->length < array->capacity)
        XMLArraySetCapacity(NULL, array, array->length);
}

static JSBool
XMLArrayInit(JSContext *cx, JSXMLArray *array, uint32 capacity)
{
    array->length = 0;
    array->capacity = capacity;
    array->vector = NULL;
    array->cursors = NULL;
    return capacity == 0 || XMLArraySetCapacity(cx, array, capacity);
}

typedef void
(* JS_DLL_CALLBACK JSXMLArrayElemDtor)(JSContext *cx, void *elt);

static void
XMLArrayFinish(JSContext *cx, JSXMLArray *array, JSXMLArrayElemDtor dtor)
{
    uint32 i, n;
    void *elt;
    JSXMLArrayCursor *cursor;

    if (dtor) {
        for (i = 0, n = array->length; i < n; i++) {
            elt = array->vector[i];
            if (elt)
                dtor(cx, elt);
        }
    }
    JS_free(cx, array->vector);

    while ((cursor = array->cursors) != NULL)
        XMLArrayCursorFinish(cursor);

#ifdef DEBUG
    memset(array, 0xd5, sizeof *array);
#endif
}

#define XML_NOT_FOUND   ((uint32) -1)

static uint32
XMLArrayFindMember(JSXMLArray *array, void *elt, JSIdentityOp identity)
{
    void **vector;
    uint32 i, n;

    /* The identity op must not reallocate array->vector. */
    vector = array->vector;
    if (identity) {
        for (i = 0, n = array->length; i < n; i++) {
            if (identity(vector[i], elt))
                return i;
        }
    } else {
        for (i = 0, n = array->length; i < n; i++) {
            if (vector[i] == elt)
                return i;
        }
    }
    return XML_NOT_FOUND;
}

/*
 * Grow array vector capacity by powers of two to LINEAR_THRESHOLD, and after
 * that, grow by LINEAR_INCREMENT.  Both must be powers of two, and threshold
 * should be greater than increment.
 */
#define LINEAR_THRESHOLD        256
#define LINEAR_INCREMENT        32

static JSBool
XMLArrayAddMember(JSContext *cx, JSXMLArray *array, uint32 index, void *elt)
{
    uint32 capacity, i;
    int log2;
    void **vector;

    if (index >= array->length) {
        if (index >= array->capacity) {
            capacity = index + 1;
            if (index >= LINEAR_THRESHOLD) {
                capacity = JS_ROUNDUP(capacity, LINEAR_INCREMENT);
            } else {
                JS_CEILING_LOG2(log2, capacity);
                capacity = JS_BIT(log2);
            }
            if ((size_t)capacity > ~(size_t)0 / sizeof(void *) ||
                !(vector = (void **)
                           realloc(array->vector, capacity * sizeof(void *)))) {
                JS_ReportOutOfMemory(cx);
                return JS_FALSE;
            }
            array->capacity = capacity;
            array->vector = vector;
            for (i = array->length; i < index; i++)
                vector[i] = NULL;
        }
        array->length = index + 1;
    }

    array->vector[index] = elt;
    return JS_TRUE;
}

static JSBool
XMLArrayInsert(JSContext *cx, JSXMLArray *array, uint32 i, uint32 n)
{
    uint32 j;
    JSXMLArrayCursor *cursor;

    j = array->length;
    JS_ASSERT(i <= j);
    if (!XMLArraySetCapacity(cx, array, j + n))
        return JS_FALSE;

    array->length = j + n;
    JS_ASSERT(n != (uint32)-1);
    while (j != i) {
        --j;
        array->vector[j + n] = array->vector[j];
    }

    for (cursor = array->cursors; cursor; cursor = cursor->next) {
        if (cursor->index > i)
            cursor->index += n;
    }
    return JS_TRUE;
}

static void *
XMLArrayDelete(JSContext *cx, JSXMLArray *array, uint32 index, JSBool compress)
{
    uint32 length;
    void **vector, *elt;
    JSXMLArrayCursor *cursor;

    length = array->length;
    if (index >= length)
        return NULL;

    vector = array->vector;
    elt = vector[index];
    if (compress) {
        while (++index < length)
            vector[index-1] = vector[index];
        array->length = length - 1;
    } else {
        vector[index] = NULL;
    }

    for (cursor = array->cursors; cursor; cursor = cursor->next) {
        if (cursor->index > index)
            --cursor->index;
    }
    return elt;
}

static void
XMLArrayTruncate(JSContext *cx, JSXMLArray *array, uint32 length)
{
    void **vector;

    JS_ASSERT(!array->cursors);
    if (length >= array->length)
        return;

    if (length == 0) {
        if (array->vector)
            free(array->vector);
        vector = NULL;
    } else {
        vector = realloc(array->vector, length * sizeof(void *));
        if (!vector)
            return;
    }

    if (array->length > length)
        array->length = length;
    array->capacity = length;
    array->vector = vector;
}

#define XMLARRAY_INIT(x,a,n)        XMLArrayInit(x, a, n)
#define XMLARRAY_FINISH(x,a,d)      XMLArrayFinish(x, a, (JSXMLArrayElemDtor)d)
#define XMLARRAY_FIND_MEMBER(a,e,f) XMLArrayFindMember(a, (void *)(e), f)
#define XMLARRAY_HAS_MEMBER(a,e,f)  (XMLArrayFindMember(a, (void *)(e), f) != \
                                     XML_NOT_FOUND)
#define XMLARRAY_MEMBER(a,i,t)      ((t *) (a)->vector[i])
#define XMLARRAY_SET_MEMBER(a,i,e)  ((a)->vector[i] = (void *)(e))
#define XMLARRAY_ADD_MEMBER(x,a,i,e)XMLArrayAddMember(x, a, i, (void *)(e))
#define XMLARRAY_INSERT(x,a,i,n)    XMLArrayInsert(x, a, i, n)
#define XMLARRAY_APPEND(x,a,e)      XMLARRAY_ADD_MEMBER(x, a, (a)->length, (e))
#define XMLARRAY_DELETE(x,a,i,c,t)  ((t *) XMLArrayDelete(x, a, i, c))
#define XMLARRAY_TRUNCATE(x,a,n)    XMLArrayTruncate(x, a, n)

/*
 * Define XML setting property strings and constants early, so everyone can
 * use the same names and their magic numbers (tinyids, flags).
 */
static const char js_ignoreComments_str[]   = "ignoreComments";
static const char js_ignoreProcessingInstructions_str[]
                                            = "ignoreProcessingInstructions";
static const char js_ignoreWhitespace_str[] = "ignoreWhitespace";
static const char js_prettyPrinting_str[]   = "prettyPrinting";
static const char js_prettyIndent_str[]     = "prettyIndent";

/*
 * NB: These XML static property tinyids must
 * (a) not collide with the generic negative tinyids at the top of jsfun.c;
 * (b) index their corresponding xml_static_props array elements.
 * Don't change 'em!
 */
enum xml_static_tinyid {
    XML_IGNORE_COMMENTS,
    XML_IGNORE_PROCESSING_INSTRUCTIONS,
    XML_IGNORE_WHITESPACE,
    XML_PRETTY_PRINTING,
    XML_PRETTY_INDENT
};

static JSBool
xml_setting_setter(JSContext *cx, JSObject *obj, jsval id, jsval *vp)
{
    JSBool b;
    uint8 flag;

    JS_ASSERT(JSVAL_IS_INT(id));
    if (!js_ValueToBoolean(cx, *vp, &b))
        return JS_FALSE;

    flag = JS_BIT(JSVAL_TO_INT(id));
    if (b)
        cx->xmlSettingFlags |= flag;
    else
        cx->xmlSettingFlags &= ~flag;
    return JS_TRUE;
}

static JSPropertySpec xml_static_props[] = {
    {js_ignoreComments_str,     XML_IGNORE_COMMENTS,   JSPROP_PERMANENT,
                                NULL, xml_setting_setter},
    {js_ignoreProcessingInstructions_str,
                   XML_IGNORE_PROCESSING_INSTRUCTIONS, JSPROP_PERMANENT,
                                NULL, xml_setting_setter},
    {js_ignoreWhitespace_str,   XML_IGNORE_WHITESPACE, JSPROP_PERMANENT,
                                NULL, xml_setting_setter},
    {js_prettyPrinting_str,     XML_PRETTY_PRINTING,   JSPROP_PERMANENT,
                                NULL, xml_setting_setter},
    {js_prettyIndent_str,       XML_PRETTY_INDENT,     JSPROP_PERMANENT,
                                NULL, NULL},
    {0,0,0,0,0}
};

/* Derive cx->xmlSettingFlags bits from xml_static_props tinyids. */
#define XSF_IGNORE_COMMENTS     JS_BIT(XML_IGNORE_COMMENTS)
#define XSF_IGNORE_PROCESSING_INSTRUCTIONS                                    \
                                JS_BIT(XML_IGNORE_PROCESSING_INSTRUCTIONS)
#define XSF_IGNORE_WHITESPACE   JS_BIT(XML_IGNORE_WHITESPACE)
#define XSF_PRETTY_PRINTING     JS_BIT(XML_PRETTY_PRINTING)
#define XSF_CACHE_VALID         JS_BIT(XML_PRETTY_INDENT)

/*
 * Extra, unrelated but necessarily disjoint flag used by ParseNodeToXML.
 * This flag means a couple of things:
 *
 * - The top JSXML created for a parse tree must have an object owning it.
 *
 * - That the default namespace normally inherited from the temporary
 *   <parent xmlns='...'> tag that wraps a runtime-concatenated XML source
 *   string must, in the case of a precompiled XML object tree, inherit via
 *   ad-hoc code in ParseNodeToXML.
 *
 * Because of the second purpose, we name this flag XSF_PRECOMPILED_ROOT.
 */
#define XSF_PRECOMPILED_ROOT    (XSF_CACHE_VALID << 1)

/* Macros for special-casing xmlns= and xmlns:foo= in ParseNodeToQName. */
#define IS_XMLNS(str)                                                         \
    (JSSTRING_LENGTH(str) == 5 && IS_XMLNS_CHARS(JSSTRING_CHARS(str)))

#define IS_XMLNS_CHARS(chars)                                                 \
    ((chars)[0] == 'x' && (chars)[1] == 'm' && (chars)[2] == 'l' &&           \
     (chars)[3] == 'n' && (chars)[4] == 's')

static JSXMLQName *
ParseNodeToQName(JSContext *cx, JSParseNode *pn, JSXMLArray *inScopeNSes,
                 JSBool isAttributeName)
{
    JSString *str, *uri, *prefix, *localName;
    size_t length, offset;
    const jschar *start, *limit, *colon;
    uint32 n;
    JSXMLNamespace *ns;

    JS_ASSERT(pn->pn_arity == PN_NULLARY);
    str = ATOM_TO_STRING(pn->pn_atom);
    length = JSSTRING_LENGTH(str);
    start = JSSTRING_CHARS(str);
    JS_ASSERT(length != 0 && *start != '@');
    JS_ASSERT(length != 1 || *start != '*');

    uri = cx->runtime->emptyString;
    limit = start + length;
    colon = js_strchr_limit(start, ':', limit);
    if (colon) {
        offset = PTRDIFF(colon, start, jschar);
        prefix = js_NewDependentString(cx, str, 0, offset, 0);
        if (!prefix)
            return NULL;

        if (!IS_XMLNS(prefix)) {
            uri = NULL;
            n = inScopeNSes->length;
            while (n != 0) {
                ns = XMLARRAY_MEMBER(inScopeNSes, --n, JSXMLNamespace);
                if (ns->prefix && !js_CompareStrings(ns->prefix, prefix)) {
                    uri = ns->uri;
                    break;
                }
            }
            if (!uri) {
                js_ReportCompileErrorNumber(cx, pn,
                                            JSREPORT_PN | JSREPORT_ERROR,
                                            JSMSG_BAD_XML_NAMESPACE,
                                            js_ValueToPrintableString(cx,
                                                STRING_TO_JSVAL(prefix)));
                return NULL;
            }
        }

        localName = js_NewStringCopyN(cx, colon + 1, length - (offset + 1), 0);
        if (!localName)
            return NULL;
    } else {
        if (isAttributeName) {
            /*
             * An unprefixed attribute is not in any namespace, so set prefix
             * as well as uri to the empty string.
             */
            prefix = uri;
        } else {
            /*
             * Loop from back to front looking for the closest declared default
             * namespace.
             */
            n = inScopeNSes->length;
            while (n != 0) {
                ns = XMLARRAY_MEMBER(inScopeNSes, --n, JSXMLNamespace);
                if (!ns->prefix || IS_EMPTY(ns->prefix)) {
                    uri = ns->uri;
                    break;
                }
            }
            prefix = NULL;
        }
        localName = str;
    }

    return js_NewXMLQName(cx, uri, prefix, localName);
}

static JSString *
ChompXMLWhitespace(JSContext *cx, JSString *str)
{
    size_t length, newlength, offset;
    const jschar *cp, *start, *end;
    jschar c;

    length = JSSTRING_LENGTH(str);
    for (cp = start = JSSTRING_CHARS(str), end = cp + length; cp < end; cp++) {
        c = *cp;
        if (!JS_ISXMLSPACE(c))
            break;
    }
    while (end > cp) {
        c = end[-1];
        if (!JS_ISXMLSPACE(c))
            break;
        --end;
    }
    newlength = PTRDIFF(end, cp, jschar);
    if (newlength == length)
        return str;
    offset = PTRDIFF(cp, start, jschar);
    return js_NewDependentString(cx, str, offset, newlength, 0);
}

static JSXML *
ParseNodeToXML(JSContext *cx, JSParseNode *pn, JSXMLArray *inScopeNSes,
               uintN flags)
{
    JSXML *xml, *kid, *attr;
    JSBool inLRS;
    JSString *str;
    uint32 length, n, i;
    JSParseNode *pn2, *next, **pnp;
    JSXMLNamespace *ns;
    JSXMLQName *qn;
    JSXMLClass xml_class;

#define PN2X_SKIP_CHILD ((JSXML *) 1)

    /*
     * Cases return early to avoid common code that gets an outermost xml's
     * object, which protects GC-things owned by xml and its descendants from
     * garbage collection.
     */
    xml = NULL;
    inLRS = JS_FALSE;
    switch (pn->pn_type) {
      case TOK_XMLELEM:
        length = inScopeNSes->length;
        pn2 = pn->pn_head;
        xml = ParseNodeToXML(cx, pn2, inScopeNSes, flags);
        if (!xml)
            return NULL;
        flags &= ~XSF_PRECOMPILED_ROOT;

        n = pn->pn_count;
        JS_ASSERT(n >= 2);
        n -= 2;
        if (!XMLArraySetCapacity(cx, &xml->xml_kids, n))
            goto fail;

        i = 0;
        while ((pn2 = pn2->pn_next) != NULL) {
            next = pn2->pn_next;
            if (!next) {
                /* Don't append the end tag! */
                JS_ASSERT(pn2->pn_type == TOK_XMLETAGO);
                break;
            }

            if ((flags & XSF_IGNORE_WHITESPACE) &&
                n > 1 && pn2->pn_type == TOK_XMLSPACE) {
                --n;
                continue;
            }

            kid = ParseNodeToXML(cx, pn2, inScopeNSes, flags);
            if (kid == PN2X_SKIP_CHILD) {
                --n;
                continue;
            }

            if (!kid) {
                xml->xml_kids.length = i;
                goto fail;
            }

            /* XXX where is this documented in an XML spec, or in E4X? */
            if ((flags & XSF_IGNORE_WHITESPACE) &&
                n > 1 && kid->xml_class == JSXML_CLASS_TEXT) {
                str = ChompXMLWhitespace(cx, kid->xml_value);
                if (!str)
                    goto fail;
                kid->xml_value = str;
            }

            XMLARRAY_SET_MEMBER(&xml->xml_kids, i, kid);
            kid->parent = xml;
            ++i;
        }

        JS_ASSERT(i == n);
        xml->xml_kids.length = n;
        if (n < pn->pn_count - 2)
            XMLArrayTrim(&xml->xml_kids);
        XMLARRAY_TRUNCATE(cx, inScopeNSes, length);
        return xml;

      case TOK_XMLLIST:
        xml = js_NewXML(cx, JSXML_CLASS_LIST);
        if (!xml)
            return NULL;

        if ((flags & XSF_PRECOMPILED_ROOT) && !js_GetXMLObject(cx, xml))
            goto fail;

        n = pn->pn_count;
        if (!XMLArraySetCapacity(cx, &xml->xml_kids, n))
            goto fail;

        i = 0;
        for (pn2 = pn->pn_head; pn2; pn2 = pn2->pn_next) {
            /*
             * Always ignore insignificant whitespace in lists -- we shouldn't
             * condition this on an XML.ignoreWhitespace setting when the list
             * constructor is XMLList (note XML/XMLList unification hazard).
             */
            if (pn2->pn_type == TOK_XMLSPACE) {
                --n;
                continue;
            }

            kid = ParseNodeToXML(cx, pn2, inScopeNSes, flags);
            if (kid == PN2X_SKIP_CHILD) {
                --n;
                continue;
            }

            if (!kid) {
                xml->xml_kids.length = i;
                goto fail;
            }

            XMLARRAY_SET_MEMBER(&xml->xml_kids, i, kid);
            ++i;
        }

        xml->xml_kids.length = n;
        if (n < pn->pn_count)
            XMLArrayTrim(&xml->xml_kids);
        return xml;

      case TOK_XMLSTAGO:
      case TOK_XMLPTAGC:
        length = inScopeNSes->length;
        pn2 = pn->pn_head;
        JS_ASSERT(pn2->pn_type = TOK_XMLNAME);
        if (pn2->pn_arity == PN_LIST)
            goto syntax;

        xml = js_NewXML(cx, JSXML_CLASS_ELEMENT);
        if (!xml)
            goto fail;
        inLRS = JS_EnterLocalRootScope(cx);
        if (!inLRS)
            goto fail;

        /* First pass: check syntax and process namespace declarations. */
        JS_ASSERT(pn->pn_count >= 1);
        n = pn->pn_count - 1;
        pnp = &pn2->pn_next;
        while ((pn2 = *pnp) != NULL) {
            size_t length;
            const jschar *chars;

            if (pn2->pn_type != TOK_XMLNAME || pn2->pn_arity != PN_NULLARY)
                goto syntax;

            str = ATOM_TO_STRING(pn2->pn_atom);
            pn2 = pn2->pn_next;
            JS_ASSERT(pn2);
            if (pn2->pn_type != TOK_XMLATTR)
                goto syntax;

            length = JSSTRING_LENGTH(str);
            chars = JSSTRING_CHARS(str);
            if (length >= 5 &&
                IS_XMLNS_CHARS(chars) &&
                (length == 5 || chars[5] == ':')) {
                JSString *uri, *prefix;

                uri = ATOM_TO_STRING(pn2->pn_atom);
                if (length == 5) {
                    prefix = IS_EMPTY(uri) ? uri : NULL;
                } else {
                    prefix = js_NewStringCopyN(cx, chars + 6, length - 6, 0);
                    if (!prefix)
                        goto fail;
                }

                /*
                 * Once the new ns is appended to xml->xml_namespaces, it is
                 * protected from GC by the object that owns xml -- which is
                 * either xml->object if outermost, or the object owning xml's
                 * oldest ancestor if !outermost.
                 */
                ns = js_NewXMLNamespace(cx, prefix, uri, JS_TRUE);
                if (!ns)
                    goto fail;

                /*
                 * Don't add a namespace that's already in scope.  If someone
                 * extracts a child property from its parent via [[Get]], then
                 * we enforce the invariant, noted many times in ECMA-357, that
                 * the child's namespaces form a possibly-improper superset of
                 * its ancestors' namespaces.
                 */
                if (XMLARRAY_HAS_MEMBER(inScopeNSes, ns, namespace_identity)) {
                    js_DestroyXMLNamespace(cx, ns);
                } else {
                    if (!XMLARRAY_APPEND(cx, inScopeNSes, ns) ||
                        !XMLARRAY_APPEND(cx, &xml->xml_namespaces, ns)) {
                        js_DestroyXMLNamespace(cx, ns);
                        goto fail;
                    }
                }

                JS_ASSERT(n >= 2);
                n -= 2;
                *pnp = pn2->pn_next;
                /* XXXbe recycle pn2 */
                continue;
            }

            pnp = &pn2->pn_next;
        }

        /*
         * If called from js_ParseNodeToXMLObject, emulate the effect of the
         * <parent xmlns='%s'>...</parent> wrapping done by "ToXML Applied to
         * the String Type" (ECMA-357 10.3.1).
         */
        if (flags & XSF_PRECOMPILED_ROOT) {
            JS_ASSERT(length >= 1);
            ns = XMLARRAY_MEMBER(inScopeNSes, 0, JSXMLNamespace);
            ns = js_NewXMLNamespace(cx, ns->prefix, ns->uri, JS_FALSE);
            if (!ns)
                goto fail;
            if (!XMLARRAY_APPEND(cx, &xml->xml_namespaces, ns)) {
                js_DestroyXMLNamespace(cx, ns);
                goto fail;
            }
        }
        XMLArrayTrim(&xml->xml_namespaces);

        /* Second pass: process tag name and attributes, using namespaces. */
        pn2 = pn->pn_head;
        qn = ParseNodeToQName(cx, pn2, inScopeNSes, JS_FALSE);
        if (!qn)
            goto fail;
        xml->name = qn;

        JS_ASSERT((n & 1) == 0);
        n >>= 1;
        if (!XMLArraySetCapacity(cx, &xml->xml_attrs, n))
            goto fail;

        for (i = 0; (pn2 = pn2->pn_next) != NULL; i++) {
            qn = ParseNodeToQName(cx, pn2, inScopeNSes, JS_TRUE);
            if (!qn) {
                xml->xml_attrs.length = i;
                goto fail;
            }

            pn2 = pn2->pn_next;
            JS_ASSERT(pn2);
            JS_ASSERT(pn2->pn_type == TOK_XMLATTR);

            attr = js_NewXML(cx, JSXML_CLASS_ATTRIBUTE);
            if (!attr) {
                js_DestroyXMLQName(cx, qn);
                xml->xml_attrs.length = i;
                goto fail;
            }

            XMLARRAY_SET_MEMBER(&xml->xml_attrs, i, attr);
            attr->parent = xml;
            attr->name = qn;
            attr->xml_value = ATOM_TO_STRING(pn2->pn_atom);
        }

        xml->xml_attrs.length = n;

        /* Point tag closes its own namespace scope. */
        if (pn->pn_type == TOK_XMLPTAGC)
            XMLARRAY_TRUNCATE(cx, inScopeNSes, length);
        break;

      case TOK_XMLSPACE:
      case TOK_XMLTEXT:
      case TOK_XMLCDATA:
      case TOK_XMLCOMMENT:
      case TOK_XMLPI:
        str = ATOM_TO_STRING(pn->pn_atom);
        qn = NULL;
        if (pn->pn_type == TOK_XMLCOMMENT) {
            if (flags & XSF_IGNORE_COMMENTS)
                return PN2X_SKIP_CHILD;
            xml_class = JSXML_CLASS_COMMENT;
        } else if (pn->pn_type == TOK_XMLPI) {
            if (flags & XSF_IGNORE_PROCESSING_INSTRUCTIONS)
                return PN2X_SKIP_CHILD;
            inLRS = JS_EnterLocalRootScope(cx);
            if (!inLRS)
                goto fail;
            qn = ParseNodeToQName(cx, pn, inScopeNSes, JS_FALSE);
            if (!qn)
                goto fail;

            str = pn->pn_atom2
                  ? ATOM_TO_STRING(pn->pn_atom2)
                  : cx->runtime->emptyString;
            xml_class = JSXML_CLASS_PROCESSING_INSTRUCTION;
        } else {
            /* CDATA section content, or element text. */
            xml_class = JSXML_CLASS_TEXT;
        }

        xml = js_NewXML(cx, xml_class);
        if (!xml) {
            if (qn)
                js_DestroyXMLQName(cx, qn);
            goto fail;
        }
        xml->name = qn;
        if (pn->pn_type == TOK_XMLSPACE)
            xml->xml_flags |= XMLF_WHITESPACE_TEXT;
        xml->xml_value = str;
        break;

      default:
        goto syntax;
    }

    if (inLRS)
        JS_LeaveLocalRootScope(cx);
    if ((flags & XSF_PRECOMPILED_ROOT) && !js_GetXMLObject(cx, xml)) {
        js_DestroyXML(cx, xml);
        return NULL;
    }
    return xml;

#undef PN2X_SKIP_CHILD

syntax:
    js_ReportCompileErrorNumber(cx, pn, JSREPORT_PN | JSREPORT_ERROR,
                                JSMSG_BAD_XML_MARKUP);
fail:
    if (inLRS)
        JS_LeaveLocalRootScope(cx);
    if (xml)
        js_DestroyXML(cx, xml);
    return NULL;
}

/*
 * XML helper, object-ops, and library functions.  We start with the helpers,
 * in ECMA-357 order, but merging XML (9.1) and XMLList (9.2) helpers.
 */
static JSBool
GetXMLSetting(JSContext *cx, const char *name, jsval *vp)
{
    jsval v;

    if (!js_FindConstructor(cx, NULL, js_XML_str, &v))
        return JS_FALSE;
    if (!JSVAL_IS_FUNCTION(cx, v)) {
        *vp = JSVAL_VOID;
        return JS_TRUE;
    }
    return JS_GetProperty(cx, JSVAL_TO_OBJECT(v), name, vp);
}

static JSBool
GetBooleanXMLSetting(JSContext *cx, const char *name, JSBool *bp)
{
    int i;
    jsval v;

    if (cx->xmlSettingFlags & XSF_CACHE_VALID) {
        for (i = 0; xml_static_props[i].name; i++) {
            if (!strcmp(xml_static_props[i].name, name)) {
                *bp = (cx->xmlSettingFlags & JS_BIT(i)) != 0;
                return JS_TRUE;
            }
        }
        *bp = JS_FALSE;
        return JS_TRUE;
    }

    return GetXMLSetting(cx, name, &v) && js_ValueToBoolean(cx, v, bp);
}

static JSBool
GetUint32XMLSetting(JSContext *cx, const char *name, uint32 *uip)
{
    jsval v;

    return GetXMLSetting(cx, name, &v) && js_ValueToECMAUint32(cx, v, uip);
}

static JSBool
GetXMLSettingFlags(JSContext *cx, uintN *flagsp)
{
    JSBool flag;

    /* Just get the first flag to validate the setting flags cache. */
    if (!GetBooleanXMLSetting(cx, js_ignoreComments_str, &flag))
        return JS_FALSE;
    *flagsp = cx->xmlSettingFlags;
    return JS_TRUE;
}

static JSXML *
ParseXMLSource(JSContext *cx, JSString *src)
{
    jsval nsval;
    JSXMLNamespace *ns;
    size_t urilen, srclen, length, offset;
    jschar *chars;
    const jschar *srcp, *endp;
    void *mark;
    JSTokenStream *ts;
    uintN lineno;
    JSStackFrame *fp;
    JSOp op;
    JSParseNode *pn;
    JSXML *xml;
    JSXMLArray nsarray;
    uintN flags;

    static const char prefix[] = "<parent xmlns='";
    static const char middle[] = "'>";
    static const char suffix[] = "</parent>";

#define constrlen(constr)   (sizeof(constr) - 1)

    if (!js_GetDefaultXMLNamespace(cx, &nsval))
        return NULL;
    ns = (JSXMLNamespace *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(nsval));

    urilen = JSSTRING_LENGTH(ns->uri);
    srclen = JSSTRING_LENGTH(src);
    length = constrlen(prefix) + urilen + constrlen(middle) + srclen +
             constrlen(suffix);

    chars = (jschar *) JS_malloc(cx, (length + 1) * sizeof(jschar));
    if (!chars)
        return NULL;

    js_InflateStringToBuffer(chars, prefix, constrlen(prefix));
    offset = constrlen(prefix);
    js_strncpy(chars + offset, JSSTRING_CHARS(ns->uri), urilen);
    offset += urilen;
    js_InflateStringToBuffer(chars + offset, middle, constrlen(middle));
    offset += constrlen(middle);
    srcp = JSSTRING_CHARS(src);
    js_strncpy(chars + offset, srcp, srclen);
    offset += srclen;
    js_InflateStringToBuffer(chars + offset, suffix, constrlen(suffix));

    mark = JS_ARENA_MARK(&cx->tempPool);
    ts = js_NewBufferTokenStream(cx, chars, length);
    if (!ts)
        return NULL;
    for (fp = cx->fp; fp && !fp->pc; fp = fp->down)
        continue;
    if (fp) {
        op = (JSOp) *fp->pc;
        if (op == JSOP_TOXML || op == JSOP_TOXMLLIST) {
            ts->filename = fp->script->filename;
            lineno = js_PCToLineNumber(cx, fp->script, fp->pc);
            for (endp = srcp + srclen; srcp < endp; srcp++)
                if (*srcp == '\n')
                    --lineno;
            ts->lineno = lineno;
        }
    }

    xml = NULL;
    JS_KEEP_ATOMS(cx->runtime);
    pn = js_ParseXMLTokenStream(cx, cx->fp->scopeChain, ts, JS_FALSE);
    if (pn && XMLARRAY_INIT(cx, &nsarray, 1)) {
        if (GetXMLSettingFlags(cx, &flags))
            xml = ParseNodeToXML(cx, pn, &nsarray, flags);

        XMLARRAY_FINISH(cx, &nsarray, NULL);
    }
    JS_UNKEEP_ATOMS(cx->runtime);

    JS_ARENA_RELEASE(&cx->tempPool, mark);
    JS_free(cx, chars);
    return xml;

#undef constrlen
}

/*
 * Errata in 10.3.1, 10.4.1, and 13.4.4.24 (at least).
 *
 * 10.3.1 Step 6(a) fails to NOTE that implementations that do not enforce
 * the constraint:
 *
 *     for all x belonging to XML:
 *         x.[[InScopeNamespaces]] >= x.[[Parent]].[[InScopeNamespaces]]
 *
 * must union x.[[InScopeNamespaces]] into x[0].[[InScopeNamespaces]] here
 * (in new sub-step 6(a), renumbering the others to (b) and (c)).
 *
 * Same goes for 10.4.1 Step 7(a).
 *
 * In order for XML.prototype.namespaceDeclarations() to work correctly, the
 * default namespace thereby unioned into x[0].[[InScopeNamespaces]] must be
 * flagged as not declared, so that 13.4.4.24 Step 8(a) can exclude all such
 * undeclared namespaces associated with x not belonging to ancestorNS.
 */
static JSXML *
OrphanXMLChild(JSContext *cx, JSXML *xml, uint32 i)
{
    JSXMLNamespace *ns;

    ns = XMLARRAY_MEMBER(&xml->xml_namespaces, 0, JSXMLNamespace);
    xml = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
    if (xml->xml_class == JSXML_CLASS_ELEMENT) {
        if (!js_GetXMLNamespaceObject(cx, ns))
            return NULL;
        if (!XMLARRAY_APPEND(cx, &xml->xml_namespaces, ns))
            return NULL;
        ns->declared = JS_FALSE;
    }
    xml->parent = NULL;
    return xml;
}

static JSObject *
ToXML(JSContext *cx, jsval v)
{
    JSObject *obj;
    JSXML *xml;
    JSClass *clasp;
    JSString *str;
    uint32 length;

    if (JSVAL_IS_PRIMITIVE(v)) {
        if (JSVAL_IS_NULL(v) || JSVAL_IS_VOID(v))
            goto bad;
    } else {
        obj = JSVAL_TO_OBJECT(v);
        if (OBJECT_IS_XML(cx, obj)) {
            xml = (JSXML *) JS_GetPrivate(cx, obj);
            if (xml->xml_class == JSXML_CLASS_LIST) {
                if (xml->xml_kids.length != 1)
                    goto bad;
                xml = XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML);
                JS_ASSERT(xml->xml_class != JSXML_CLASS_LIST);
                return js_GetXMLObject(cx, xml);
            }
            return obj;
        }

        clasp = OBJ_GET_CLASS(cx, obj);
        if (clasp->flags & JSCLASS_DOCUMENT_OBSERVER) {
            JS_ASSERT(0);
        }

        if (clasp != &js_StringClass &&
            clasp != &js_NumberClass &&
            clasp != &js_BooleanClass) {
            goto bad;
        }
    }

    str = js_ValueToString(cx, v);
    if (!str)
        return NULL;
    if (IS_EMPTY(str)) {
        length = 0;
    } else {
        xml = ParseXMLSource(cx, str);
        if (!xml)
            return NULL;
        length = JSXML_LENGTH(xml);
    }

    if (length == 0) {
        obj = js_NewXMLObject(cx, JSXML_CLASS_TEXT);
        if (!obj)
            return NULL;
    } else if (length == 1) {
        xml = OrphanXMLChild(cx, xml, 0);
        if (!xml)
            return NULL;
        obj = js_GetXMLObject(cx, xml);
        if (!obj)
            return NULL;
    } else {
        JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL, JSMSG_SYNTAX_ERROR);
        return NULL;
    }
    return obj;

bad:
    str = js_DecompileValueGenerator(cx, JSDVG_IGNORE_STACK, v, NULL);
    if (str) {
        JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                             JSMSG_BAD_XML_CONVERSION,
                             JS_GetStringBytes(str));
    }
    return NULL;
}

static JSBool
Append(JSContext *cx, JSXML *list, JSXML *kid);

static JSObject *
ToXMLList(JSContext *cx, jsval v)
{
    JSObject *obj, *listobj;
    JSXML *xml, *list, *kid;
    JSClass *clasp;
    JSString *str;
    uint32 i, length;

    if (JSVAL_IS_PRIMITIVE(v)) {
        if (JSVAL_IS_NULL(v) || JSVAL_IS_VOID(v))
            goto bad;
    } else {
        obj = JSVAL_TO_OBJECT(v);
        if (OBJECT_IS_XML(cx, obj)) {
            xml = (JSXML *) JS_GetPrivate(cx, obj);
            if (xml->xml_class != JSXML_CLASS_LIST) {
                listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
                if (!listobj)
                    return NULL;
                list = (JSXML *) JS_GetPrivate(cx, listobj);
                if (!Append(cx, list, xml))
                    return NULL;
                return listobj;
            }
            return obj;
        }

        clasp = OBJ_GET_CLASS(cx, obj);
        if (clasp->flags & JSCLASS_DOCUMENT_OBSERVER) {
            JS_ASSERT(0);
        }

        if (clasp != &js_StringClass &&
            clasp != &js_NumberClass &&
            clasp != &js_BooleanClass) {
            goto bad;
        }
    }

    str = js_ValueToString(cx, v);
    if (!str)
        return NULL;
    if (IS_EMPTY(str)) {
        xml = NULL;
        length = 0;
    } else {
        if (!JS_EnterLocalRootScope(cx))
            return NULL;
        xml = ParseXMLSource(cx, str);
        if (!xml) {
            JS_LeaveLocalRootScope(cx);
            return NULL;
        }
        length = JSXML_LENGTH(xml);
    }

    listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
    if (listobj) {
        list = (JSXML *) JS_GetPrivate(cx, listobj);
        for (i = 0; i < length; i++) {
            kid = OrphanXMLChild(cx, xml, i);
            if (!kid)
                return NULL;
            if (!Append(cx, list, kid)) {
                listobj = NULL;
                break;
            }
        }
    }

    if (xml)
        JS_LeaveLocalRootScope(cx);
    return listobj;

bad:
    str = js_DecompileValueGenerator(cx, JSDVG_IGNORE_STACK, v, NULL);
    if (str) {
        JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                             JSMSG_BAD_XMLLIST_CONVERSION,
                             JS_GetStringBytes(str));
    }
    return NULL;
}

/*
 * ECMA-357 10.2.1 17(d-g) pulled out into a common subroutine that appends
 * equals, a double quote, an attribute value, and a closing double quote.
 */
static void
AppendAttributeValue(JSContext *cx, JSStringBuffer *sb, JSString *valstr)
{
    js_AppendCString(sb, "=\"");
    valstr = js_EscapeAttributeValue(cx, valstr);
    if (!valstr) {
        free(sb->base);
        sb->base = STRING_BUFFER_ERROR_BASE;
        return;
    }
    js_AppendJSString(sb, valstr);
    js_AppendChar(sb, '"');
}

/*
 * ECMA-357 10.2.1.1 EscapeElementValue helper method.
 * This function takes ownership of sb->base, if sb is non-null, in all cases.
 */
static JSString *
EscapeElementValue(JSContext *cx, JSStringBuffer *sb, JSString *str)
{
    size_t length, newlength;
    const jschar *cp, *start, *end;
    jschar c;

    length = newlength = JSSTRING_LENGTH(str);
    for (cp = start = JSSTRING_CHARS(str), end = cp + length; cp < end; cp++) {
        c = *cp;
        if (c == '<'
#if 0
            /*
             * XXX Erratum: escaping > is unnecessary, and doing so breaks
             *     tests/e4x/Expressions/11.1.4.js Section 19.
             */
            || c == '>'
#endif
            ) {
            newlength += 3;
        } else if (c == '&') {
            newlength += 4;
        }
    }
    if ((sb && STRING_BUFFER_OFFSET(sb) != 0) || newlength > length) {
        JSStringBuffer localSB;
        if (!sb) {
            sb = &localSB;
            js_InitStringBuffer(sb);
        }
        if (!sb->grow(sb, STRING_BUFFER_OFFSET(sb) + newlength)) {
            JS_ReportOutOfMemory(cx);
            return NULL;
        }
        for (cp = start; cp < end; cp++) {
            c = *cp;
            if (c == '<')
                js_AppendCString(sb, js_lt_entity_str);
#if 0
            else if (c == '>')
                js_AppendCString(sb, js_gt_entity_str);
#endif
            else if (c == '&')
                js_AppendCString(sb, js_amp_entity_str);
            else
                js_AppendChar(sb, c);
        }
        JS_ASSERT(STRING_BUFFER_OK(sb));
        str = js_NewString(cx, sb->base, STRING_BUFFER_OFFSET(sb), 0);
        if (!str)
            js_FinishStringBuffer(sb);
    }
    return str;
}

/*
 * ECMA-357 10.2.1.2 EscapeAttributeValue helper method.
 * This function takes ownership of sb->base, if sb is non-null, in all cases.
 */
static JSString *
EscapeAttributeValue(JSContext *cx, JSStringBuffer *sb, JSString *str)
{
    size_t length, newlength;
    const jschar *cp, *start, *end;
    jschar c;

    length = newlength = JSSTRING_LENGTH(str);
    for (cp = start = JSSTRING_CHARS(str), end = cp + length; cp < end; cp++) {
        c = *cp;
        if (c == '"')
            newlength += 5;
        else if (c == '<')
            newlength += 3;
        else if (c == '&' || c == '\n' || c == '\r' || c == '\t')
            newlength += 4;
    }
    if ((sb && STRING_BUFFER_OFFSET(sb) != 0) || newlength > length) {
        JSStringBuffer localSB;
        if (!sb) {
            sb = &localSB;
            js_InitStringBuffer(sb);
        }
        if (!sb->grow(sb, STRING_BUFFER_OFFSET(sb) + newlength)) {
            JS_ReportOutOfMemory(cx);
            return NULL;
        }
        for (cp = start; cp < end; cp++) {
            c = *cp;
            if (c == '"')
                js_AppendCString(sb, js_quot_entity_str);
            else if (c == '<')
                js_AppendCString(sb, js_lt_entity_str);
            else if (c == '&')
                js_AppendCString(sb, js_amp_entity_str);
            else if (c == '\n')
                js_AppendCString(sb, "&#xA;");
            else if (c == '\r')
                js_AppendCString(sb, "&#xD;");
            else if (c == '\t')
                js_AppendCString(sb, "&#x9;");
            else
                js_AppendChar(sb, c);
        }
        JS_ASSERT(STRING_BUFFER_OK(sb));
        str = js_NewString(cx, sb->base, STRING_BUFFER_OFFSET(sb), 0);
        if (!str)
            js_FinishStringBuffer(sb);
    }
    return str;
}

/* 13.3.5.4 [[GetNamespace]]([InScopeNamespaces]) */
static JSXMLNamespace *
GetNamespace(JSContext *cx, JSXMLQName *qn, JSXMLArray *inScopeNSes)
{
    JSXMLNamespace *match, *ns;
    uint32 i, n;
    jsval argv[1];
    JSObject *nsobj;

    JS_ASSERT(qn->uri);
    if (!qn->uri) {
        JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                             JSMSG_BAD_XML_NAMESPACE,
                             qn->prefix
                             ? js_ValueToPrintableString(cx,
                                   STRING_TO_JSVAL(qn->prefix))
                             : js_type_str[JSTYPE_VOID]);
        return NULL;
    }

    /* Look for a matching namespace in inScopeNSes, if provided. */
    match = NULL;
    if (inScopeNSes) {
        for (i = 0, n = inScopeNSes->length; i < n; i++) {
            ns = XMLARRAY_MEMBER(inScopeNSes, i, JSXMLNamespace);
            if (!js_CompareStrings(ns->uri, qn->uri) &&
                (ns->prefix == qn->prefix ||
                 (ns->prefix && qn->prefix &&
                  !js_CompareStrings(ns->prefix, qn->prefix)))) {
                match = ns;
                break;
            }
        }
    }

    /* If we didn't match, make a new namespace from qn. */
    if (!match) {
        argv[0] = STRING_TO_JSVAL(qn->uri);
        nsobj = js_ConstructObject(cx, &js_NamespaceClass.base, NULL, NULL,
                                   1, argv);
        if (!nsobj)
            return NULL;
        match = (JSXMLNamespace *) JS_GetPrivate(cx, nsobj);
        if (!match->prefix)
            match->prefix = qn->prefix;
    } else {
        /* Share ns reference by converting it to GC'd allocation. */
        if (!js_GetXMLNamespaceObject(cx, match))
            return NULL;
    }
    return match;
}

static JSString *
GeneratePrefix(JSContext *cx, JSString *uri, JSXMLArray *decls)
{
    const jschar *cp, *start, *end;
    size_t length, newlength, offset;
    uint32 i, n, m, serial;
    jschar *bp, *dp;
    JSBool done;
    JSXMLNamespace *ns;
    JSString *prefix;

    JS_ASSERT(!IS_EMPTY(uri));

    /*
     * Try peeling off the last filename suffix or pathname component till
     * we have a valid XML name.  This heuristic will prefer "xul" given
     * ".../there.is.only.xul", "xbl" given ".../xbl", and "xbl2" given any
     * likely URI of the form ".../xbl2/2005".
     */
    start = JSSTRING_CHARS(uri);
    cp = end = start + JSSTRING_LENGTH(uri);
    while (--cp >= start) {
        if (*cp == '.' || *cp == '/') {
            ++cp;
            if (IsXMLName(cp, PTRDIFF(end, cp, jschar)))
                break;
            end = --cp;
        }
    }
    length = PTRDIFF(end, cp, jschar);

    /*
     * Now search through decls looking for a collision.  If we collide with
     * an existing prefix, start tacking on a hyphen and a serial number.
     */
    serial = 0;
    bp = NULL;
#ifdef __GNUC__         /* suppress bogus gcc warnings */
    newlength = 0;
#endif
    do {
        done = JS_TRUE;
        for (i = 0, n = decls->length; i < n; i++) {
            ns = XMLARRAY_MEMBER(decls, i, JSXMLNamespace);
            if (ns->prefix &&
                JSSTRING_LENGTH(ns->prefix) == length &&
                !memcmp(JSSTRING_CHARS(ns->prefix), cp,
                        length * sizeof(jschar))) {
                if (!bp) {
                    newlength = length + 2 + (size_t) log10(n);
                    bp = (jschar *)
                         JS_malloc(cx, (newlength + 1) * sizeof(jschar));
                    if (!bp)
                        return NULL;
                    js_strncpy(bp, cp, length);
                }

                ++serial;
                JS_ASSERT(serial < n);
                dp = bp + length + 2 + (size_t) log10(serial);
                *dp = 0;
                for (m = serial; m != 0; m /= 10)
                    *--dp = (jschar)('0' + m % 10);
                *--dp = '-';
                JS_ASSERT(dp == cp + length);

                done = JS_FALSE;
                break;
            }
        }
    } while (!done);

    if (!bp) {
        offset = PTRDIFF(cp, start, jschar);
        prefix = js_NewDependentString(cx, uri, offset, length, 0);
    } else {
        prefix = js_NewString(cx, bp, newlength, 0);
        if (!prefix)
            JS_free(cx, bp);
    }
    return prefix;
}

/* ECMA-357 10.2.1 and 10.2.2 */
static JSString *
XMLToXMLString(JSContext *cx, JSXML *xml, JSXMLArray *ancestorNSes,
               uintN indentLevel)
{
    JSBool pretty, indentKids;
    JSStringBuffer sb;
    JSString *str, *name, *prefix, *kidstr;
    size_t length, newlength, namelength;
    jschar *bp, *base;
    uint32 i, n;
    JSXMLArray empty, decls, ancdecls;
    JSXMLNamespace *ns, *ns2;
    uintN nextIndentLevel;
    JSXML *attr, *kid;

    static const jschar comment_prefix_ucNstr[] = {'<', '!', '-', '-'};
    static const jschar comment_suffix_ucNstr[] = {'-', '-', '>'};
    static const jschar pi_prefix_ucNstr[] = {'<', '?'};
    static const jschar pi_suffix_ucNstr[] = {'?', '>'};

    if (!GetBooleanXMLSetting(cx, js_prettyPrinting_str, &pretty))
        return NULL;

    js_InitStringBuffer(&sb);
    if (pretty)
        js_RepeatChar(&sb, ' ', indentLevel);
    str = NULL;

    /* XXXbe Erratum? should CDATA be handled specially? */
    switch (xml->xml_class) {
      case JSXML_CLASS_TEXT:
        /* Step 4. */
        if (pretty) {
            str = ChompXMLWhitespace(cx, xml->xml_value);
            if (!str)
                return NULL;
        } else {
            str = xml->xml_value;
        }
        return EscapeElementValue(cx, &sb, str);

      case JSXML_CLASS_ATTRIBUTE:
        /* Step 5. */
        return EscapeAttributeValue(cx, &sb, xml->xml_value);

      case JSXML_CLASS_COMMENT:
        /* Step 6. */
        str = xml->xml_value;
        length = JSSTRING_LENGTH(str);
        newlength = STRING_BUFFER_OFFSET(&sb) + 4 + length + 3;
        bp = base = (jschar *)
                    JS_realloc(cx, sb.base, (newlength + 1) * sizeof(jschar));
        if (!bp) {
            js_FinishStringBuffer(&sb);
            return NULL;
        }

        bp += STRING_BUFFER_OFFSET(&sb);
        js_strncpy(bp, comment_prefix_ucNstr, 4);
        bp += 4;
        js_strncpy(bp, JSSTRING_CHARS(str), length);
        bp += length;
        js_strncpy(bp, comment_suffix_ucNstr, 3);
        bp[3] = 0;
        str = js_NewString(cx, base, newlength, 0);
        if (!str)
            free(base);
        return str;

      case JSXML_CLASS_PROCESSING_INSTRUCTION:
        /* Step 7. */
        name = xml->name->localName;
        namelength = JSSTRING_LENGTH(name);
        str = xml->xml_value;
        length = JSSTRING_LENGTH(str);
        newlength = STRING_BUFFER_OFFSET(&sb) + 2 + namelength + 1 + length + 2;
        bp = base = (jschar *)
                    JS_realloc(cx, sb.base, (newlength + 1) * sizeof(jschar));
        if (!bp) {
            js_FinishStringBuffer(&sb);
            return NULL;
        }

        bp += STRING_BUFFER_OFFSET(&sb);
        js_strncpy(bp, pi_prefix_ucNstr, 2);
        bp += 2;
        js_strncpy(bp, JSSTRING_CHARS(name), namelength);
        bp += namelength;
        *bp++ = (jschar) ' ';
        js_strncpy(bp, JSSTRING_CHARS(str), length);
        bp += length;
        js_strncpy(bp, pi_suffix_ucNstr, 2);
        bp[2] = 0;
        str = js_NewString(cx, base, newlength, 0);
        if (!str)
            free(base);
        return str;

      case JSXML_CLASS_LIST:
        /* ECMA-357 10.2.2. */
        for (i = 0, n = xml->xml_kids.length; i < n; i++) {
            if (pretty && i != 0)
                js_AppendChar(&sb, '\n');

            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            kidstr = XMLToXMLString(cx, kid, ancestorNSes, indentLevel);
            if (!kidstr)
                goto list_out;

            js_AppendJSString(&sb, kidstr);
        }

        if (!sb.base) {
            if (!STRING_BUFFER_OK(&sb)) {
                JS_ReportOutOfMemory(cx);
                return NULL;
            }
            return cx->runtime->emptyString;
        }

        str = js_NewString(cx, sb.base, STRING_BUFFER_OFFSET(&sb), 0);
      list_out:
        if (!str)
            js_FinishStringBuffer(&sb);
        return str;

      default:;
    }

    /* ECMA-357 10.2.1 step 8 onward: handle ToXMLString on an XML element. */
    if (!ancestorNSes) {
        XMLARRAY_INIT(cx, &empty, 0);
        ancestorNSes = &empty;
    }
    XMLARRAY_INIT(cx, &decls, 0);
    ancdecls.capacity = 0;

    /* Clone in-scope namespaces not in ancestorNSes into decls. */
    for (i = 0, n = xml->xml_namespaces.length; i < n; i++) {
        ns = XMLARRAY_MEMBER(&xml->xml_namespaces, i, JSXMLNamespace);
        if (!ns->declared)
            continue;
        if (!XMLARRAY_HAS_MEMBER(ancestorNSes, ns, namespace_identity)) {
            /* NOTE: may want to exclude unused namespaces here. */
            ns2 = js_NewXMLNamespace(cx, ns->prefix, ns->uri, JS_TRUE);
            if (!ns2)
                goto out;
            if (!XMLARRAY_APPEND(cx, &decls, ns2)) {
                js_DestroyXMLNamespace(cx, ns2);
                goto out;
            }
        }
    }

    /*
     * Union ancestorNSes and decls into ancdecls.  Note that ancdecls does
     * not own its member references.  In the spec, ancdecls has no name, but
     * is always written out as (AncestorNamespaces U namespaceDeclarations).
     */
    if (!XMLARRAY_INIT(cx, &ancdecls, ancestorNSes->length + decls.length))
        goto out;
    for (i = 0, n = ancestorNSes->length; i < n; i++) {
        ns2 = XMLARRAY_MEMBER(ancestorNSes, i, JSXMLNamespace);
        JS_ASSERT(!XMLARRAY_HAS_MEMBER(&decls, ns2, namespace_identity));
        if (!XMLARRAY_APPEND(cx, &ancdecls, ns2))
            goto out;
    }
    for (i = 0, n = decls.length; i < n; i++) {
        ns2 = XMLARRAY_MEMBER(&decls, i, JSXMLNamespace);
        JS_ASSERT(!XMLARRAY_HAS_MEMBER(&ancdecls, ns2, namespace_identity));
        if (!XMLARRAY_APPEND(cx, &ancdecls, ns2))
            goto out;
    }

    /* Step 11, except we don't clone ns unless its prefix is undefined. */
    ns = GetNamespace(cx, xml->name, &ancdecls);
    if (!ns)
        goto out;

    /* Step 12 (NULL means *undefined* here), plus the deferred ns cloning. */
    if (!ns->prefix) {
        /*
         * Create a namespace prefix that isn't used by any member of decls.
         * Assign the new prefix to a copy of ns.  Flag this namespace as if
         * it were declared, for assertion-testing's sake later below.
         */
        prefix = GeneratePrefix(cx, ns->uri, &ancdecls);
        if (!prefix)
            goto out;
        ns = js_NewXMLNamespace(cx, prefix, ns->uri, JS_TRUE);
        if (!ns)
            goto out;
        if (!XMLARRAY_APPEND(cx, &decls, ns)) {
            js_DestroyXMLNamespace(cx, ns);
            goto out;
        }
    }

    /* Format the element or point-tag into sb. */
    js_AppendChar(&sb, '<');

    if (ns->prefix && !IS_EMPTY(ns->prefix)) {
        js_AppendJSString(&sb, ns->prefix);
        js_AppendChar(&sb, ':');
    }
    js_AppendJSString(&sb, xml->name->localName);

    /*
     * Step 16 makes a union to avoid writing two loops in step 17, to share
     * common attribute value appending spec-code.  We prefer two loops for
     * faster code and less data overhead.
     */

    /* Step 17(c): append XML namespace declarations. */
    for (i = 0, n = decls.length; i < n; i++) {
        ns2 = XMLARRAY_MEMBER(&decls, i, JSXMLNamespace);
        JS_ASSERT(ns2->declared);

        js_AppendCString(&sb, " xmlns");

        /* 17(c)(ii): NULL means *undefined* here. */
        if (!ns2->prefix) {
            prefix = GeneratePrefix(cx, ns2->uri, &ancdecls);
            if (!prefix)
                goto out;
            ns2->prefix = prefix;
        }

        /* 17(c)(iii). */
        if (!IS_EMPTY(ns2->prefix)) {
            js_AppendChar(&sb, ':');
            js_AppendJSString(&sb, ns2->prefix);
        }

        /* 17(d-g). */
        AppendAttributeValue(cx, &sb, ns2->uri);
    }

    /* Step 17(b): append attributes. */
    for (i = 0, n = xml->xml_attrs.length; i < n; i++) {
        attr = XMLARRAY_MEMBER(&xml->xml_attrs, i, JSXML);
        js_AppendChar(&sb, ' ');
        ns2 = GetNamespace(cx, attr->name, ancestorNSes);
        if (!ns2)
            goto out;

        /* 17(b)(ii): NULL means *undefined* here. */
        if (!ns2->prefix) {
            prefix = GeneratePrefix(cx, ns2->uri, &ancdecls);
            if (!prefix)
                goto out;

            /* Again, we avoid copying ns2 until we know it's prefix-less. */
            ns2 = js_NewXMLNamespace(cx, prefix, ns2->uri, JS_TRUE);
            if (!ns2)
                goto out;
            if (!XMLARRAY_APPEND(cx, &decls, ns2)) {
                js_DestroyXMLNamespace(cx, ns2);
                goto out;
            }
        }

        /* 17(b)(iii). */
        if (!IS_EMPTY(ns2->prefix)) {
            js_AppendJSString(&sb, ns2->prefix);
            js_AppendChar(&sb, ':');
        }

        /* 17(b)(iv). */
        js_AppendJSString(&sb, attr->name->localName);

        /* 17(d-g). */
        AppendAttributeValue(cx, &sb, attr->xml_value);
    }

    /* Step 18: handle point tags. */
    n = xml->xml_kids.length;
    if (n == 0) {
        js_AppendCString(&sb, "/>");
    } else {
        /* Steps 19 through 25: handle element content, and open the end-tag. */
        js_AppendChar(&sb, '>');
        indentKids = n > 1 ||
                     (n == 1 &&
                      XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML)->xml_class
                      != JSXML_CLASS_TEXT);

        if (pretty && indentKids) {
            if (!GetUint32XMLSetting(cx, js_prettyIndent_str, &i))
                return NULL;
            nextIndentLevel = indentLevel + i;
        } else {
            nextIndentLevel = 0;
        }

        for (i = 0; i < n; i++) {
            if (pretty && indentKids)
                js_AppendChar(&sb, '\n');

            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            kidstr = XMLToXMLString(cx, kid, &ancdecls, nextIndentLevel);
            if (!kidstr)
                goto out;

            js_AppendJSString(&sb, kidstr);
        }

        if (pretty && indentKids) {
            js_AppendChar(&sb, '\n');
            js_RepeatChar(&sb, ' ', indentLevel);
        }
        js_AppendCString(&sb, "</");

        /* Step 26. */
        if (ns->prefix && !IS_EMPTY(ns->prefix)) {
            js_AppendJSString(&sb, ns->prefix);
            js_AppendChar(&sb, ':');
        }

        /* Step 27. */
        js_AppendJSString(&sb, xml->name->localName);
        js_AppendChar(&sb, '>');
    }

    if (!STRING_BUFFER_OK(&sb)) {
        JS_ReportOutOfMemory(cx);
        goto out;
    }

    str = js_NewString(cx, sb.base, STRING_BUFFER_OFFSET(&sb), 0);
out:
    if (!str)
        js_FinishStringBuffer(&sb);
    XMLARRAY_FINISH(cx, &decls, js_DestroyXMLNamespace);
    if (ancdecls.capacity != 0)
        XMLARRAY_FINISH(cx, &ancdecls, NULL);
    return str;
}

/* ECMA-357 10.2 */
static JSString *
ToXMLString(JSContext *cx, jsval v)
{
    JSObject *obj;
    JSString *str;
    JSXML *xml;

    if (JSVAL_IS_NULL(v) || JSVAL_IS_VOID(v)) {
        JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                             JSMSG_BAD_XML_CONVERSION,
                             js_type_str[JSVAL_IS_NULL(v)
                                         ? JSTYPE_NULL
                                         : JSTYPE_VOID]);
        return NULL;
    }

    if (JSVAL_IS_BOOLEAN(v) || JSVAL_IS_NUMBER(v))
        return js_ValueToString(cx, v);

    if (JSVAL_IS_STRING(v))
        return EscapeElementValue(cx, NULL, JSVAL_TO_STRING(v));

    obj = JSVAL_TO_OBJECT(v);
    if (!OBJECT_IS_XML(cx, obj)) {
        if (!OBJ_DEFAULT_VALUE(cx, obj, JSTYPE_STRING, &v))
            return NULL;
        str = js_ValueToString(cx, v);
        if (!str)
            return NULL;
        return EscapeElementValue(cx, NULL, str);
    }

    /* Handle non-element cases in this switch, returning from each case. */
    xml = (JSXML *) JS_GetPrivate(cx, obj);
    return XMLToXMLString(cx, xml, NULL, 0);
}

static JSXMLQName *
ToAttributeName(JSContext *cx, jsval v)
{
    JSString *name, *uri, *prefix;
    JSObject *obj;
    JSClass *clasp;
    JSXMLQName *qn;

    if (JSVAL_IS_STRING(v)) {
        name = JSVAL_TO_STRING(v);
        uri = prefix = cx->runtime->emptyString;
    } else {
        if (JSVAL_IS_PRIMITIVE(v)) {
            name = js_DecompileValueGenerator(cx, JSDVG_IGNORE_STACK, v, NULL);
            if (name) {
                JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                                     JSMSG_BAD_XML_ATTRIBUTE_NAME,
                                     JS_GetStringBytes(name));
            }
            return NULL;
        }

        obj = JSVAL_TO_OBJECT(v);
        clasp = OBJ_GET_CLASS(cx, obj);
        if (clasp == &js_AttributeNameClass)
            return (JSXMLQName *) JS_GetPrivate(cx, obj);

        if (clasp == &js_QNameClass.base) {
            qn = (JSXMLQName *) JS_GetPrivate(cx, obj);
            uri = qn->uri;
            prefix = qn->prefix;
            name = qn->localName;
        } else {
            if (clasp == &js_AnyNameClass) {
                name = ATOM_TO_STRING(cx->runtime->atomState.starAtom);
            } else {
                name = js_ValueToString(cx, v);
                if (!name)
                    return NULL;
            }
            uri = prefix = cx->runtime->emptyString;
        }
    }

    qn = js_NewXMLQName(cx, uri, prefix, name);
    if (!qn)
        return NULL;
    if (!js_GetAttributeNameObject(cx, qn)) {
        js_DestroyXMLQName(cx, qn);
        return NULL;
    }
    return qn;
}

static JSXMLQName *
ToXMLName(JSContext *cx, jsval v, jsid *funidp)
{
    JSString *name;
    JSObject *obj;
    JSClass *clasp;
    uint32 index;
    JSXMLQName *qn;
    JSAtom *atom;

    if (JSVAL_IS_STRING(v)) {
        name = JSVAL_TO_STRING(v);
    } else {
        if (JSVAL_IS_PRIMITIVE(v)) {
            name = js_DecompileValueGenerator(cx, JSDVG_IGNORE_STACK, v, NULL);
            if (name)
                goto bad;
            return NULL;
        }

        obj = JSVAL_TO_OBJECT(v);
        clasp = OBJ_GET_CLASS(cx, obj);
        if (clasp == &js_AttributeNameClass || clasp == &js_QNameClass.base)
            goto out;
        if (clasp == &js_AnyNameClass) {
            name = ATOM_TO_STRING(cx->runtime->atomState.starAtom);
            goto construct;
        }
        name = js_ValueToString(cx, v);
        if (!name)
            return NULL;
    }

    /*
     * ECMA-357 10.6.1 step 1 seems to be incorrect.  The spec says:
     *
     * 1. If ToString(ToNumber(P)) == ToString(P), throw a TypeError exception
     *
     * First, _P_ should be _s_, to refer to the given string.
     *
     * Second, why does ToXMLName applied to the string type throw TypeError
     * only for numeric literals without any leading or trailing whitespace?
     *
     * If the idea is to reject uint32 property names, then the check needs to
     * be stricter, to exclude hexadecimal and floating point literals.
     */
    if (js_IdIsIndex(STRING_TO_JSVAL(name), &index))
        goto bad;

    if (*JSSTRING_CHARS(name) == '@') {
        name = js_NewDependentString(cx, name, 1, JSSTRING_LENGTH(name) - 1, 0);
        if (!name)
            return NULL;
        *funidp = 0;
        return ToAttributeName(cx, STRING_TO_JSVAL(name));
    }

construct:
    v = STRING_TO_JSVAL(name);
    obj = js_ConstructObject(cx, &js_QNameClass.base, NULL, NULL, 1, &v);
    if (!obj)
        return NULL;

out:
    qn = (JSXMLQName *) JS_GetPrivate(cx, obj);
    atom = cx->runtime->atomState.lazy.functionNamespaceURIAtom;
    if (atom &&
        (qn->uri == ATOM_TO_STRING(atom) ||
         !js_CompareStrings(qn->uri, ATOM_TO_STRING(atom)))) {
        if (!JS_ValueToId(cx, STRING_TO_JSVAL(qn->localName), funidp))
            return NULL;
    } else {
        *funidp = 0;
    }
    return qn;

bad:
    JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                         JSMSG_BAD_XML_NAME,
                         js_ValueToPrintableString(cx, STRING_TO_JSVAL(name)));
    return NULL;
}

/* ECMA-357 9.1.1.13 XML [[AddInScopeNamespace]]. */
static JSBool
AddInScopeNamespace(JSContext *cx, JSXML *xml, JSXMLNamespace *ns)
{
    JSXMLNamespace *match, *ns2;
    uint32 i, n, m;

    if (xml->xml_class != JSXML_CLASS_ELEMENT)
        return JS_TRUE;

    /* NULL means *undefined* here -- see ECMA-357 9.1.1.13 step 2. */
    if (!ns->prefix) {
        match = NULL;
        for (i = 0, n = xml->xml_namespaces.length; i < n; i++) {
            ns2 = XMLARRAY_MEMBER(&xml->xml_namespaces, i, JSXMLNamespace);
            if (!js_CompareStrings(ns2->uri, ns->uri)) {
                match = ns2;
                break;
            }
        }
        if (!match && !XMLARRAY_ADD_MEMBER(cx, &xml->xml_namespaces, n, ns))
            return JS_FALSE;
    } else {
        if (IS_EMPTY(ns->prefix) && IS_EMPTY(xml->name->uri))
            return JS_TRUE;
        match = NULL;
#ifdef __GNUC__         /* suppress bogus gcc warnings */
        m = XML_NOT_FOUND;
#endif
        for (i = 0, n = xml->xml_namespaces.length; i < n; i++) {
            ns2 = XMLARRAY_MEMBER(&xml->xml_namespaces, i, JSXMLNamespace);
            if (ns2->prefix && !js_CompareStrings(ns2->prefix, ns->prefix)) {
                match = ns2;
                m = i;
                break;
            }
        }
        if (match && js_CompareStrings(match->uri, ns->uri)) {
            ns2 = XMLARRAY_DELETE(cx, &xml->xml_namespaces, m, JS_TRUE,
                                  JSXMLNamespace);
            JS_ASSERT(ns2 == match);
            match->prefix = NULL;
            if (!AddInScopeNamespace(cx, xml, match)) {
                js_DestroyXMLNamespace(cx, match);
                return JS_FALSE;
            }
        }
        if (!XMLARRAY_APPEND(cx, &xml->xml_namespaces, ns))
            return JS_FALSE;
    }

    /* OPTION: enforce that descendants have superset namespaces. */
    return JS_TRUE;
}

/* ECMA-357 9.2.1.6 XMLList [[Append]]. */
static JSBool
Append(JSContext *cx, JSXML *list, JSXML *xml)
{
    uint32 i, j, k, n;
    JSXML *kid;

    JS_ASSERT(list->xml_class == JSXML_CLASS_LIST);
    i = list->xml_kids.length;
    n = 1;
    if (xml->xml_class == JSXML_CLASS_LIST) {
        list->xml_target = xml->xml_target;
        list->xml_targetprop = xml->xml_targetprop;
        n = JSXML_LENGTH(xml);
        k = i + n;
        if (!XMLArraySetCapacity(cx, &list->xml_kids, k))
            return JS_FALSE;
        for (j = 0; j < n; j++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, j, JSXML);
            if (!js_GetXMLObject(cx, kid)) {
                list->xml_kids.length = i + j;
                return JS_FALSE;
            }
            XMLARRAY_SET_MEMBER(&list->xml_kids, i + j, kid);
        }
        list->xml_kids.length = k;
        return JS_TRUE;
    }

    list->xml_target = xml->parent;
    if (xml->xml_class == JSXML_CLASS_PROCESSING_INSTRUCTION)
        list->xml_targetprop = NULL;
    else
        list->xml_targetprop = xml->name;
    if (!js_GetXMLObject(cx, xml))
        return JS_FALSE;
    if (!XMLARRAY_ADD_MEMBER(cx, &list->xml_kids, i, xml))
        return JS_FALSE;
    return JS_TRUE;
}

/* ECMA-357 9.1.1.7 XML [[DeepCopy]] and 9.2.1.7 XMLList [[DeepCopy]]. */
static JSXML *
DeepCopyInLRS(JSContext *cx, JSXML *xml, uintN flags);

static JSXML *
DeepCopy(JSContext *cx, JSXML *xml, JSObject *obj, uintN flags)
{
    JSXML *copy;
    JSBool ok;

    /* Our caller may not be protecting newborns with a local root scope. */
    if (!JS_EnterLocalRootScope(cx))
        return NULL;
    copy = DeepCopyInLRS(cx, xml, flags);
    if (copy) {
        if (obj) {
            /* Caller provided the object for this copy, hook 'em up. */
            ok = JS_SetPrivate(cx, obj, copy);
            if (ok) {
                copy->object = obj;
                copy->markflag = JSXML_MARK_CLEAR;
            }
        } else {
            ok = js_GetXMLObject(cx, copy) != NULL;
        }
        if (!ok) {
            js_DestroyXML(cx, copy);
            copy = NULL;
        }
    }
    JS_LeaveLocalRootScope(cx);
    return copy;
}

/*
 * (i) We must be in a local root scope (InLRS).
 * (ii) parent must have a rooted object.
 * (iii) from's owning object must be locked if not thread-local.
 */
static JSBool
DeepCopySetInLRS(JSContext *cx, JSXMLArray *from, JSXMLArray *to, JSXML *parent,
                 uintN flags)
{
    uint32 i, j, n;
    JSXML *kid, *kid2;
    JSString *str;

    JS_ASSERT(cx->localRootStack);

    n = from->length;
    if (!XMLArraySetCapacity(cx, to, n))
        return JS_FALSE;

    for (i = j = 0; i < n; i++) {
        kid = XMLARRAY_MEMBER(from, i, JSXML);
        if ((flags & XSF_IGNORE_COMMENTS) &&
            kid->xml_class == JSXML_CLASS_COMMENT) {
            continue;
        }
        if ((flags & XSF_IGNORE_PROCESSING_INSTRUCTIONS) &&
            kid->xml_class == JSXML_CLASS_PROCESSING_INSTRUCTION) {
            continue;
        }
        if ((flags & XSF_IGNORE_WHITESPACE) &&
            (kid->xml_flags & XMLF_WHITESPACE_TEXT)) {
            continue;
        }
        kid2 = DeepCopyInLRS(cx, kid, flags);
        if (!kid2) {
            to->length = j;
            return JS_FALSE;
        }

        if ((flags & XSF_IGNORE_WHITESPACE) &&
            n > 1 && kid2->xml_class == JSXML_CLASS_TEXT) {
            str = ChompXMLWhitespace(cx, kid2->xml_value);
            if (!str) {
                to->length = j;
                return JS_FALSE;
            }
            kid2->xml_value = str;
        }

        XMLARRAY_SET_MEMBER(to, j++, kid2);
        if (parent->xml_class != JSXML_CLASS_LIST)
            kid2->parent = parent;
    }

    to->length = j;
    if (j < n)
        XMLArrayTrim(to);
    return JS_TRUE;
}

static JSXML *
DeepCopyInLRS(JSContext *cx, JSXML *xml, uintN flags)
{
    JSXML *copy;
    JSXMLQName *qn;
    JSBool ok;
    uint32 i, n;
    JSXMLNamespace *ns, *ns2;

    /* Our caller must be protecting newborn objects. */
    JS_ASSERT(cx->localRootStack);

    copy = js_NewXML(cx, xml->xml_class);
    if (!copy)
        return NULL;
    qn = xml->name;
    if (qn) {
        qn = js_NewXMLQName(cx, qn->uri, qn->prefix, qn->localName);
        if (!qn) {
            ok = JS_FALSE;
            goto out;
        }
    }
    copy->name = qn;
    copy->xml_flags = xml->xml_flags;

    if (JSXML_HAS_VALUE(xml)) {
        copy->xml_value = xml->xml_value;
        ok = JS_TRUE;
    } else {
        ok = DeepCopySetInLRS(cx, &xml->xml_kids, &copy->xml_kids, copy, flags);
        if (!ok)
            goto out;

        if (xml->xml_class == JSXML_CLASS_LIST) {
            copy->xml_target = xml->xml_target;
            copy->xml_targetprop = xml->xml_targetprop;
        } else {
            n = xml->xml_namespaces.length;
            ok = XMLArraySetCapacity(cx, &copy->xml_namespaces, n);
            if (!ok)
                goto out;
            for (i = 0; i < n; i++) {
                ns = XMLARRAY_MEMBER(&xml->xml_namespaces, i, JSXMLNamespace);
                ns2 = js_NewXMLNamespace(cx, ns->prefix, ns->uri, ns->declared);
                if (!ns2) {
                    copy->xml_namespaces.length = i;
                    ok = JS_FALSE;
                    goto out;
                }
                XMLARRAY_SET_MEMBER(&copy->xml_namespaces, i, ns2);
            }
            copy->xml_namespaces.length = n;

            ok = DeepCopySetInLRS(cx, &xml->xml_attrs, &copy->xml_attrs, copy,
                                  0);
            if (!ok)
                goto out;
        }
    }

out:
    if (!ok) {
        js_DestroyXML(cx, copy);
        return NULL;
    }
    return copy;
}

static void
ReportBadXMLName(JSContext *cx, jsval id)
{
    JSString *name;

    name = js_DecompileValueGenerator(cx, JSDVG_IGNORE_STACK, id, NULL);
    if (name) {
        JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                             JSMSG_BAD_XML_NAME,
                             JS_GetStringBytes(name));
    }
}

/* ECMA-357 9.1.1.4 XML [[DeleteByIndex]]. */
static JSBool
DeleteByIndex(JSContext *cx, JSXML *xml, jsval id, jsval *vp)
{
    uint32 index;
    JSXML *kid;

    if (!js_IdIsIndex(id, &index)) {
        ReportBadXMLName(cx, id);
        return JS_FALSE;
    }

    if (JSXML_HAS_KIDS(xml) && index < xml->xml_kids.length) {
        kid = XMLARRAY_MEMBER(&xml->xml_kids, index, JSXML);
        kid->parent = NULL;
        XMLArrayDelete(cx, &xml->xml_kids, index, JS_TRUE);
        js_DestroyXML(cx, kid);
    }

    *vp = JSVAL_TRUE;
    return JS_TRUE;
}

typedef JSBool (*JSXMLNameMatcher)(JSXMLQName *nameqn, JSXML *xml);

static JSBool
MatchAttrName(JSXMLQName *nameqn, JSXML *attr)
{
    JSXMLQName *attrqn = attr->name;

    return (IS_STAR(nameqn->localName) ||
            !js_CompareStrings(attrqn->localName, nameqn->localName)) &&
           (!nameqn->uri ||
            !js_CompareStrings(attrqn->uri, nameqn->uri));
}

static JSBool
MatchElemName(JSXMLQName *nameqn, JSXML *elem)
{
    return (IS_STAR(nameqn->localName) ||
            (elem->xml_class == JSXML_CLASS_ELEMENT &&
             !js_CompareStrings(elem->name->localName, nameqn->localName))) &&
           (!nameqn->uri ||
            (elem->xml_class == JSXML_CLASS_ELEMENT &&
             !js_CompareStrings(elem->name->uri, nameqn->uri)));
}

/* ECMA-357 9.1.1.8 XML [[Descendants]] and 9.2.1.8 XMLList [[Descendants]]. */
static JSBool
DescendantsHelper(JSContext *cx, JSXML *xml, JSXMLQName *nameqn, JSXML *list)
{
    uint32 i, n;
    JSXML *attr, *kid;

    if (xml->xml_class == JSXML_CLASS_ELEMENT &&
        OBJ_GET_CLASS(cx, nameqn->object) == &js_AttributeNameClass) {
        for (i = 0, n = xml->xml_attrs.length; i < n; i++) {
            attr = XMLARRAY_MEMBER(&xml->xml_attrs, i, JSXML);
            if (MatchAttrName(nameqn, attr)) {
                if (!Append(cx, list, attr))
                    return JS_FALSE;
            }
        }
    }

    for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
        kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
        if (OBJ_GET_CLASS(cx, nameqn->object) != &js_AttributeNameClass &&
            MatchElemName(nameqn, kid)) {
            if (!Append(cx, list, kid))
                return JS_FALSE;
        }
        if (!DescendantsHelper(cx, kid, nameqn, list))
            return JS_FALSE;
    }
    return JS_TRUE;
}

static JSXML *
Descendants(JSContext *cx, JSXML *xml, jsval id)
{
    jsid funid;
    JSXMLQName *nameqn;
    JSObject *listobj;
    JSXML *list;
    JSBool ok;

    nameqn = ToXMLName(cx, id, &funid);
    if (!nameqn)
        return NULL;

    listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
    if (!listobj)
        return NULL;
    list = (JSXML *) JS_GetPrivate(cx, listobj);
    if (funid)
        return list;

    /*
     * Protect nameqn's object and strings from GC by linking list to it
     * temporarily.  The cx->newborn[GCX_OBJECT] GC root protects listobj,
     * which protects list.  Any other object allocations occuring beneath
     * DescendantsHelper use local roots.
     */
    list->name = nameqn;
    if (!JS_EnterLocalRootScope(cx))
        return NULL;
    ok = DescendantsHelper(cx, xml, nameqn, list);
    JS_LeaveLocalRootScope(cx);
    if (!ok)
        return NULL;
    list->name = NULL;
    return list;
}

/* Recursive (JSXML *) parameterized version of Equals. */
static JSBool
XMLEquals(JSContext *cx, JSXML *xml, JSXML *vxml, JSBool *bp)
{
    JSXMLQName *qn, *vqn;
    uint32 i, j, n;
    JSXML **xvec, **vvec, *attr, *vattr;
    JSObject *xobj, *vobj;

retry:
    if (xml->xml_class != vxml->xml_class) {
        if (xml->xml_class == JSXML_CLASS_LIST && xml->xml_kids.length == 1) {
            xml = XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML);
            goto retry;
        }
        if (vxml->xml_class == JSXML_CLASS_LIST && vxml->xml_kids.length == 1) {
            vxml = XMLARRAY_MEMBER(&vxml->xml_kids, 0, JSXML);
            goto retry;
        }
        *bp = JS_FALSE;
        return JS_TRUE;
    }

    qn = xml->name;
    vqn = vxml->name;
    if (qn) {
        *bp = vqn &&
              !js_CompareStrings(qn->localName, vqn->localName) &&
              !js_CompareStrings(qn->uri, vqn->uri);
    } else {
        *bp = vqn == NULL;
    }
    if (!*bp)
        return JS_TRUE;

    if (JSXML_HAS_VALUE(xml)) {
        *bp = !js_CompareStrings(xml->xml_value, vxml->xml_value);
    } else if ((n = xml->xml_kids.length) != vxml->xml_kids.length) {
        *bp = JS_FALSE;
    } else {
        xvec = (JSXML **) xml->xml_kids.vector;
        vvec = (JSXML **) vxml->xml_kids.vector;
        for (i = 0; i < n; i++) {
            xobj = js_GetXMLObject(cx, xvec[i]);
            vobj = js_GetXMLObject(cx, vvec[i]);
            if (!xobj || !vobj)
                return JS_FALSE;
            if (!js_XMLObjectOps.equality(cx, xobj, OBJECT_TO_JSVAL(vobj), bp))
                return JS_FALSE;
            if (!*bp)
                break;
        }

        if (*bp && xml->xml_class == JSXML_CLASS_ELEMENT) {
            n = xml->xml_attrs.length;
            if (n != vxml->xml_attrs.length)
                *bp = JS_FALSE;
            for (i = 0; i < n; i++) {
                attr = XMLARRAY_MEMBER(&xml->xml_attrs, i, JSXML);
                j = XMLARRAY_FIND_MEMBER(&vxml->xml_attrs, attr, attr_identity);
                if (j == XML_NOT_FOUND) {
                    *bp = JS_FALSE;
                    break;
                }
                vattr = XMLARRAY_MEMBER(&vxml->xml_attrs, j, JSXML);
                *bp = !js_CompareStrings(attr->xml_value, vattr->xml_value);
                if (!*bp)
                    break;
            }
        }
    }

    return JS_TRUE;
}

/* ECMA-357 9.1.1.9 XML [[Equals]] and 9.2.1.9 XMLList [[Equals]]. */
static JSBool
Equals(JSContext *cx, JSXML *xml, jsval v, JSBool *bp)
{
    JSObject *vobj;
    JSXML *vxml;

    if (JSVAL_IS_PRIMITIVE(v)) {
        if (xml->xml_class == JSXML_CLASS_LIST) {
            if (JSVAL_IS_VOID(v)) {
                *bp = JS_TRUE;
            } else if (xml->xml_kids.length == 1) {
                vxml = XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML);
                vobj = js_GetXMLObject(cx, vxml);
                if (!vobj)
                    return JS_FALSE;
                return js_XMLObjectOps.equality(cx, vobj, v, bp);
            } else {
                *bp = JS_FALSE;
            }
        }
    } else {
        vobj = JSVAL_TO_OBJECT(v);
        if (!OBJECT_IS_XML(cx, vobj)) {
            *bp = JS_FALSE;
        } else {
            vxml = (JSXML *) JS_GetPrivate(cx, vobj);
            if (!XMLEquals(cx, xml, vxml, bp))
                return JS_FALSE;
        }
    }
    return JS_TRUE;
}

static JSBool
Replace(JSContext *cx, JSXML *xml, jsval id, jsval v);

/* ECMA-357 9.1.1.11 XML [[Insert]]. */
static JSBool
Insert(JSContext *cx, JSXML *xml, jsval id, jsval v)
{
    uint32 i, j, n;
    JSXML *vxml, *kid;
    JSObject *vobj;

    if (!JSXML_HAS_KIDS(xml))
        return JS_TRUE;

    if (!js_IdIsIndex(id, &i)) {
        ReportBadXMLName(cx, id);
        return JS_FALSE;
    }

    n = 1;
    vxml = NULL;
    if (!JSVAL_IS_PRIMITIVE(v)) {
        vobj = JSVAL_TO_OBJECT(v);
        if (OBJECT_IS_XML(cx, vobj)) {
            vxml = (JSXML *) JS_GetPrivate(cx, vobj);
            if (vxml->xml_class == JSXML_CLASS_LIST)
                n = vxml->xml_kids.length;
        }
    }

    if (n == 0)
        return JS_TRUE;

    if (!XMLArrayInsert(cx, &xml->xml_kids, i, n))
        return JS_FALSE;

    if (vxml && vxml->xml_class == JSXML_CLASS_LIST) {
        for (j = 0; j < n; j++) {
            kid = XMLARRAY_MEMBER(&vxml->xml_kids, j, JSXML);
            if (!js_GetXMLObject(cx, kid))
                return JS_FALSE;
            kid->parent = xml;
            XMLARRAY_SET_MEMBER(&xml->xml_kids, i + j, kid);

            /* OPTION: enforce that descendants have superset namespaces. */
        }
    } else {
        /*
         * Tricky: ECMA-357 9.1.1.11 step 7 specifies:
         *
         *      For j = x.[[Length]]-1 downto i,
         *              rename property ToString(j) of x to ToString(j + n)
         *
         * That loop, coded above, simply copies pointers up in xml->xml_kids.
         * We don't need to change property "names", nor do we need to null
         * pointers in the vxml->xml_class == JSXML_CLASS_LIST case, above.
         *
         * But here, before calling Replace, we must help Replace discern that
         * the "properties" have been "renamed" by nulling the n xml->xml_kids
         * slots that have been evacuated to make way for vxml.
         */
        for (j = 0; j < n; j++)
            xml->xml_kids.vector[i + j] = NULL;
        if (!Replace(cx, xml, id, v))
            return JS_FALSE;
    }
    return JS_TRUE;
}

static JSBool
IndexToIdVal(JSContext *cx, uint32 index, jsval *idvp)
{
    JSString *str;

    if (index <= JSVAL_INT_MAX) {
        *idvp = INT_TO_JSVAL(index);
    } else {
        str = js_NumberToString(cx, (jsdouble) index);
        if (!str)
            return JS_FALSE;
        *idvp = STRING_TO_JSVAL(str);
    }
    return JS_TRUE;
}

/* ECMA-357 9.1.1.12 XML [[Replace]]. */
static JSBool
Replace(JSContext *cx, JSXML *xml, jsval id, jsval v)
{
    uint32 i, n;
    JSXML *vxml, *kid;
    JSObject *vobj;
    jsval junk;
    JSString *str;

    if (!JSXML_HAS_KIDS(xml))
        return JS_TRUE;

    if (!js_IdIsIndex(id, &i)) {
        ReportBadXMLName(cx, id);
        return JS_FALSE;
    }

    /*
     * 9.1.1.12
     * [[Replace]] handles _i >= x.[[Length]]_ by incrementing _x.[[Length]_.
     * It should therefore constrain callers to pass in _i <= x.[[Length]]_.
     */
    n = xml->xml_kids.length;
    JS_ASSERT(i <= n);
    if (i >= n) {
        if (!IndexToIdVal(cx, n, &id))
            return JS_FALSE;
        i = n;
    }

    vxml = NULL;
    if (!JSVAL_IS_PRIMITIVE(v)) {
        vobj = JSVAL_TO_OBJECT(v);
        if (OBJECT_IS_XML(cx, vobj))
            vxml = (JSXML *) JS_GetPrivate(cx, vobj);
    }

    switch (vxml ? vxml->xml_class : JSXML_CLASS_LIMIT) {
      case JSXML_CLASS_ELEMENT:
        /* OPTION: enforce that descendants have superset namespaces. */
      case JSXML_CLASS_COMMENT:
      case JSXML_CLASS_PROCESSING_INSTRUCTION:
      case JSXML_CLASS_TEXT:
        goto do_replace;

      case JSXML_CLASS_LIST:
        if (i < n && !DeleteByIndex(cx, xml, id, &junk))
            return JS_FALSE;
        if (!Insert(cx, xml, id, v))
            return JS_FALSE;
        break;

      default:
        str = js_ValueToString(cx, v);
        if (!str)
            return JS_FALSE;

        vxml = js_NewXML(cx, JSXML_CLASS_TEXT);
        if (!vxml)
            return JS_FALSE;
        vxml->xml_value = str;

      do_replace:
        vxml->parent = xml;
        if (i < n) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid) {
                kid->parent = NULL;
                js_DestroyXML(cx, kid);
            }
        }
        if (!XMLARRAY_ADD_MEMBER(cx, &xml->xml_kids, i, vxml))
            return JS_FALSE;
        break;
    }

    return JS_TRUE;
}

/* Forward declared -- its implementation uses other statics that call it. */
static JSBool
ResolveValue(JSContext *cx, JSXML *list, JSXML **result);

/* ECMA-357 9.1.1.3 XML [[Delete]], 9.2.1.3 XML [[Delete]]. */
static JSBool
DeleteProperty(JSContext *cx, JSObject *obj, jsval id, jsval *vp)
{
    JSXML *xml, *kid, *parent;
    JSBool isIndex;
    JSXMLArray *array;
    uint32 length, index, deleteCount;
    JSXMLQName *nameqn;
    jsid funid;
    JSObject *nameobj, *kidobj;
    JSXMLNameMatcher matcher;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    isIndex = js_IdIsIndex(id, &index);
    if (JSXML_HAS_KIDS(xml)) {
        array = &xml->xml_kids;
        length = array->length;
    } else {
        array = NULL;
        length = 0;
    }

    if (xml->xml_class == JSXML_CLASS_LIST) {
        /* ECMA-357 9.2.1.3. */
        if (isIndex && index < length) {
            kid = XMLARRAY_MEMBER(array, index, JSXML);
            parent = kid->parent;
            if (parent) {
                JS_ASSERT(parent != xml);
                JS_ASSERT(JSXML_HAS_KIDS(parent));

                if (kid->xml_class == JSXML_CLASS_ATTRIBUTE) {
                    nameqn = kid->name;
                    nameobj = js_GetAttributeNameObject(cx, nameqn);
                    if (!nameobj || !js_GetXMLObject(cx, parent))
                        return JS_FALSE;

                    id = OBJECT_TO_JSVAL(nameobj);
                    if (!DeleteProperty(cx, parent->object, id, vp))
                        return JS_FALSE;
                } else {
                    index = XMLARRAY_FIND_MEMBER(&parent->xml_kids, kid, NULL);
                    JS_ASSERT(index != XML_NOT_FOUND);
                    if (!IndexToIdVal(cx, index, &id))
                        return JS_FALSE;
                    if (!DeleteByIndex(cx, parent, id, vp))
                        return JS_FALSE;
                }
            }

            XMLArrayDelete(cx, array, index, JS_TRUE);
        } else {
            for (index = 0; index < length; index++) {
                kid = XMLARRAY_MEMBER(array, index, JSXML);
                if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                    kidobj = js_GetXMLObject(cx, kid);
                    if (!kidobj || !DeleteProperty(cx, kidobj, id, vp))
                        return JS_FALSE;
                }
            }
        }
    } else {
        /* ECMA-357 9.1.1.3. */
        if (isIndex) {
            /* See NOTE in spec: this variation is reserved for future use. */
            ReportBadXMLName(cx, id);
            return JS_FALSE;
        }

        nameqn = ToXMLName(cx, id, &funid);
        if (!nameqn)
            return JS_FALSE;
        if (funid)
            goto out;
        nameobj = nameqn->object;

        if (OBJ_GET_CLASS(cx, nameobj) == &js_AttributeNameClass) {
            if (xml->xml_class != JSXML_CLASS_ELEMENT)
                goto out;
            array = &xml->xml_attrs;
            matcher = MatchAttrName;
        } else {
            matcher = MatchElemName;
        }
        length = array->length;
        if (length != 0) {
            deleteCount = 0;
            for (index = 0; index < length; index++) {
                kid = XMLARRAY_MEMBER(array, index, JSXML);
                if (matcher(nameqn, kid)) {
                    kid->parent = NULL;
                    XMLArrayDelete(cx, array, index, JS_FALSE);
                    js_DestroyXML(cx, kid);
                    ++deleteCount;
                } else if (deleteCount != 0) {
                    XMLARRAY_SET_MEMBER(array,
                                        index - deleteCount,
                                        array->vector[index]);
                }
            }
            array->length -= deleteCount;
        }
    }

out:
    *vp = JSVAL_TRUE;
    return JS_TRUE;
}

/*
 * Class compatibility mask flag bits stored in xml_methods[i].extra.  If XML
 * and XMLList are unified (an incompatible change to ECMA-357), then we don't
 * need any of this.
 */
#define XML_MASK                0x1
#define XMLLIST_MASK            0x2
#define GENERIC_MASK            (XML_MASK | XMLLIST_MASK)
#define CLASS_TO_MASK(c)        (1 + ((c) == JSXML_CLASS_LIST))

static JSBool
GetFunction(JSContext *cx, JSObject *obj, JSXML *xml, jsid id, jsval *vp)
{
    jsval fval;
    JSFunction *fun;

    do {
        /* XXXbe really want a separate scope for function:*. */
        if (!js_GetProperty(cx, obj, id, &fval))
            return JS_FALSE;
        if (JSVAL_IS_FUNCTION(cx, fval)) {
            if (xml && OBJECT_IS_XML(cx, obj)) {
                fun = (JSFunction *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(fval));
                if ((fun->spare & CLASS_TO_MASK(xml->xml_class)) == 0)
                    fval = JSVAL_VOID;
            }
            break;
        }
    } while ((obj = OBJ_GET_PROTO(cx, obj)) != NULL);
    *vp = fval;
    return JS_TRUE;
}

static JSBool
SyncInScopeNamespaces(JSContext *cx, JSXML *xml)
{
    JSXMLArray *nsarray;
    uint32 i, n;
    JSXMLNamespace *ns;

    nsarray = &xml->xml_namespaces;
    while ((xml = xml->parent) != NULL) {
        for (i = 0, n = xml->xml_namespaces.length; i < n; i++) {
            ns = XMLARRAY_MEMBER(&xml->xml_namespaces, i, JSXMLNamespace);
            if (!XMLARRAY_HAS_MEMBER(nsarray, ns, namespace_identity)) {
                if (!js_GetXMLNamespaceObject(cx, ns))
                    return JS_FALSE;
                if (!XMLARRAY_APPEND(cx, nsarray, ns))
                    return JS_FALSE;
            }
        }
    }
    return JS_TRUE;
}

/* ECMA-357 9.1.1.1 XML [[Get]] and 9.2.1.1 XMLList [[Get]]. */
static JSBool
GetProperty(JSContext *cx, JSObject *obj, jsval id, jsval *vp)
{
    JSXML *xml, *list, *kid;
    uint32 index, i, n;
    JSObject *kidobj, *listobj, *nameobj;
    JSXMLQName *nameqn;
    jsid funid;
    JSBool ok;
    jsval kidval;
    JSXMLArray *array;
    JSXMLNameMatcher matcher;

    xml = (JSXML *) JS_GetInstancePrivate(cx, obj, &js_XMLClass, NULL);
    if (!xml)
        return JS_TRUE;

retry:
    if (xml->xml_class == JSXML_CLASS_LIST) {
        /* ECMA-357 9.2.1.1 starts here. */
        if (js_IdIsIndex(id, &index)) {
            /*
             * Erratum: 9.2 is not completely clear that indexed properties
             * correspond to kids, but that's what it seems to say, and it's
             * what any sane user would want.
             */
            if (index < xml->xml_kids.length) {
                kid = XMLARRAY_MEMBER(&xml->xml_kids, index, JSXML);
                kidobj = js_GetXMLObject(cx, kid);
                if (!kidobj)
                    return JS_FALSE;

                *vp = OBJECT_TO_JSVAL(kidobj);
            } else {
                *vp = JSVAL_VOID;
            }
            return JS_TRUE;
        }

        nameqn = ToXMLName(cx, id, &funid);
        if (!nameqn)
            return JS_FALSE;
        if (funid)
            return GetFunction(cx, obj, xml, funid, vp);

        /*
         * Recursion through GetProperty may allocate more list objects, so
         * we make use of local root scopes here.  Each new allocation will
         * push the newborn onto the local root stack.
         */
        ok = JS_EnterLocalRootScope(cx);
        if (!ok)
            return JS_FALSE;

        /*
         * NB: nameqn is already protected from GC by cx->newborn[GCX_OBJECT]
         * until listobj is created.  After that, a local root keeps listobj
         * alive, and listobj's private keeps nameqn alive via targetprop.
         */
        listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
        if (!listobj) {
            ok = JS_FALSE;
        } else {
            list = (JSXML *) JS_GetPrivate(cx, listobj);
            list->xml_target = xml;
            list->xml_targetprop = nameqn;

            for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
                kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
                if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                    kidobj = js_GetXMLObject(cx, kid);
                    if (!kidobj) {
                        ok = JS_FALSE;
                        break;
                    }
                    ok = GetProperty(cx, kidobj, id, &kidval);
                    if (!ok)
                        break;
                    kidobj = JSVAL_TO_OBJECT(kidval);
                    kid = (JSXML *) JS_GetPrivate(cx, kidobj);
                    if (JSXML_LENGTH(kid) > 0) {
                        ok = Append(cx, list, kid);
                        if (!ok)
                            break;
                    }
                }
            }
        }
    } else {
        /* ECMA-357 9.1.1.1 starts here. */
        if (js_IdIsIndex(id, &index)) {
            obj = ToXMLList(cx, OBJECT_TO_JSVAL(obj));
            if (!obj)
                return JS_FALSE;
            xml = (JSXML *) JS_GetPrivate(cx, obj);
            goto retry;
        }

        nameqn = ToXMLName(cx, id, &funid);
        if (!nameqn)
            return JS_FALSE;
        if (funid)
            return GetFunction(cx, obj, xml, funid, vp);
        nameobj = nameqn->object;

        /*
         * Recursion through GetProperty may allocate more list objects, so
         * we make use of local root scopes here.  Each new allocation will
         * push the newborn onto the local root stack.
         */
        ok = JS_EnterLocalRootScope(cx);
        if (!ok)
            return JS_FALSE;

        listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
        if (!listobj) {
            ok = JS_FALSE;
        } else {
            list = (JSXML *) JS_GetPrivate(cx, listobj);
            list->xml_target = xml;
            list->xml_targetprop = nameqn;

            if (JSXML_HAS_KIDS(xml)) {
                if (OBJ_GET_CLASS(cx, nameobj) == &js_AttributeNameClass) {
                    array = &xml->xml_attrs;
                    matcher = MatchAttrName;
                } else {
                    array = &xml->xml_kids;
                    matcher = MatchElemName;
                }
                for (i = 0, n = array->length; i < n; i++) {
                    kid = XMLARRAY_MEMBER(array, i, JSXML);
                    if (matcher(nameqn, kid)) {
                        if (array == &xml->xml_kids &&
                            kid->xml_class == JSXML_CLASS_ELEMENT) {
                            ok = SyncInScopeNamespaces(cx, kid);
                            if (!ok)
                                break;
                        }
                        ok = Append(cx, list, kid);
                        if (!ok)
                            break;
                    }
                }
            }
        }
    }

    /* Common tail code for list and non-list cases. */
    JS_LeaveLocalRootScope(cx);
    if (!ok)
        return JS_FALSE;

    *vp = OBJECT_TO_JSVAL(listobj);
    return JS_TRUE;
}

static JSXML *
CopyOnWrite(JSContext *cx, JSXML *xml, JSObject *obj)
{
    JS_ASSERT(xml->object != obj);

    xml = DeepCopy(cx, xml, obj, 0);
    if (!xml)
        return NULL;

    JS_ASSERT(xml->object == obj);
    JS_ASSERT(xml->markflag == JSXML_MARK_CLEAR);
    return xml;
}

#define CHECK_COPY_ON_WRITE(cx,xml,obj)                                       \
    (xml->object == obj ? xml : CopyOnWrite(cx, xml, obj))

static JSString *
KidToString(JSContext *cx, JSXML *xml, uint32 index)
{
    JSXML *kid;
    JSObject *kidobj;

    kid = XMLARRAY_MEMBER(&xml->xml_kids, index, JSXML);
    kidobj = js_GetXMLObject(cx, kid);
    if (!kidobj)
        return NULL;
    return js_ValueToString(cx, OBJECT_TO_JSVAL(kidobj));
}

/* ECMA-357 9.1.1.2 XML [[Put]] and 9.2.1.2 XMLList [[Put]]. */
static JSBool
PutProperty(JSContext *cx, JSObject *obj, jsval id, jsval *vp)
{
    JSBool ok, primitiveAssign;
    JSXML *xml, *vxml, *rxml, *kid, *attr, *parent, *copy, *kid2, *match;
    JSObject *vobj, *nameobj, *attrobj, *parentobj, *kidobj, *copyobj;
    JSXMLQName *targetprop, *nameqn, *attrqn;
    uint32 index, i, j, k, n, q;
    jsval attrval, nsval, junk;
    jsid funid;
    JSString *left, *right, *space;
    JSXMLNamespace *ns;

    xml = (JSXML *) JS_GetInstancePrivate(cx, obj, &js_XMLClass, NULL);
    if (!xml)
        return JS_TRUE;

    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;

    /* Precompute vxml for 9.2.1.2 2(c)(vii)(2-3) and 2(d) and 9.1.1.2 1. */
    vxml = NULL;
    if (!JSVAL_IS_PRIMITIVE(*vp)) {
        vobj = JSVAL_TO_OBJECT(*vp);
        if (OBJECT_IS_XML(cx, vobj))
            vxml = (JSXML *) JS_GetPrivate(cx, vobj);
    }

    /* Control flow after here must exit via label out. */
    ok = JS_EnterLocalRootScope(cx);
    if (!ok)
        return JS_FALSE;

    if (xml->xml_class == JSXML_CLASS_LIST) {
        /* ECMA-357 9.2.1.2. */
        if (js_IdIsIndex(id, &index)) {
            /* Step 1 sets i to the property index. */
            i = index;

            /* 2(a-b). */
            if (xml->xml_target) {
                ok = ResolveValue(cx, xml->xml_target, &rxml);
                if (!ok)
                    goto out;
                if (!rxml)
                    goto out;
                JS_ASSERT(rxml->object);
            } else {
                rxml = NULL;
            }

            /* 2(c). */
            if (index >= xml->xml_kids.length) {
                /* 2(c)(i). */
                if (rxml) {
                    if (rxml->xml_class == JSXML_CLASS_LIST) {
                        if (rxml->xml_kids.length != 1)
                            goto out;
                        rxml = XMLARRAY_MEMBER(&rxml->xml_kids, 0, JSXML);
                        ok = js_GetXMLObject(cx, rxml) != NULL;
                        if (!ok)
                            goto out;
                    }

                    /*
                     * Erratum: ECMA-357 9.2.1.2 step 2(c)(ii) sets
                     * _y.[[Parent]] = r_ where _r_ is the result of
                     * [[ResolveValue]] called on _x.[[TargetObject]] in
                     * 2(a)(i).  This can result in text parenting text:
                     *
                     *    var MYXML = new XML();
                     *    MYXML.appendChild(new XML("<TEAM>Giants</TEAM>"));
                     *
                     * (testcase from Werner Sharp <wsharp@macromedia.com>).
                     *
                     * To match insertChildAfter, insertChildBefore,
                     * prependChild, and setChildren, we should silently
                     * do nothing in this case.
                     */
                    if (!JSXML_HAS_KIDS(rxml))
                        goto out;
                }

                /* 2(c)(ii) is distributed below as several js_NewXML calls. */
                targetprop = xml->xml_targetprop;
                if (!targetprop || IS_STAR(targetprop->localName)) {
                    /* 2(c)(iv)(1-2), out of order w.r.t. 2(c)(iii). */
                    kid = js_NewXML(cx, JSXML_CLASS_TEXT);
                    if (!kid)
                        goto bad;
                } else {
                    nameobj = js_GetXMLQNameObject(cx, targetprop);
                    if (!nameobj)
                        goto bad;
                    if (OBJ_GET_CLASS(cx, nameobj) == &js_AttributeNameClass) {
                        /*
                         * 2(c)(iii)(1-3).
                         * Note that rxml can't be null here, because target
                         * and targetprop are non-null.
                         */
                        ok = GetProperty(cx, rxml->object, id, &attrval);
                        if (!ok)
                            goto out;
                        attrobj = JSVAL_TO_OBJECT(attrval);
                        attr = (JSXML *) JS_GetPrivate(cx, attrobj);
                        if (JSXML_LENGTH(attr) != 0)
                            goto out;

                        kid = js_NewXML(cx, JSXML_CLASS_ATTRIBUTE);
                    } else {
                        /* 2(c)(v). */
                        kid = js_NewXML(cx, JSXML_CLASS_ELEMENT);
                    }
                    if (!kid)
                        goto bad;

                    /* An important bit of 2(c)(ii). */
                    kid->name = targetprop;
                }

                /* Final important bit of 2(c)(ii). */
                kid->parent = rxml;

                /* 2(c)(vi-vii). */
                i = xml->xml_kids.length;
                if (kid->xml_class != JSXML_CLASS_ATTRIBUTE) {
                    /*
                     * 2(c)(vii)(1) tests whether _y.[[Parent]]_ is not null.
                     * y.[[Parent]] is here called kid->parent, which we know
                     * from 2(c)(ii) is _r_, here called rxml.  So let's just
                     * test that!  Erratum, the spec should be simpler here.
                     */
                    if (rxml) {
                        JS_ASSERT(JSXML_HAS_KIDS(rxml));
                        JS_ASSERT(rxml->xml_kids.length != 0);
                        j = n = rxml->xml_kids.length - 1;
                        if (i != 0) {
                            for (j = 0; j < n; j++) {
                                if (rxml->xml_kids.vector[j] ==
                                    xml->xml_kids.vector[i-1]) {
                                    break;
                                }
                            }
                        }

                        kidobj = js_GetXMLObject(cx, kid);
                        if (!kidobj)
                            goto bad;
                        ok = Insert(cx, rxml, INT_TO_JSVAL(j + 1),
                                    OBJECT_TO_JSVAL(kidobj));
                        if (!ok) {
                            js_DestroyXML(cx, kid);
                            goto out;
                        }
                    }

                    /*
                     * 2(c)(vii)(2-3).
                     * Erratum: [[PropertyName]] in 2(c)(vii)(3) must be a
                     * typo for [[TargetProperty]].
                     */
                    if (vxml) {
                        kid->name = (vxml->xml_class == JSXML_CLASS_LIST)
                                    ? vxml->xml_targetprop
                                    : vxml->name;
                        if (kid->name) {
                            ok = js_GetXMLQNameObject(cx, kid->name) != NULL;
                            if (!ok)
                                goto out;
                        }
                    }
                }

                /* 2(c)(viii). */
                ok = Append(cx, xml, kid);
                if (!ok) {
                    js_DestroyXML(cx, kid);
                    goto out;
                }
            }

            /* 2(d). */
            if (!vxml ||
                vxml->xml_class == JSXML_CLASS_TEXT ||
                vxml->xml_class == JSXML_CLASS_ATTRIBUTE) {
                ok = JS_ConvertValue(cx, *vp, JSTYPE_STRING, vp);
                if (!ok)
                    goto out;
            }

            /* 2(e). */
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            parent = kid->parent;
            if (kid->xml_class == JSXML_CLASS_ATTRIBUTE) {
                nameobj = js_GetAttributeNameObject(cx, kid->name);
                if (!nameobj)
                    goto bad;
                id = OBJECT_TO_JSVAL(nameobj);

                /* 2(e)(i). */
                parentobj = parent->object;
                ok = PutProperty(cx, parentobj, id, vp);
                if (!ok)
                    goto out;

                /* 2(e)(ii). */
                ok = GetProperty(cx, parentobj, id, vp);
                if (!ok)
                    goto out;
                attr = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(*vp));

                /* 2(e)(iii). */
                xml->xml_kids.vector[i] = attr->xml_kids.vector[0];
            }

            /* 2(f). */
            else if (vxml && vxml->xml_class == JSXML_CLASS_LIST) {
                /* 2(f)(i) Create a shallow copy _c_ of _V_. */
                copyobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
                if (!copyobj)
                    goto bad;
                copy = (JSXML *) JS_GetPrivate(cx, copyobj);
                n = vxml->xml_kids.length;
                ok = XMLArraySetCapacity(cx, &copy->xml_kids, n);
                if (!ok)
                    goto out;
                for (k = 0; k < n; k++) {
                    kid2 = XMLARRAY_MEMBER(&vxml->xml_kids, k, JSXML);
                    ok = js_GetXMLObject(cx, kid2) != NULL;
                    if (!ok) {
                        copy->xml_kids.length = k;
                        goto out;
                    }
                    XMLARRAY_SET_MEMBER(&copy->xml_kids, k, kid2);
                }
                copy->xml_kids.length = n;

                JS_ASSERT(parent != xml);
                if (parent) {
                    q = XMLARRAY_FIND_MEMBER(&parent->xml_kids, kid, NULL);
                    JS_ASSERT(q != XML_NOT_FOUND);

                    ok = IndexToIdVal(cx, q, &id);
                    if (!ok)
                        goto out;
                    ok = Replace(cx, parent, id, OBJECT_TO_JSVAL(copyobj));
                    if (!ok)
                        goto out;

#ifdef DEBUG
                    /* Erratum: this loop in the spec is useless. */
                    for (j = 0, n = copy->xml_kids.length; j < n; j++) {
                        kid2 = XMLARRAY_MEMBER(&parent->xml_kids, q + j, JSXML);
                        JS_ASSERT(XMLARRAY_MEMBER(&copy->xml_kids, j, JSXML)
                                  == kid2);
                    }
#endif
                }

                /*
                 * 2(f)(iv-vi).
                 * Erratum: notice the unhandled zero-length V basis case and
                 * the off-by-one errors for the n != 0 cases in the spec.
                 */
                if (n == 0) {
                    XMLArrayDelete(cx, &xml->xml_kids, i, JS_TRUE);
                } else {
                    ok = XMLArrayInsert(cx, &xml->xml_kids, i + 1, n - 1);
                    if (!ok)
                        goto out;

                    for (j = 0; j < n; j++)
                        xml->xml_kids.vector[i + j] = copy->xml_kids.vector[j];
                }
            }

            /* 2(g). */
            else if (vxml || JSXML_HAS_VALUE(kid)) {
                if (parent) {
                    q = XMLARRAY_FIND_MEMBER(&parent->xml_kids, kid, NULL);
                    JS_ASSERT(q != XML_NOT_FOUND);

                    ok = IndexToIdVal(cx, q, &id);
                    if (!ok)
                        goto out;
                    ok = Replace(cx, parent, id, *vp);
                    if (!ok)
                        goto out;

                    vxml = XMLARRAY_MEMBER(&parent->xml_kids, q, JSXML);
                    *vp = OBJECT_TO_JSVAL(vxml->object);
                }

                /*
                 * 2(g)(iii).
                 * Erratum: _V_ may not be of type XML, but all index-named
                 * properties _x[i]_ in an XMLList _x_ must be of type XML,
                 * according to 9.2.1.1 Overview and other places in the spec.
                 *
                 * Thanks to 2(d), we know _V_ (*vp here) is either a string
                 * or an XML/XMLList object.  If *vp is a string, call ToXML
                 * on it to satisfy the constraint.
                 */
                if (!vxml) {
                    JS_ASSERT(JSVAL_IS_STRING(*vp));
                    vobj = ToXML(cx, *vp);
                    if (!vobj)
                        goto bad;
                    *vp = OBJECT_TO_JSVAL(vobj);
                    vxml = (JSXML *) JS_GetPrivate(cx, vobj);
                }
                XMLARRAY_SET_MEMBER(&xml->xml_kids, i, vxml);
            }

            /* 2(h). */
            else {
                kidobj = js_GetXMLObject(cx, kid);
                if (!kidobj)
                    goto bad;
                id = ATOM_KEY(cx->runtime->atomState.starAtom);
                ok = PutProperty(cx, kidobj, id, vp);
                if (!ok)
                    goto out;
            }
        } else {
            /*
             * 3.
             * Erratum: if x.[[Length]] > 1 or [[ResolveValue]] returns null
             * or an r with r.[[Length]] != 1, throw TypeError.
             */
            n = JSXML_LENGTH(xml);
            if (n > 1)
                goto type_error;
            if (n == 0) {
                ok = ResolveValue(cx, xml, &rxml);
                if (!ok)
                    goto out;
                if (!rxml || JSXML_LENGTH(rxml) != 1)
                    goto type_error;
                ok = Append(cx, xml, rxml);
                if (!ok)
                    goto out;
            }
            JS_ASSERT(JSXML_LENGTH(xml) == 1);
            kid = XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML);
            kidobj = js_GetXMLObject(cx, kid);
            if (!kidobj)
                goto bad;
            ok = PutProperty(cx, kidobj, id, vp);
            if (!ok)
                goto out;
        }
    } else {
        /*
         * ECMA-357 9.1.1.2.
         * Erratum: move steps 3 and 4 to before 1 and 2, to avoid wasted
         * effort in ToString or [[DeepCopy]].
         */
        if (js_IdIsIndex(id, &index)) {
            /* See NOTE in spec: this variation is reserved for future use. */
            ReportBadXMLName(cx, id);
            goto bad;
        }

        if (JSXML_HAS_VALUE(xml))
            goto out;

        if (!vxml ||
            vxml->xml_class == JSXML_CLASS_TEXT ||
            vxml->xml_class == JSXML_CLASS_ATTRIBUTE) {
            ok = JS_ConvertValue(cx, *vp, JSTYPE_STRING, vp);
            if (!ok)
                goto out;
        } else {
            rxml = DeepCopyInLRS(cx, vxml, 0);
            if (!rxml || !js_GetXMLObject(cx, rxml))
                goto bad;
            vxml = rxml;
            *vp = OBJECT_TO_JSVAL(vxml->object);
        }

        nameqn = ToXMLName(cx, id, &funid);
        if (!nameqn)
            goto bad;
        if (funid) {
            ok = js_SetProperty(cx, obj, funid, vp);
            goto out;
        }
        nameobj = nameqn->object;

        /*
         * 6.
         * Erratum: why is this done here, so early? use is way later....
         */
        ok = js_GetDefaultXMLNamespace(cx, &nsval);
        if (!ok)
            goto out;

        if (OBJ_GET_CLASS(cx, nameobj) == &js_AttributeNameClass) {
            /* 7(a). */
            if (!js_IsXMLName(cx, OBJECT_TO_JSVAL(nameobj)))
                goto out;

            /* 7(b-c). */
            if (vxml && vxml->xml_class == JSXML_CLASS_LIST) {
                n = vxml->xml_kids.length;
                if (n == 0) {
                    *vp = STRING_TO_JSVAL(cx->runtime->emptyString);
                } else {
                    left = KidToString(cx, vxml, 0);
                    if (!left)
                        goto bad;

                    space = ATOM_TO_STRING(cx->runtime->atomState.spaceAtom);
                    for (i = 1; i < n; i++) {
                        left = js_ConcatStrings(cx, left, space);
                        if (!left)
                            goto bad;
                        right = KidToString(cx, vxml, i);
                        if (!right)
                            goto bad;
                        left = js_ConcatStrings(cx, left, right);
                        if (!left)
                            goto bad;
                    }

                    *vp = STRING_TO_JSVAL(left);
                }
            } else {
                ok = JS_ConvertValue(cx, *vp, JSTYPE_STRING, vp);
                if (!ok)
                    goto out;
            }

            /* 7(d-e). */
            match = NULL;
            for (i = 0, n = xml->xml_attrs.length; i < n; i++) {
                attr = XMLARRAY_MEMBER(&xml->xml_attrs, i, JSXML);
                attrqn = attr->name;
                if (!js_CompareStrings(attrqn->localName, nameqn->localName) &&
                    (!nameqn->uri ||
                     !js_CompareStrings(attrqn->uri, nameqn->uri))) {
                    if (!match) {
                        match = attr;
                    } else {
                        nameobj = js_GetAttributeNameObject(cx, attrqn);
                        if (!nameobj)
                            goto bad;

                        id = OBJECT_TO_JSVAL(nameobj);
                        ok = DeleteProperty(cx, obj, id, &junk);
                        if (!ok)
                            goto out;
                        --i;
                    }
                }
            }

            /* 7(f). */
            attr = match;
            if (!attr) {
                /* 7(f)(i-ii). */
                if (!nameqn->uri) {
                    left = right = cx->runtime->emptyString;
                } else {
                    left = nameqn->uri;
                    right = nameqn->prefix;
                }
                nameqn = js_NewXMLQName(cx, left, right, nameqn->localName);
                if (!nameqn)
                    goto bad;

                /* 7(f)(iii). */
                attr = js_NewXML(cx, JSXML_CLASS_ATTRIBUTE);
                if (!attr) {
                    js_DestroyXMLQName(cx, nameqn);
                    goto bad;
                }
                attr->parent = xml;
                attr->name = nameqn;

                /* 7(f)(iv). */
                ok = XMLARRAY_ADD_MEMBER(cx, &xml->xml_attrs, n, attr);
                if (!ok) {
                    js_DestroyXML(cx, attr);
                    goto out;
                }

                /* 7(f)(v-vi). */
                ns = GetNamespace(cx, nameqn, NULL);
                if (!ns)
                    goto bad;
                ok = AddInScopeNamespace(cx, xml, ns);
                if (!ok)
                    goto out;
            }

            /* 7(g). */
            attr->xml_value = JSVAL_TO_STRING(*vp);
            goto out;
        }

        /* 8-9. */
        if (!js_IsXMLName(cx, OBJECT_TO_JSVAL(nameobj)) &&
            !IS_STAR(nameqn->localName)) {
            goto out;
        }

        /* 10-11. */
        id = JSVAL_VOID;
        primitiveAssign = !vxml && !IS_STAR(nameqn->localName);

        /* 12. */
        k = n = xml->xml_kids.length;
        while (k != 0) {
            --k;
            kid = XMLARRAY_MEMBER(&xml->xml_kids, k, JSXML);
            if (MatchElemName(nameqn, kid)) {
                if (!JSVAL_IS_VOID(id)) {
                    ok = DeleteByIndex(cx, xml, id, &junk);
                    if (!ok)
                        goto out;
                }
                ok = IndexToIdVal(cx, k, &id);
                if (!ok)
                    goto out;
            }
        }

        /* 13. */
        if (JSVAL_IS_VOID(id)) {
            /* 13(a). */
            ok = IndexToIdVal(cx, n, &id);
            if (!ok)
                goto out;

            /* 13(b). */
            if (primitiveAssign) {
                if (!nameqn->uri) {
                    ns = (JSXMLNamespace *)
                         JS_GetPrivate(cx, JSVAL_TO_OBJECT(nsval));
                    left = ns->uri;
                    right = ns->prefix;
                } else {
                    left = nameqn->uri;
                    right = nameqn->prefix;
                }
                nameqn = js_NewXMLQName(cx, left, right, nameqn->localName);
                if (!nameqn)
                    goto bad;

                /* 13(b)(iii). */
                vobj = js_NewXMLObject(cx, JSXML_CLASS_ELEMENT);
                if (!vobj) {
                    js_DestroyXMLQName(cx, nameqn);
                    goto bad;
                }
                vxml = (JSXML *) JS_GetPrivate(cx, vobj);
                vxml->parent = xml;
                vxml->name = nameqn;

                /* 13(b)(iv-vi). */
                ns = GetNamespace(cx, nameqn, NULL);
                if (!ns)
                    goto bad;
                ok = Replace(cx, xml, id, OBJECT_TO_JSVAL(vobj));
                if (!ok)
                    goto out;
                ok = AddInScopeNamespace(cx, vxml, ns);
                if (!ok)
                    goto out;
            }
        }

        /* 14. */
        if (primitiveAssign) {
            js_IdIsIndex(id, &index);
            kid = XMLARRAY_MEMBER(&xml->xml_kids, index, JSXML);
            if (JSXML_HAS_KIDS(kid)) {
                XMLARRAY_FINISH(cx, &kid->xml_kids, js_DestroyXML);
                ok = XMLARRAY_INIT(cx, &kid->xml_kids, 1);
                if (!ok)
                    goto out;
            }

            /* 14(b-c). */
            /* XXXbe Erratum? redundant w.r.t. 7(b-c) else clause above */
            ok = JS_ConvertValue(cx, *vp, JSTYPE_STRING, vp);
            if (!ok)
                goto out;
            if (!IS_EMPTY(JSVAL_TO_STRING(*vp)))
                ok = Replace(cx, kid, JSVAL_ZERO, *vp);
        } else {
            /* 15(a). */
            ok = Replace(cx, xml, id, *vp);
        }
    }

out:
    JS_LeaveLocalRootScope(cx);
    return ok;

type_error:
    JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                         JSMSG_BAD_XMLLIST_PUT,
                         js_ValueToPrintableString(cx, id));
bad:
    ok = JS_FALSE;
    goto out;
}

/* ECMA-357 9.1.1.10 XML [[ResolveValue]], 9.2.1.10 XMLList [[ResolveValue]]. */
static JSBool
ResolveValue(JSContext *cx, JSXML *list, JSXML **result)
{
    JSXML *target, *base;
    JSXMLQName *targetprop;
    jsval id, tv;

    /* Our caller must be protecting newborn objects. */
    JS_ASSERT(cx->localRootStack);

    if (list->xml_class != JSXML_CLASS_LIST || list->xml_kids.length != 0) {
        if (!js_GetXMLObject(cx, list))
            return JS_FALSE;
        *result = list;
        return JS_TRUE;
    }

    target = list->xml_target;
    targetprop = list->xml_targetprop;
    if (!target ||
        !targetprop ||
        OBJ_GET_CLASS(cx, targetprop->object) == &js_AttributeNameClass ||
        IS_STAR(targetprop->localName)) {
        *result = NULL;
        return JS_TRUE;
    }

    if (!ResolveValue(cx, target, &base))
        return JS_FALSE;
    if (!base) {
        *result = NULL;
        return JS_TRUE;
    }
    if (!js_GetXMLObject(cx, base))
        return JS_FALSE;

    id = OBJECT_TO_JSVAL(targetprop->object);
    if (!GetProperty(cx, base->object, id, &tv))
        return JS_FALSE;
    target = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(tv));

    if (JSXML_LENGTH(target) == 0) {
        if (base->xml_class == JSXML_CLASS_LIST && JSXML_LENGTH(base) > 1) {
            *result = NULL;
            return JS_TRUE;
        }
        tv = STRING_TO_JSVAL(cx->runtime->emptyString);
        if (!PutProperty(cx, base->object, id, &tv))
            return JS_FALSE;
        if (!GetProperty(cx, base->object, id, &tv))
            return JS_FALSE;
        target = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(tv));
    }

    *result = target;
    return JS_TRUE;
}

/* ECMA-357 9.1.1.6 XML [[HasProperty]] and 9.2.1.5 XMLList [[HasProperty]]. */
static JSBool
HasProperty(JSContext *cx, JSObject *obj, jsval id, JSBool *foundp)
{
    JSXML *xml, *kid;
    uint32 i, n;
    JSObject *kidobj;
    JSXMLQName *qn;
    jsid funid;
    JSXMLArray *array;
    JSXMLNameMatcher matcher;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (xml->xml_class == JSXML_CLASS_LIST) {
        n = JSXML_LENGTH(xml);
        if (js_IdIsIndex(id, &i)) {
            *foundp = i < n;
            return JS_TRUE;
        }

        for (i = 0; i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                kidobj = js_GetXMLObject(cx, kid);
                if (!kidobj || !HasProperty(cx, kidobj, id, foundp))
                    return JS_FALSE;
                if (*foundp)
                    return JS_TRUE;
            }
        }
    } else if (xml->xml_class == JSXML_CLASS_ELEMENT) {
        if (js_IdIsIndex(id, &i)) {
            *foundp = (i == 0);
            return JS_TRUE;
        }

        qn = ToXMLName(cx, id, &funid);
        if (!qn)
            return JS_FALSE;
        if (funid) {
            JSObject *pobj;
            JSProperty *prop;

            if (!js_LookupProperty(cx, obj, funid, &pobj, &prop))
                return JS_FALSE;
            *foundp = prop != NULL;
            OBJ_DROP_PROPERTY(cx, pobj, prop);
            return JS_TRUE;
        }

        if (OBJ_GET_CLASS(cx, qn->object) == &js_AttributeNameClass) {
            array = &xml->xml_attrs;
            matcher = MatchAttrName;
        } else {
            array = &xml->xml_kids;
            matcher = MatchElemName;
        }
        for (i = 0, n = array->length; i < n; i++) {
            kid = XMLARRAY_MEMBER(array, i, JSXML);
            *foundp = matcher(qn, kid);
            if (*foundp)
                return JS_TRUE;
        }
    }

    *foundp = JS_FALSE;
    return JS_TRUE;
}

static void
xml_finalize(JSContext *cx, JSObject *obj)
{
    JSXML *xml, *kid, *attr;
    JSRuntime *rt;
    uint32 i, n;
    JSXMLNamespace *ns;
    JSXMLQName *qn;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (!xml)
        return;
    if (xml->object == obj)
        xml->object = NULL;
    if (xml->markflag == JSXML_MARK_CLEAR) {
        /* Not marked by obj or any other owner, so flag xml as doomed. */
        xml->markflag = JSXML_MARK_DOOMED;
        rt = cx->runtime;
        xml->object = (JSObject *) rt->gcDoomedXML;
        rt->gcDoomedXML = xml;

        if (JSXML_HAS_KIDS(xml)) {
            /*
             * Destroy all single-owner descendants not underneath a GC'd
             * descendant.
             */
            for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
                kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
                if (kid->markflag == JSXML_MARK_SINGLE_OWNER) {
                    js_DestroyXML(cx, kid);
#ifdef DEBUG
                    XMLARRAY_SET_MEMBER(&xml->xml_kids, i, NULL);
#endif
                }
            }

            if (xml->xml_class == JSXML_CLASS_ELEMENT) {
                /* Likewise for namespaces and attributes. */
                for (i = 0, n = xml->xml_namespaces.length; i < n; i++) {
                    ns = XMLARRAY_MEMBER(&xml->xml_namespaces, i,
                                         JSXMLNamespace);
                    if (ns->markflag == JSXML_MARK_SINGLE_OWNER) {
                        js_DestroyXMLNamespace(cx, ns);
#ifdef DEBUG
                        XMLARRAY_SET_MEMBER(&xml->xml_namespaces, i, NULL);
#endif
                    }
                }

                for (i = 0, n = xml->xml_attrs.length; i < n; i++) {
                    attr = XMLARRAY_MEMBER(&xml->xml_attrs, i, JSXML);
                    if (attr->markflag == JSXML_MARK_SINGLE_OWNER) {
                        js_DestroyXML(cx, attr);
#ifdef DEBUG
                        XMLARRAY_SET_MEMBER(&xml->xml_attrs, i, NULL);
#endif
                    }
                }
            }
        }

        /* Destroy name if singly-owned. */
        qn = xml->name;
        if (qn && qn->markflag == JSXML_MARK_SINGLE_OWNER) {
            js_DestroyXMLQName(cx, qn);
#ifdef DEBUG
            xml->name = NULL;
#endif
        }
    }
    UNMETER(xml_stats.livexmlobj);
}

static void
xml_mark_private(JSContext *cx, JSXML *xml, void *arg);

static void
xml_mark_vector(JSContext *cx, JSXML **vec, uint32 len, void *arg)
{
    uint32 i;
    JSXML *elt;

    for (i = 0; i < len; i++) {
        elt = vec[i];
        if (elt->object) {
#ifdef GC_MARK_DEBUG
            char buf[100];
            JSXMLQName *qn = elt->name;

            JS_snprintf(buf, sizeof buf, "%s::%s",
                        qn->uri ? JS_GetStringBytes(qn->uri) : "*",
                        JS_GetStringBytes(qn->localName));
#else
            const char *buf = NULL;
#endif
            JS_MarkGCThing(cx, elt->object, buf, arg);
        } else {
            xml_mark_private(cx, elt, arg);
        }
    }
}

static void
xml_mark_private(JSContext *cx, JSXML *xml, void *arg)
{
    JSXML *parent;
    JSXMLQName *qn;

    if (xml->markflag != JSXML_MARK_CLEAR)
        return;
    xml->markflag = JSXML_MARK_LIVE;

    parent = xml->parent;
    if (parent) {
        if (parent->object)
            JS_MarkGCThing(cx, parent->object, "parent", arg);
        else
            xml_mark_private(cx, parent, arg);
    }

    qn = xml->name;
    if (qn) {
        if (qn->object)
            JS_MarkGCThing(cx, qn->object, "name", arg);
        else
            qname_mark_private(cx, qn, arg);
    }

    if (JSXML_HAS_VALUE(xml)) {
        JS_MarkGCThing(cx, xml->xml_value, "value", arg);
    } else {
        xml_mark_vector(cx,
                        (JSXML **) xml->xml_kids.vector,
                        xml->xml_kids.length,
                        arg);
        XMLArrayTrim(&xml->xml_kids);

        if (xml->xml_class == JSXML_CLASS_LIST) {
            if (xml->xml_target)
                xml_mark_private(cx, xml->xml_target, arg);
            if (xml->xml_targetprop)
                qname_mark_private(cx, xml->xml_targetprop, arg);
        } else {
            namespace_mark_vector(cx,
                                  (JSXMLNamespace **)
                                  xml->xml_namespaces.vector,
                                  xml->xml_namespaces.length,
                                  arg);
            XMLArrayTrim(&xml->xml_namespaces);

            xml_mark_vector(cx,
                            (JSXML **) xml->xml_attrs.vector,
                            xml->xml_attrs.length,
                            arg);
            XMLArrayTrim(&xml->xml_attrs);
        }
    }
}

/*
 * js_XMLObjectOps.newObjectMap == js_NewObjectMap, so XML objects appear to
 * be native.  Therefore, xml_lookupProperty must return a valid JSProperty
 * pointer parameter via *propp to signify "property found".  Since the only
 * call to xml_lookupProperty is via OBJ_LOOKUP_PROPERTY, and then only from
 * js_FindXMLProperty (in this file) and js_FindProperty (in jsobj.c, called
 * from jsinterp.c), the only time we add a JSScopeProperty here is when an
 * unqualified name or XML name is being accessed.
 *
 * This scope property both speeds up subsequent js_Find*Property calls, and
 * keeps the JSOP_NAME code in js_Interpret happy by giving it an sprop with
 * (getter, setter) == (GetProperty, PutProperty).  We can't use that getter
 * and setter as js_XMLClass's getProperty and setProperty, because doing so
 * would break the XML methods, which are function-valued properties of the
 * XML.prototype object.
 *
 * NB: xml_deleteProperty must take care to remove any property added here.
 */
static JSBool
xml_lookupProperty(JSContext *cx, JSObject *obj, jsid id, JSObject **objp,
                   JSProperty **propp)
{
    JSBool found;
    JSScopeProperty *sprop;

    if (!HasProperty(cx, obj, ID_TO_VALUE(id), &found))
        return JS_FALSE;
    if (!found) {
        *objp = obj;
        *propp = NULL;
    } else {
        sprop = js_AddNativeProperty(cx, obj, id, GetProperty, PutProperty,
                                     SPROP_INVALID_SLOT, JSPROP_ENUMERATE,
                                     0, 0);
        if (!sprop)
            return JS_FALSE;
        *objp = obj;
        *propp = (JSProperty *) sprop;
    }
    return JS_TRUE;
}

static JSBool
xml_defineProperty(JSContext *cx, JSObject *obj, jsid id, jsval value,
                   JSPropertyOp getter, JSPropertyOp setter, uintN attrs,
                   JSProperty **propp)
{
    if (JSVAL_IS_FUNCTION(cx, value) || getter || setter ||
        (attrs & JSPROP_ENUMERATE) == 0 ||
        (attrs & (JSPROP_READONLY | JSPROP_PERMANENT | JSPROP_SHARED))) {
        return js_DefineProperty(cx, obj, id, value, getter, setter, attrs,
                                 propp);
    }

    if (!PutProperty(cx, obj, ID_TO_VALUE(id), &value))
        return JS_FALSE;
    if (propp)
        *propp = NULL;
    return JS_TRUE;
}

static JSBool
xml_getProperty(JSContext *cx, JSObject *obj, jsid id, jsval *vp)
{
    if (id == JS_DEFAULT_XML_NAMESPACE_ID) {
        *vp = JSVAL_VOID;
        return JS_TRUE;
    }

    return GetProperty(cx, obj, ID_TO_VALUE(id), vp);
}

static JSBool
xml_setProperty(JSContext *cx, JSObject *obj, jsid id, jsval *vp)
{
    return PutProperty(cx, obj, ID_TO_VALUE(id), vp);
}

static JSBool
FoundProperty(JSContext *cx, JSObject *obj, jsid id, JSProperty *prop,
              JSBool *foundp)
{
    if (prop) {
        *foundp = JS_TRUE;
        return JS_TRUE;
    }
    return HasProperty(cx, obj, ID_TO_VALUE(id), foundp);
}

static JSBool
xml_getAttributes(JSContext *cx, JSObject *obj, jsid id, JSProperty *prop,
                  uintN *attrsp)
{
    JSBool found;

    if (!FoundProperty(cx, obj, id, prop, &found))
        return JS_FALSE;
    *attrsp = found ? JSPROP_ENUMERATE : 0;
    return JS_TRUE;
}

static JSBool
xml_setAttributes(JSContext *cx, JSObject *obj, jsid id, JSProperty *prop,
                  uintN *attrsp)
{
    JSBool found;

    if (!FoundProperty(cx, obj, id, prop, &found))
        return JS_FALSE;
    if (found) {
        JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                             JSMSG_CANT_SET_XML_ATTRS);
    }
    return !found;
}

static JSBool
xml_deleteProperty(JSContext *cx, JSObject *obj, jsid id, jsval *rval)
{
    /*
     * If this object has its own (mutable) scope, and if id isn't an index,
     * then we may have added a property to the scope in xml_lookupProperty
     * for it to return to mean "found" and to provide a handle for access
     * operations to call the property's getter or setter.  The property also
     * helps speed up unqualified accesses via the property cache, avoiding
     * what amount to two HasProperty searches.
     *
     * But now it's time to remove any such property, to purge the property
     * cache and remove the scope entry.
     */
    if (OBJ_SCOPE(obj)->object == obj && !JSID_IS_INT(id)) {
        if (!js_DeleteProperty(cx, obj, id, rval))
            return JS_FALSE;
    }

    return DeleteProperty(cx, obj, ID_TO_VALUE(id), rval);
}

static JSBool
xml_defaultValue(JSContext *cx, JSObject *obj, JSType hint, jsval *vp)
{
    JSXML *xml;

    if (hint == JSTYPE_OBJECT) {
        /* Called from for..in code in js_Interpret: return an XMLList. */
        xml = (JSXML *) JS_GetPrivate(cx, obj);
        if (xml->xml_class != JSXML_CLASS_LIST) {
            obj = ToXMLList(cx, OBJECT_TO_JSVAL(obj));
            if (!obj)
                return JS_FALSE;
        }
        *vp = OBJECT_TO_JSVAL(obj);
        return JS_TRUE;
    }

    return JS_CallFunctionName(cx, obj, js_toString_str, 0, NULL, vp);
}

static JSBool
xml_enumerate(JSContext *cx, JSObject *obj, JSIterateOp enum_op,
              jsval *statep, jsid *idp)
{
    JSXML *xml;
    uint32 length, index;
    JSXMLArrayCursor *cursor;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    length = JSXML_LENGTH(xml);

    switch (enum_op) {
      case JSENUMERATE_INIT:
        if (length == 0) {
            cursor = NULL;
        } else {
            cursor = (JSXMLArrayCursor *) JS_malloc(cx, sizeof *cursor);
            if (!cursor)
                return JS_FALSE;
            XMLArrayCursorInit(cursor, &xml->xml_kids);
        }
        *statep = PRIVATE_TO_JSVAL(cursor);
        if (idp)
            *idp = INT_TO_JSID(length);
        break;

      case JSENUMERATE_NEXT:
        cursor = JSVAL_TO_PRIVATE(*statep);
        if (cursor && cursor->array && (index = cursor->index) < length) {
            *idp = INT_TO_JSID(index);
            cursor->index = index + 1;
            break;
        }
        /* FALL THROUGH */

      case JSENUMERATE_DESTROY:
        cursor = JSVAL_TO_PRIVATE(*statep);
        if (cursor) {
            XMLArrayCursorFinish(cursor);
            JS_free(cx, cursor);
        }
        *statep = JSVAL_NULL;
        break;
    }
    return JS_TRUE;
}

static JSBool
xml_checkAccess(JSContext *cx, JSObject *obj, jsid id, JSAccessMode mode,
                jsval *vp, uintN *attrsp)
{
    if (!cx->runtime->checkObjectAccess)
        return JS_TRUE;
    return cx->runtime->checkObjectAccess(cx, obj, ID_TO_VALUE(id), mode, vp);
}

static JSBool
xml_hasInstance(JSContext *cx, JSObject *obj, jsval v, JSBool *bp)
{
    return JS_TRUE;
}

static uint32
xml_mark(JSContext *cx, JSObject *obj, void *arg)
{
    JSXML *xml;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    xml_mark_private(cx, xml, arg);
    return 0;
}

static void
xml_clear(JSContext *cx, JSObject *obj)
{
}

static JSBool
HasSimpleContent(JSXML *xml)
{
    JSXML *kid;
    JSBool simple;
    uint32 i, n;

again:
    switch (xml->xml_class) {
      case JSXML_CLASS_COMMENT:
      case JSXML_CLASS_PROCESSING_INSTRUCTION:
        return JS_FALSE;
      case JSXML_CLASS_LIST:
        if (xml->xml_kids.length == 0)
            return JS_TRUE;
        if (xml->xml_kids.length == 1) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML);
            xml = kid;
            goto again;
        }
        /* FALL THROUGH */
      default:
        simple = JS_TRUE;
        for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                simple = JS_FALSE;
                break;
            }
        }
        return simple;
    }
}

static JSObject *
xml_getMethod(JSContext *cx, JSObject *obj, jsid id, jsval *vp)
{
    JSXML *xml;
    jsval fval;

    JS_ASSERT(JS_InstanceOf(cx, obj, &js_XMLClass, NULL));
    xml = (JSXML *) JS_GetPrivate(cx, obj);

retry:
    /* 11.2.2.1 Step 3(d) onward. */
    if (!GetFunction(cx, obj, xml, id, &fval))
        return NULL;

    if (JSVAL_IS_VOID(fval) && OBJECT_IS_XML(cx, obj)) {
        if (xml->xml_class == JSXML_CLASS_LIST) {
            if (xml->xml_kids.length == 1) {
                xml = XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML);
                obj = js_GetXMLObject(cx, xml);
                if (!obj)
                    return NULL;
                goto retry;
            }
        } else if (HasSimpleContent(xml)) {
            JSString *str;

            str = js_ValueToString(cx, OBJECT_TO_JSVAL(obj));
            if (!str || !js_ValueToObject(cx, STRING_TO_JSVAL(str), &obj))
                return NULL;
            if (!js_GetProperty(cx, obj, id, &fval))
                return NULL;
        }
    }

    *vp = fval;
    return obj;
}

static JSBool
xml_enumerateValues(JSContext *cx, JSObject *obj, JSIterateOp enum_op,
                    jsval *statep, jsid *idp, jsval *vp)
{
    JSXML *xml, *kid;
    uint32 length, index;
    JSXMLArrayCursor *cursor;
    JSObject *kidobj;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    length = JSXML_LENGTH(xml);
    JS_ASSERT(INT_FITS_IN_JSVAL(length));

    switch (enum_op) {
      case JSENUMERATE_INIT:
        if (length == 0) {
            cursor = NULL;
        } else {
            cursor = (JSXMLArrayCursor *) JS_malloc(cx, sizeof *cursor);
            if (!cursor)
                return JS_FALSE;
            XMLArrayCursorInit(cursor, &xml->xml_kids);
        }
        *statep = PRIVATE_TO_JSVAL(cursor);
        if (idp)
            *idp = INT_TO_JSID(length);
        if (vp)
            *vp = JSVAL_VOID;
        break;

      case JSENUMERATE_NEXT:
        cursor = JSVAL_TO_PRIVATE(*statep);
        if (cursor && cursor->array && (index = cursor->index) < length) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, index, JSXML);
            kidobj = js_GetXMLObject(cx, kid);
            if (!kidobj)
                return JS_FALSE;
            JS_ASSERT(INT_FITS_IN_JSVAL(index));
            *idp = INT_TO_JSID(index);
            *vp = OBJECT_TO_JSVAL(kidobj);
            cursor->index = index + 1;
            break;
        }
        /* FALL THROUGH */

      case JSENUMERATE_DESTROY:
        cursor = JSVAL_TO_PRIVATE(*statep);
        if (cursor) {
            XMLArrayCursorFinish(cursor);
            JS_free(cx, cursor);
        }
        *statep = JSVAL_NULL;
        break;
    }
    return JS_TRUE;
}

static JSBool
xml_equality(JSContext *cx, JSObject *obj, jsval v, JSBool *bp)
{
    JSXML *xml, *vxml;
    JSObject *vobj;
    JSBool ok;
    JSString *str, *vstr;
    jsdouble d, d2;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    vxml = NULL;
    if (!JSVAL_IS_PRIMITIVE(v)) {
        vobj = JSVAL_TO_OBJECT(v);
        if (OBJECT_IS_XML(cx, vobj))
            vxml = (JSXML *) JS_GetPrivate(cx, vobj);
    }

    if (xml->xml_class == JSXML_CLASS_LIST) {
        ok = Equals(cx, xml, v, bp);
    } else if (vxml) {
        if (vxml->xml_class == JSXML_CLASS_LIST) {
            ok = Equals(cx, vxml, OBJECT_TO_JSVAL(obj), bp);
        } else {
            if (((xml->xml_class == JSXML_CLASS_TEXT ||
                  xml->xml_class == JSXML_CLASS_ATTRIBUTE) &&
                 HasSimpleContent(vxml)) ||
                ((vxml->xml_class == JSXML_CLASS_TEXT ||
                  vxml->xml_class == JSXML_CLASS_ATTRIBUTE) &&
                 HasSimpleContent(xml))) {
                ok = JS_EnterLocalRootScope(cx);
                if (ok) {
                    str = js_ValueToString(cx, OBJECT_TO_JSVAL(obj));
                    vstr = js_ValueToString(cx, v);
                    ok = str && vstr;
                    if (ok)
                        *bp = !js_CompareStrings(str, vstr);
                    JS_LeaveLocalRootScope(cx);
                }
            } else {
                ok = XMLEquals(cx, xml, vxml, bp);
            }
        }
    } else {
        ok = JS_EnterLocalRootScope(cx);
        if (ok) {
            if (HasSimpleContent(xml)) {
                str = js_ValueToString(cx, OBJECT_TO_JSVAL(obj));
                vstr = js_ValueToString(cx, v);
                ok = str && vstr;
                if (ok)
                    *bp = !js_CompareStrings(str, vstr);
            } else if (JSVAL_IS_STRING(v) || JSVAL_IS_NUMBER(v)) {
                str = js_ValueToString(cx, OBJECT_TO_JSVAL(obj));
                if (!str) {
                    ok = JS_FALSE;
                } else if (JSVAL_IS_STRING(v)) {
                    *bp = !js_CompareStrings(str, JSVAL_TO_STRING(v));
                } else {
                    ok = js_ValueToNumber(cx, STRING_TO_JSVAL(str), &d);
                    if (ok) {
                        d2 = JSVAL_IS_INT(v) ? JSVAL_TO_INT(v)
                                             : *JSVAL_TO_DOUBLE(v);
                        *bp = JSDOUBLE_COMPARE(d, ==, d2, JS_FALSE);
                    }
                }
            } else {
                *bp = JS_FALSE;
            }
            JS_LeaveLocalRootScope(cx);
        }
    }
    return ok;
}

static JSBool
xml_concatenate(JSContext *cx, JSObject *obj, jsval v, jsval *vp)
{
    JSBool ok;
    JSObject *listobj, *robj;
    JSXML *list, *lxml, *rxml;

    ok = JS_EnterLocalRootScope(cx);
    if (!ok)
        return JS_FALSE;

    listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
    if (!listobj) {
        ok = JS_FALSE;
        goto out;
    }

    list = (JSXML *) JS_GetPrivate(cx, listobj);
    lxml = (JSXML *) JS_GetPrivate(cx, obj);
    ok = Append(cx, list, lxml);
    if (!ok)
        goto out;

    if (VALUE_IS_XML(cx, v)) {
        rxml = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
    } else {
        robj = ToXML(cx, v);
        if (!robj) {
            ok = JS_FALSE;
            goto out;
        }
        rxml = (JSXML *) JS_GetPrivate(cx, robj);
    }
    ok = Append(cx, list, rxml);
    if (!ok)
        goto out;

    *vp = OBJECT_TO_JSVAL(listobj);
out:
    JS_LeaveLocalRootScope(cx);
    return ok;
}

/* Use js_NewObjectMap so XML objects satisfy OBJ_IS_NATIVE tests. */
JSXMLObjectOps js_XMLObjectOps = {
  { js_NewObjectMap,            js_DestroyObjectMap,
    xml_lookupProperty,         xml_defineProperty,
    xml_getProperty,            xml_setProperty,
    xml_getAttributes,          xml_setAttributes,
    xml_deleteProperty,         xml_defaultValue,
    xml_enumerate,              xml_checkAccess,
    NULL,                       NULL,
    NULL,                       NULL,
    NULL,                       xml_hasInstance,
    js_SetProtoOrParent,        js_SetProtoOrParent,
    xml_mark,                   xml_clear,
    NULL,                       NULL },
    xml_getMethod,              xml_enumerateValues,
    xml_equality,               xml_concatenate
};

static JSObjectOps *
xml_getObjectOps(JSContext *cx, JSClass *clasp)
{
    return &js_XMLObjectOps.base;
}

JSClass js_XMLClass = {
    js_XML_str,        JSCLASS_HAS_PRIVATE,
    JS_PropertyStub,   JS_PropertyStub,   JS_PropertyStub,   JS_PropertyStub,
    JS_EnumerateStub,  JS_ResolveStub,    JS_ConvertStub,    xml_finalize,
    xml_getObjectOps,  NULL,              NULL,              NULL,
    NULL,              NULL,              NULL,              NULL
};

static JSObject *
CallConstructorFunction(JSContext *cx, JSObject *obj, JSClass *clasp,
                        uintN argc, jsval *argv)
{
    JSObject *tmp;
    jsval rval;

    while ((tmp = OBJ_GET_PARENT(cx, obj)) != NULL)
        obj = tmp;
    if (!JS_CallFunctionName(cx, obj, clasp->name, argc, argv, &rval))
        return NULL;
    JS_ASSERT(!JSVAL_IS_PRIMITIVE(rval));
    return JSVAL_TO_OBJECT(rval);
}

static JSBool
xml_addNamespace(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                 jsval *rval)
{
    JSXML *xml;
    JSObject *nsobj;
    JSXMLNamespace *ns;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (xml->xml_class != JSXML_CLASS_ELEMENT)
        return JS_TRUE;
    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;

    nsobj = CallConstructorFunction(cx, obj, &js_NamespaceClass.base, 1, argv);
    if (!nsobj)
        return JS_FALSE;
    argv[0] = OBJECT_TO_JSVAL(nsobj);

    ns = (JSXMLNamespace *) JS_GetPrivate(cx, nsobj);
    if (!AddInScopeNamespace(cx, xml, ns))
        return JS_FALSE;
    ns->declared = JS_TRUE;
    *rval = OBJECT_TO_JSVAL(obj);
    return JS_TRUE;
}

static JSBool
xml_appendChild(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                jsval *rval)
{
    JSXML *xml, *vxml;
    jsval name, v;
    JSObject *vobj;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;

    if (!js_GetAnyName(cx, &name))
        return JS_FALSE;

    if (!GetProperty(cx, obj, name, &v))
        return JS_FALSE;

    JS_ASSERT(!JSVAL_IS_PRIMITIVE(v));
    vobj = JSVAL_TO_OBJECT(v);
    JS_ASSERT(OBJECT_IS_XML(cx, vobj));
    vxml = (JSXML *) JS_GetPrivate(cx, vobj);
    JS_ASSERT(vxml->xml_class == JSXML_CLASS_LIST);

    if (!IndexToIdVal(cx, vxml->xml_kids.length, &name))
        return JS_FALSE;
    if (!PutProperty(cx, JSVAL_TO_OBJECT(v), name, &argv[0]))
        return JS_FALSE;

    *rval = OBJECT_TO_JSVAL(obj);
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_attribute(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
              jsval *rval)
{
    JSXMLQName *qn;
    jsval name;

    qn = ToAttributeName(cx, argv[0]);
    if (!qn)
        return JS_FALSE;
    name = OBJECT_TO_JSVAL(qn->object);
    return GetProperty(cx, obj, name, rval);
}

/* XML and XMLList */
static JSBool
xml_attributes(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
               jsval *rval)
{
    jsval name;
    JSXMLQName *qn;

    name = ATOM_KEY(cx->runtime->atomState.starAtom);
    qn = ToAttributeName(cx, name);
    if (!qn)
        return JS_FALSE;
    name = OBJECT_TO_JSVAL(qn->object);
    return GetProperty(cx, obj, name, rval);
}

/* XML and XMLList */
static JSBool
xml_child_helper(JSContext *cx, JSObject *obj, JSXML *xml, jsval name,
                 jsval *rval)
{
    uint32 index;
    JSXML *kid;
    JSObject *kidobj;

    /* ECMA-357 13.4.4.6 */
    JS_ASSERT(xml->xml_class != JSXML_CLASS_LIST);

    if (js_IdIsIndex(name, &index)) {
        if (index >= JSXML_LENGTH(xml)) {
            *rval = JSVAL_VOID;
        } else {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, index, JSXML);
            kidobj = js_GetXMLObject(cx, kid);
            if (!kidobj)
                return JS_FALSE;
            *rval = OBJECT_TO_JSVAL(kidobj);
        }
        return JS_TRUE;
    }

    return GetProperty(cx, obj, name, rval);
}

static JSBool
xml_child(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSXML *xml, *list, *kid, *vxml;
    jsval name, v;
    uint32 i, n;
    JSObject *listobj, *kidobj;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    name = argv[0];
    if (xml->xml_class == JSXML_CLASS_LIST) {
        /* ECMA-357 13.5.4.4 */
        listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
        if (!listobj)
            return JS_FALSE;

        *rval = OBJECT_TO_JSVAL(listobj);
        list = (JSXML *) JS_GetPrivate(cx, listobj);
        list->xml_target = xml;

        for (i = 0, n = xml->xml_kids.length; i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            kidobj = js_GetXMLObject(cx, kid);
            if (!kidobj)
                return JS_FALSE;
            if (!xml_child_helper(cx, kidobj, kid, name, &v))
                return JS_FALSE;

            JS_ASSERT(!JSVAL_IS_PRIMITIVE(v));
            vxml = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
            if (JSXML_LENGTH(vxml) != 0 && !Append(cx, list, vxml))
                return JS_FALSE;
        }
        return JS_TRUE;
    }

    return xml_child_helper(cx, obj, xml, name, rval);
}

static JSBool
xml_childIndex(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
               jsval *rval)
{
    JSXML *xml, *parent;
    uint32 i, n;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    parent = xml->parent;
    if (!parent || xml->xml_class == JSXML_CLASS_ATTRIBUTE) {
        *rval = DOUBLE_TO_JSVAL(cx->runtime->jsNaN);
        return JS_TRUE;
    }
    for (i = 0, n = JSXML_LENGTH(parent); i < n; i++) {
        if (XMLARRAY_MEMBER(&parent->xml_kids, i, JSXML) == xml)
            break;
    }
    JS_ASSERT(i < n);
    return js_NewNumberValue(cx, i, rval);
}

/* XML and XMLList */
static JSBool
xml_children(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
             jsval *rval)
{
    jsval name;

    name = ATOM_KEY(cx->runtime->atomState.starAtom);
    return GetProperty(cx, obj, name, rval);
}

/* XML and XMLList */
static JSBool
xml_comments(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
             jsval *rval)
{
    JSXML *xml, *list, *kid, *vxml;
    JSObject *listobj, *kidobj;
    JSBool ok;
    uint32 i, n;
    jsval v;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
    if (!listobj)
        return JS_FALSE;

    *rval = OBJECT_TO_JSVAL(listobj);
    list = (JSXML *) JS_GetPrivate(cx, listobj);
    list->xml_target = xml;

    ok = JS_TRUE;

    if (xml->xml_class == JSXML_CLASS_LIST) {
        /* 13.5.4.6 Step 2. */
        for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                ok = JS_EnterLocalRootScope(cx);
                if (!ok)
                    break;
                kidobj = js_GetXMLObject(cx, kid);
                ok = kidobj
                     ? xml_comments(cx, kidobj, argc, argv, &v)
                     : JS_FALSE;
                JS_LeaveLocalRootScope(cx);
                if (!ok)
                    break;
                vxml = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
                if (JSXML_LENGTH(vxml) != 0) {
                    ok = Append(cx, list, vxml);
                    if (!ok)
                        break;
                }
            }
        }
    } else {
        /* 13.4.4.9 Step 2. */
        for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_COMMENT) {
                ok = Append(cx, list, kid);
                if (!ok)
                    break;
            }
        }
    }

    return ok;
}

/* XML and XMLList */
static JSBool
xml_contains(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
             jsval *rval)
{
    JSXML *xml, *kid;
    jsval value;
    JSBool eq;
    JSObject *kidobj;
    uint32 i, n;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    value = argv[0];
    if (xml->xml_class == JSXML_CLASS_LIST) {
        eq = JS_FALSE;
        for (i = 0, n = xml->xml_kids.length; i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            kidobj = js_GetXMLObject(cx, kid);
            if (!kidobj || !xml_equality(cx, kidobj, value, &eq))
                return JS_FALSE;
            if (eq)
                break;
        }
    } else {
        if (!Equals(cx, xml, value, &eq))
            return JS_FALSE;
    }
    *rval = BOOLEAN_TO_JSVAL(eq);
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_copy(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSXML *xml, *copy;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    copy = DeepCopy(cx, xml, NULL, 0);
    if (!copy)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(copy->object);
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_descendants(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                jsval *rval)
{
    JSXML *xml, *list;
    jsval name;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    name = (argc == 0) ? ATOM_KEY(cx->runtime->atomState.starAtom) : argv[0];
    list = Descendants(cx, xml, name);
    if (!list)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(list->object);
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_elements(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
             jsval *rval)
{
    JSXML *xml, *list, *kid, *vxml;
    jsval name, v;
    JSXMLQName *nameqn;
    jsid funid;
    JSObject *listobj, *kidobj;
    JSBool ok;
    uint32 i, n;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    name = (argc == 0) ? ATOM_KEY(cx->runtime->atomState.starAtom) : argv[0];
    nameqn = ToXMLName(cx, name, &funid);
    if (!nameqn)
        return JS_FALSE;
    argv[0] = OBJECT_TO_JSVAL(nameqn->object);

    listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
    if (!listobj)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(listobj);
    if (funid)
        return JS_TRUE;

    list = (JSXML *) JS_GetPrivate(cx, listobj);
    list->xml_target = xml;
    list->xml_targetprop = nameqn;
    ok = JS_TRUE;

    if (xml->xml_class == JSXML_CLASS_LIST) {
        /* 13.5.4.6 */
        for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                ok = JS_EnterLocalRootScope(cx);
                if (!ok)
                    break;
                kidobj = js_GetXMLObject(cx, kid);
                ok = kidobj
                     ? xml_elements(cx, kidobj, argc, argv, &v)
                     : JS_FALSE;
                JS_LeaveLocalRootScope(cx);
                if (!ok)
                    break;
                vxml = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
                if (JSXML_LENGTH(vxml) != 0) {
                    ok = Append(cx, list, vxml);
                    if (!ok)
                        break;
                }
            }
        }
    } else {
        for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_ELEMENT &&
                MatchElemName(nameqn, kid)) {
                ok = Append(cx, list, kid);
                if (!ok)
                    break;
            }
        }
    }

    return ok;
}

/* XML and XMLList */
static JSBool
xml_hasOwnProperty(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                   jsval *rval)
{
    jsval name;
    JSBool found;

    name = argv[0];
    if (!HasProperty(cx, obj, name, &found))
        return JS_FALSE;
    if (!found) {
        return js_HasOwnPropertyHelper(cx, obj, js_LookupProperty, argc, argv,
                                       rval);
    }
    *rval = JSVAL_TRUE;
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_hasComplexContent(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                      jsval *rval)
{
    JSXML *xml, *kid;
    JSObject *kidobj;
    uint32 i, n;

again:
    xml = (JSXML *) JS_GetPrivate(cx, obj);
    switch (xml->xml_class) {
      case JSXML_CLASS_ATTRIBUTE:
      case JSXML_CLASS_COMMENT:
      case JSXML_CLASS_PROCESSING_INSTRUCTION:
      case JSXML_CLASS_TEXT:
        *rval = JSVAL_FALSE;
        break;
      case JSXML_CLASS_LIST:
        if (xml->xml_kids.length == 0) {
            *rval = JSVAL_TRUE;
        } else if (xml->xml_kids.length == 1) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML);
            kidobj = js_GetXMLObject(cx, kid);
            JS_UNLOCK_OBJ(cx, obj);
            if (!kidobj)
                return JS_FALSE;
            obj = kidobj;
            goto again;
        }
        /* FALL THROUGH */
      default:
        *rval = JSVAL_FALSE;
        for (i = 0, n = xml->xml_kids.length; i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                *rval = JSVAL_TRUE;
                break;
            }
        }
        break;
    }
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_hasSimpleContent(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                     jsval *rval)
{
    JSXML *xml;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    *rval = BOOLEAN_TO_JSVAL(HasSimpleContent(xml));
    return JS_TRUE;
}

static JSBool
xml_inScopeNamespaces(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                      jsval *rval)
{
    JSObject *arrayobj, *nsobj;
    JSXML *xml;
    uint32 length, i, j, n;
    JSXMLNamespace *ns, *ns2;
    jsval v;

    arrayobj = js_NewArrayObject(cx, 0, NULL);
    if (!arrayobj)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(arrayobj);
    length = 0;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    do {
        if (xml->xml_class != JSXML_CLASS_ELEMENT)
            continue;
        for (i = 0, n = xml->xml_namespaces.length; i < n; i++) {
            ns = XMLARRAY_MEMBER(&xml->xml_namespaces, i, JSXMLNamespace);

            for (j = 0; j < length; j++) {
                if (!JS_GetElement(cx, arrayobj, j, &v))
                    return JS_FALSE;
                nsobj = JSVAL_TO_OBJECT(v);
                ns2 = (JSXMLNamespace *) JS_GetPrivate(cx, nsobj);
                if ((ns2->prefix && ns->prefix)
                    ? !js_CompareStrings(ns2->prefix, ns->prefix)
                    : !js_CompareStrings(ns2->uri, ns->uri)) {
                    break;
                }
            }

            if (j == length) {
                nsobj = js_GetXMLNamespaceObject(cx, ns);
                if (!nsobj)
                    return JS_FALSE;
                v = OBJECT_TO_JSVAL(nsobj);
                if (!JS_SetElement(cx, arrayobj, length, &v))
                    return JS_FALSE;
                ++length;
            }
        }
    } while ((xml = xml->parent) != NULL);
    return JS_TRUE;
}

static JSBool
xml_insertChildAfter(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                     jsval *rval)
{
    JSXML *xml, *kid;
    jsval arg;
    uint32 i;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (!JSXML_HAS_KIDS(xml))
        return JS_TRUE;

    arg = argv[0];
    if (JSVAL_IS_NULL(arg)) {
        kid = NULL;
        i = 0;
    } else {
        if (!VALUE_IS_XML(cx, arg))
            return JS_TRUE;
        kid = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(arg));
        i = XMLARRAY_FIND_MEMBER(&xml->xml_kids, kid, NULL);
        if (i == XML_NOT_FOUND)
            return JS_TRUE;
        ++i;
    }

    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;
    if (!Insert(cx, xml, INT_TO_JSID(i), argv[1]))
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(obj);
    return JS_TRUE;
}

static JSBool
xml_insertChildBefore(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                      jsval *rval)
{
    JSXML *xml, *kid;
    jsval arg;
    uint32 i;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (!JSXML_HAS_KIDS(xml))
        return JS_TRUE;

    arg = argv[0];
    if (JSVAL_IS_NULL(arg)) {
        kid = NULL;
        i = xml->xml_kids.length;
    } else {
        if (!VALUE_IS_XML(cx, arg))
            return JS_TRUE;
        kid = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(arg));
        i = XMLARRAY_FIND_MEMBER(&xml->xml_kids, kid, NULL);
        if (i == XML_NOT_FOUND)
            return JS_TRUE;
    }

    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;
    if (!Insert(cx, xml, INT_TO_JSID(i), argv[1]))
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(obj);
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_length(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSXML *xml;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (xml->xml_class != JSXML_CLASS_LIST) {
        *rval = JSVAL_ONE;
    } else {
        if (!js_NewNumberValue(cx, xml->xml_kids.length, rval))
            return JS_FALSE;
    }
    return JS_TRUE;
}

static JSBool
xml_localName(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
              jsval *rval)
{
    JSXML *xml;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    *rval = xml->name ? STRING_TO_JSVAL(xml->name->localName) : JSVAL_NULL;
    return JS_TRUE;
}

static JSBool
xml_name(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSXML *xml;
    JSObject *nameobj;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (!xml->name) {
        *rval = JSVAL_NULL;
    } else {
        nameobj = js_GetXMLQNameObject(cx, xml->name);
        if (!nameobj)
            return JS_FALSE;
        *rval = OBJECT_TO_JSVAL(nameobj);
    }
    return JS_TRUE;
}

static JSBool
xml_namespace(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
              jsval *rval)
{
    JSXML *xml;
    JSObject *arrayobj;
    JSBool ok;
    jsuint i, length;
    jsval v;
    JSXMLArray inScopeNSes;
    JSXMLNamespace *ns;
    JSString *prefix;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (argc == 0 &&
        (xml->xml_class == JSXML_CLASS_TEXT ||
         xml->xml_class == JSXML_CLASS_COMMENT ||
         xml->xml_class == JSXML_CLASS_PROCESSING_INSTRUCTION)) {
        *rval = JSVAL_NULL;
        return JS_TRUE;
    }

    if (!xml_inScopeNamespaces(cx, obj, 0, NULL, rval))
        return JS_FALSE;
    arrayobj = JSVAL_TO_OBJECT(*rval);
    ok = js_GetLengthProperty(cx, arrayobj, &length);
    if (!ok)
        return JS_FALSE;

    if (argc == 0) {
        if (!XMLArrayInit(cx, &inScopeNSes, length))
            return JS_FALSE;

        for (i = 0; i < length; i++) {
            ok = OBJ_GET_PROPERTY(cx, arrayobj, INT_TO_JSID(i), &v);
            if (!ok)
                break;
            JS_ASSERT(!JSVAL_IS_PRIMITIVE(v));
            ns = (JSXMLNamespace *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
            XMLARRAY_SET_MEMBER(&inScopeNSes, i, ns);
        }

        inScopeNSes.length = i;
        ns = ok ? GetNamespace(cx, xml->name, &inScopeNSes) : NULL;
        XMLArrayFinish(cx, &inScopeNSes, NULL);
        if (!ns)
            return JS_FALSE;

        *rval = OBJECT_TO_JSVAL(ns->object);
    } else {
        prefix = js_ValueToString(cx, argv[0]);
        if (!prefix)
            return JS_FALSE;

        for (i = 0; i < length; i++) {
            if (!OBJ_GET_PROPERTY(cx, arrayobj, INT_TO_JSID(i), &v))
                return JS_FALSE;
            JS_ASSERT(!JSVAL_IS_PRIMITIVE(v));
            ns = (JSXMLNamespace *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
            if (ns->prefix && !js_CompareStrings(ns->prefix, prefix))
                break;
        }

        *rval = (i < length) ? OBJECT_TO_JSVAL(ns->object) : JSVAL_VOID;
    }
    return JS_TRUE;
}

static JSBool
namespace_match(const void *a, const void *b)
{
    const JSXMLNamespace *nsa = (const JSXMLNamespace *) a;
    const JSXMLNamespace *nsb = (const JSXMLNamespace *) b;

    if (nsb->prefix)
        return nsa->prefix && !js_CompareStrings(nsa->prefix, nsb->prefix);
    return !js_CompareStrings(nsa->uri, nsb->uri);
}

static JSBool
xml_namespaceDeclarations(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                          jsval *rval)
{
    JSObject *arrayobj, *nsobj;
    JSXML *xml, *yml;
    JSBool ok;
    JSXMLArray ancestors, declared;
    uint32 i, n;
    JSXMLNamespace *ns;
    jsval v;

    arrayobj = js_NewArrayObject(cx, 0, NULL);
    if (!arrayobj)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(arrayobj);

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (JSXML_HAS_VALUE(xml) || xml->xml_class == JSXML_CLASS_LIST)
        return JS_TRUE;

    /* From here, control flow must goto out to finish these arrays. */
    ok = JS_TRUE;
    XMLARRAY_INIT(cx, &ancestors, 0);
    XMLARRAY_INIT(cx, &declared, 0);
    yml = xml;

    while ((yml = yml->parent) != NULL) {
        JS_ASSERT(yml->xml_class == JSXML_CLASS_ELEMENT);
        for (i = 0, n = yml->xml_namespaces.length; i < n; i++) {
            ns = XMLARRAY_MEMBER(&yml->xml_namespaces, i, JSXMLNamespace);
            if (!XMLARRAY_HAS_MEMBER(&ancestors, ns, namespace_match)) {
                ok = XMLARRAY_APPEND(cx, &ancestors, ns);
                if (!ok)
                    goto out;
            }
        }
    }

    for (i = 0, n = xml->xml_namespaces.length; i < n; i++) {
        ns = XMLARRAY_MEMBER(&xml->xml_namespaces, i, JSXMLNamespace);
        if (!ns->declared)
            continue;
        if (!XMLARRAY_HAS_MEMBER(&ancestors, ns, namespace_match)) {
            ok = XMLARRAY_APPEND(cx, &declared, ns);
            if (!ok)
                goto out;
        }
    }

    for (i = 0, n = declared.length; i < n; i++) {
        ns = XMLARRAY_MEMBER(&declared, i, JSXMLNamespace);
        nsobj = js_GetXMLNamespaceObject(cx, ns);
        if (!nsobj) {
            ok = JS_FALSE;
            goto out;
        }
        v = OBJECT_TO_JSVAL(nsobj);
        ok = OBJ_SET_PROPERTY(cx, arrayobj, INT_TO_JSID(i), &v);
        if (!ok)
            goto out;
    }

out:
    XMLARRAY_FINISH(cx, &ancestors, NULL);
    XMLARRAY_FINISH(cx, &declared, NULL);
    return ok;
}

static const char js_attribute_str[] = "attribute";
static const char js_text_str[]      = "text";

static const char *xml_class_str[] = {
    "list",
    "element",
    js_attribute_str,
    "processing-instruction",
    js_text_str,
    "comment"
};

static JSBool
xml_nodeKind(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
             jsval *rval)
{
    JSXML *xml;
    JSString *str;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    str = JS_InternString(cx, xml_class_str[xml->xml_class]);
    if (!str)
        return JS_FALSE;
    *rval = STRING_TO_JSVAL(str);
    return JS_TRUE;
}

static JSBool
NormalizingDelete(JSContext *cx, JSObject *obj, JSXML *xml, jsval id)
{
    jsval junk;

    if (xml->xml_class == JSXML_CLASS_LIST)
        return DeleteProperty(cx, obj, id, &junk);
    return DeleteByIndex(cx, xml, id, &junk);
}

/*
 * Erratum? the testcase js/tests/e4x/XML/13.4.4.26.js wants all-whitespace
 * text between tags to be removed by normalize.
 */
static JSBool
IsXMLSpace(JSString *str)
{
    const jschar *cp, *end;

    cp = JSSTRING_CHARS(str);
    end = cp + JSSTRING_LENGTH(str);
    while (cp < end) {
        if (!JS_ISXMLSPACE(*cp))
            return JS_FALSE;
        ++cp;
    }
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_normalize(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
              jsval *rval)
{
    JSXML *xml, *kid, *kid2;
    uint32 i, n;
    JSObject *kidobj;
    JSString *str;
    jsval junk;

    *rval = OBJECT_TO_JSVAL(obj);
    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (!JSXML_HAS_KIDS(xml))
        return JS_TRUE;

    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;

    for (i = 0, n = xml->xml_kids.length; i < n; i++) {
        kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
        if (kid->xml_class == JSXML_CLASS_ELEMENT) {
            kidobj = js_GetXMLObject(cx, kid);
            if (!kidobj || !xml_normalize(cx, kidobj, argc, argv, &junk))
                return JS_FALSE;
        } else if (kid->xml_class == JSXML_CLASS_TEXT) {
            while (i + 1 < n &&
                   (kid2 = XMLARRAY_MEMBER(&xml->xml_kids, i + 1, JSXML))
                   ->xml_class == JSXML_CLASS_TEXT) {
                str = js_ConcatStrings(cx, kid->xml_value, kid2->xml_value);
                if (!str)
                    return JS_FALSE;
                if (!NormalizingDelete(cx, obj, xml, INT_TO_JSVAL(i + 1)))
                    return JS_FALSE;
                n = xml->xml_kids.length;
                kid->xml_value = str;
            }
            if (IS_EMPTY(kid->xml_value) || IsXMLSpace(kid->xml_value)) {
                if (!NormalizingDelete(cx, obj, xml, INT_TO_JSVAL(i)))
                    return JS_FALSE;
                n = xml->xml_kids.length;
                --i;
            }
        }
    }

    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_parent(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSXML *xml, *parent, *kid;
    uint32 i, n;
    JSObject *parentobj;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    parent = xml->parent;
    if (xml->xml_class == JSXML_CLASS_LIST) {
        *rval = JSVAL_VOID;
        n = xml->xml_kids.length;
        if (n == 0)
            return JS_TRUE;

        kid = XMLARRAY_MEMBER(&xml->xml_kids, 0, JSXML);
        parent = kid->parent;
        for (i = 1; i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->parent != parent)
                return JS_TRUE;
        }
    }

    if (!parent) {
        *rval = JSVAL_NULL;
        return JS_TRUE;
    }

    parentobj = js_GetXMLObject(cx, parent);
    if (!parentobj)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(parentobj);
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_processingInstructions(JSContext *cx, JSObject *obj, uintN argc,
                           jsval *argv, jsval *rval)
{
    JSXML *xml, *list, *kid, *vxml;
    jsval name, v;
    JSXMLQName *nameqn;
    jsid funid;
    JSObject *listobj, *kidobj;
    JSBool ok;
    uint32 i, n;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    name = (argc == 0) ? ATOM_KEY(cx->runtime->atomState.starAtom) : argv[0];
    nameqn = ToXMLName(cx, name, &funid);
    if (!nameqn)
        return JS_FALSE;
    argv[0] = OBJECT_TO_JSVAL(nameqn->object);

    listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
    if (!listobj)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(listobj);
    if (funid)
        return JS_TRUE;

    list = (JSXML *) JS_GetPrivate(cx, listobj);
    list->xml_target = xml;
    list->xml_targetprop = nameqn;
    ok = JS_TRUE;

    if (xml->xml_class == JSXML_CLASS_LIST) {
        /* 13.5.4.17 Step 4 (misnumbered 9 -- Erratum?). */
        for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                ok = JS_EnterLocalRootScope(cx);
                if (!ok)
                    break;
                kidobj = js_GetXMLObject(cx, kid);
                ok = kidobj
                     ? xml_processingInstructions(cx, kidobj, argc, argv, &v)
                     : JS_FALSE;
                JS_LeaveLocalRootScope(cx);
                if (!ok)
                    break;
                vxml = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
                if (JSXML_LENGTH(vxml) != 0) {
                    ok = Append(cx, list, vxml);
                    if (!ok)
                        break;
                }
            }
        }
    } else {
        /* 13.4.4.28 Step 4. */
        for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_PROCESSING_INSTRUCTION &&
                (IS_STAR(nameqn->localName) ||
                 !js_CompareStrings(nameqn->localName, kid->name->localName))) {
                ok = Append(cx, list, kid);
                if (!ok)
                    break;
            }
        }
    }

    return ok;
}

static JSBool
xml_prependChild(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                 jsval *rval)
{
    JSXML *xml;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(obj);
    return Insert(cx, xml, JSVAL_ZERO, argv[0]);
}

/* XML and XMLList */
static JSBool
xml_propertyIsEnumerable(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                         jsval *rval)
{
    JSXML *xml;
    jsval name;
    uint32 index;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    name = argv[0];
    *rval = JSVAL_FALSE;
    if (js_IdIsIndex(name, &index)) {
        if (xml->xml_class == JSXML_CLASS_LIST) {
            /* 13.5.4.18. */
            *rval = BOOLEAN_TO_JSVAL(index < xml->xml_kids.length);
        } else {
            /* 13.4.4.30. */
            *rval = BOOLEAN_TO_JSVAL(index == 0);
        }
    }
    return JS_TRUE;
}

static JSBool
namespace_full_match(const void *a, const void *b)
{
    const JSXMLNamespace *nsa = (const JSXMLNamespace *) a;
    const JSXMLNamespace *nsb = (const JSXMLNamespace *) b;

    if (nsa->prefix && nsb->prefix &&
        js_CompareStrings(nsa->prefix, nsb->prefix)) {
        return JS_FALSE;
    }
    return !js_CompareStrings(nsa->uri, nsb->uri);
}

static JSBool
xml_removeNamespace_helper(JSContext *cx, JSXML *xml, JSXMLNamespace *ns)
{
    JSXMLNamespace *thisns, *attrns, *ns2;
    uint32 i, n;
    JSXML *attr, *kid;

    thisns = GetNamespace(cx, xml->name, &xml->xml_namespaces);
    JS_ASSERT(thisns);
    if (thisns == ns)
        return JS_TRUE;

    for (i = 0, n = xml->xml_attrs.length; i < n; i++) {
        attr = XMLARRAY_MEMBER(&xml->xml_attrs, i, JSXML);
        attrns = GetNamespace(cx, attr->name, &xml->xml_namespaces);
        JS_ASSERT(attrns);
        if (attrns == ns)
            return JS_TRUE;
    }

    i = XMLARRAY_FIND_MEMBER(&xml->xml_namespaces, ns, namespace_full_match);
    if (i != XML_NOT_FOUND) {
        ns2 = XMLARRAY_DELETE(cx, &xml->xml_namespaces, i, JS_TRUE,
                              JSXMLNamespace);
        js_DestroyXMLNamespace(cx, ns2);
    }

    for (i = 0, n = xml->xml_kids.length; i < n; i++) {
        kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
        if (kid->xml_class == JSXML_CLASS_ELEMENT) {
            if (!xml_removeNamespace_helper(cx, kid, ns))
                return JS_FALSE;
        }
    }
    return JS_TRUE;
}

static JSBool
xml_removeNamespace(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                    jsval *rval)
{
    JSXML *xml;
    JSObject *nsobj;
    JSXMLNamespace *ns;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    *rval = OBJECT_TO_JSVAL(obj);
    if (xml->xml_class != JSXML_CLASS_ELEMENT)
        return JS_TRUE;
    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;

    nsobj = CallConstructorFunction(cx, obj, &js_NamespaceClass.base, 1, argv);
    if (!nsobj)
        return JS_FALSE;
    argv[0] = OBJECT_TO_JSVAL(nsobj);
    ns = (JSXMLNamespace *) JS_GetPrivate(cx, nsobj);

    /* NOTE: remove ns from each ancestor if not used by that ancestor. */
    return xml_removeNamespace_helper(cx, xml, ns);
}

static JSBool
xml_replace(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSXML *xml, *vxml, *kid;
    jsval name, value, id, junk;
    uint32 index;
    JSObject *nameobj;
    JSXMLQName *nameqn;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    *rval = OBJECT_TO_JSVAL(obj);
    if (xml->xml_class != JSXML_CLASS_ELEMENT)
        return JS_TRUE;

    value = argv[1];
    vxml = VALUE_IS_XML(cx, value)
           ? (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(value))
           : NULL;
    if (!vxml) {
        if (!JS_ConvertValue(cx, value, JSTYPE_STRING, &argv[1]))
            return JS_FALSE;
        value = argv[1];
    } else {
        vxml = DeepCopy(cx, vxml, NULL, 0);
        if (!vxml)
            return JS_FALSE;
        value = argv[1] = OBJECT_TO_JSVAL(vxml->object);
    }

    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;

    name = argv[0];
    if (js_IdIsIndex(name, &index))
        return Replace(cx, xml, name, value);

    /* Call function QName per spec, not ToXMLName, to avoid attribute names. */
    nameobj = CallConstructorFunction(cx, obj, &js_QNameClass.base, 1, &name);
    if (!nameobj)
        return JS_FALSE;
    argv[0] = OBJECT_TO_JSVAL(nameobj);
    nameqn = (JSXMLQName *) JS_GetPrivate(cx, nameobj);

    id = JSVAL_VOID;
    index = xml->xml_kids.length;
    while (index != 0) {
        --index;
        kid = XMLARRAY_MEMBER(&xml->xml_kids, index, JSXML);
        if (MatchElemName(nameqn, kid)) {
            if (!JSVAL_IS_VOID(id) && !DeleteByIndex(cx, xml, id, &junk))
                return JS_FALSE;
            if (!IndexToIdVal(cx, index, &id))
                return JS_FALSE;
        }
    }
    if (JSVAL_IS_VOID(id))
        return JS_TRUE;
    return Replace(cx, xml, id, value);
}

static JSBool
xml_setChildren(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                jsval *rval)
{
    if (!PutProperty(cx, obj, ATOM_KEY(cx->runtime->atomState.starAtom),
                     &argv[0])) {
        return JS_FALSE;
    }

    *rval = OBJECT_TO_JSVAL(obj);
    return JS_TRUE;
}

static JSBool
xml_setLocalName(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                 jsval *rval)
{
    JSXML *xml;
    jsval name;
    JSXMLQName *nameqn;
    JSString *namestr;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (!JSXML_HAS_NAME(xml))
        return JS_TRUE;

    name = argv[0];
    if (!JSVAL_IS_PRIMITIVE(name) &&
        OBJ_GET_CLASS(cx, JSVAL_TO_OBJECT(name)) == &js_QNameClass.base) {
        nameqn = (JSXMLQName *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(name));
        namestr = nameqn->localName;
    } else {
        if (!JS_ConvertValue(cx, name, JSTYPE_STRING, &argv[0]))
            return JS_FALSE;
        name = argv[0];
        namestr = JSVAL_TO_STRING(name);
    }

    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;
    xml->name->localName = namestr;
    return JS_TRUE;
}

static JSBool
xml_setName(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSXML *xml;
    jsval name;
    JSXMLQName *nameqn;
    JSObject *nameobj;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (!JSXML_HAS_NAME(xml))
        return JS_TRUE;

    name = argv[0];
    if (!JSVAL_IS_PRIMITIVE(name) &&
        OBJ_GET_CLASS(cx, JSVAL_TO_OBJECT(name)) == &js_QNameClass.base &&
        !(nameqn = (JSXMLQName *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(name)))
         ->uri) {
        name = argv[0] = STRING_TO_JSVAL(nameqn->localName);
    }

    nameobj = js_ConstructObject(cx, &js_QNameClass.base, NULL, NULL, 1, &name);
    if (!nameobj)
        return JS_FALSE;

    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml)
        return JS_FALSE;
    js_DestroyXMLQName(cx, xml->name);
    xml->name = (JSXMLQName *) JS_GetPrivate(cx, nameobj);
    return JS_TRUE;
}

static JSBool
xml_setNamespace(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                 jsval *rval)
{
    JSXML *xml;
    JSObject *nsobj, *qnobj;
    jsval qnargv[2];

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (!JSXML_HAS_NAME(xml))
        return JS_TRUE;

    xml = CHECK_COPY_ON_WRITE(cx, xml, obj);
    if (!xml || !js_GetXMLQNameObject(cx, xml->name))
        return JS_FALSE;

    nsobj = js_ConstructObject(cx, &js_NamespaceClass.base, NULL, obj, 1, argv);
    if (!nsobj)
        return JS_FALSE;

    qnargv[0] = argv[0] = OBJECT_TO_JSVAL(nsobj);
    qnargv[1] = OBJECT_TO_JSVAL(xml->name->object);
    qnobj = js_ConstructObject(cx, &js_QNameClass.base, NULL, NULL, 2, qnargv);
    if (!qnobj)
        return JS_FALSE;

    xml->name = (JSXMLQName *) JS_GetPrivate(cx, qnobj);
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_text(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSXML *xml, *list, *kid, *vxml;
    JSObject *listobj, *kidobj;
    uint32 i, n;
    JSBool ok;
    jsval v;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
    if (!listobj)
        return JS_FALSE;

    *rval = OBJECT_TO_JSVAL(listobj);
    list = (JSXML *) JS_GetPrivate(cx, listobj);
    list->xml_target = xml;

    if (xml->xml_class == JSXML_CLASS_LIST) {
        ok = JS_TRUE;
        for (i = 0, n = xml->xml_kids.length; i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_ELEMENT) {
                ok = JS_EnterLocalRootScope(cx);
                if (!ok)
                    break;
                kidobj = js_GetXMLObject(cx, kid);
                ok = kidobj
                     ? xml_text(cx, kidobj, argc, argv, &v)
                     : JS_FALSE;
                JS_LeaveLocalRootScope(cx);
                if (!ok)
                    return JS_FALSE;
                vxml = (JSXML *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(v));
                if (JSXML_LENGTH(vxml) != 0 && !Append(cx, list, vxml))
                    return JS_FALSE;
            }
        }
    } else {
        for (i = 0, n = JSXML_LENGTH(xml); i < n; i++) {
            kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
            if (kid->xml_class == JSXML_CLASS_TEXT && !Append(cx, list, kid))
                return JS_FALSE;
        }
    }
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_toXMLString(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                jsval *rval)
{
    JSString *str;

    str = ToXMLString(cx, OBJECT_TO_JSVAL(obj));
    if (!str)
        return JS_FALSE;
    *rval = STRING_TO_JSVAL(str);
    return JS_TRUE;
}

/* XML and XMLList */
static JSString *
xml_toString_helper(JSContext *cx, JSXML *xml)
{
    JSString *str, *kidstr;
    JSXML *kid;
    uint32 i, n;

    if (xml->xml_class == JSXML_CLASS_ATTRIBUTE ||
        xml->xml_class == JSXML_CLASS_TEXT) {
        return xml->xml_value;
    }

    if (!HasSimpleContent(xml))
        return ToXMLString(cx, OBJECT_TO_JSVAL(xml->object));

    str = cx->runtime->emptyString;
    JS_EnterLocalRootScope(cx);
    for (i = 0, n = xml->xml_kids.length; i < n; i++) {
        kid = XMLARRAY_MEMBER(&xml->xml_kids, i, JSXML);
        if (kid->xml_class != JSXML_CLASS_COMMENT &&
            kid->xml_class != JSXML_CLASS_PROCESSING_INSTRUCTION) {
            kidstr = xml_toString_helper(cx, kid);
            if (!kidstr) {
                str = NULL;
                break;
            }
            str = js_ConcatStrings(cx, str, kidstr);
            if (!str)
                break;
        }
    }
    JS_LeaveLocalRootScope(cx);
    return str;
}

static JSBool
xml_toString(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
             jsval *rval)
{
    JSXML *xml;
    JSString *str;

    xml = (JSXML *) JS_GetPrivate(cx, obj);
    str = xml_toString_helper(cx, xml);
    if (!str)
        return JS_FALSE;
    *rval = STRING_TO_JSVAL(str);
    return JS_TRUE;
}

/* XML and XMLList */
static JSBool
xml_valueOf(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    *rval = OBJECT_TO_JSVAL(obj);
    return JS_TRUE;
}

static JSFunctionSpec xml_methods[] = {
    {"addNamespace",          xml_addNamespace,          1,0,XML_MASK},
    {"appendChild",           xml_appendChild,           1,0,XML_MASK},
    {js_attribute_str,        xml_attribute,             1,0,GENERIC_MASK},
    {"attributes",            xml_attributes,            0,0,GENERIC_MASK},
    {"child",                 xml_child,                 1,0,GENERIC_MASK},
    {"childIndex",            xml_childIndex,            0,0,XML_MASK},
    {"children",              xml_children,              0,0,GENERIC_MASK},
    {"comments",              xml_comments,              0,0,GENERIC_MASK},
    {"contains",              xml_contains,              1,0,GENERIC_MASK},
    {"copy",                  xml_copy,                  0,0,GENERIC_MASK},
    {"descendants",           xml_descendants,           1,0,GENERIC_MASK},
    {"elements",              xml_elements,              1,0,GENERIC_MASK},
    {"hasOwnProperty",        xml_hasOwnProperty,        1,0,GENERIC_MASK},
    {"hasComplexContent",     xml_hasComplexContent,     1,0,GENERIC_MASK},
    {"hasSimpleContent",      xml_hasSimpleContent,      1,0,GENERIC_MASK},
    {"inScopeNamespaces",     xml_inScopeNamespaces,     0,0,XML_MASK},
    {"insertChildAfter",      xml_insertChildAfter,      2,0,XML_MASK},
    {"insertChildBefore",     xml_insertChildBefore,     2,0,XML_MASK},
    {js_length_str,           xml_length,                0,0,GENERIC_MASK},
    {js_localName_str,        xml_localName,             0,0,XML_MASK},
    {"name",                  xml_name,                  0,0,XML_MASK},
    {js_namespace_str,        xml_namespace,             1,0,XML_MASK},
    {"namespaceDeclarations", xml_namespaceDeclarations, 0,0,XML_MASK},
    {"nodeKind",              xml_nodeKind,              0,0,XML_MASK},
    {"normalize",             xml_normalize,             0,0,GENERIC_MASK},
    {"parent",                xml_parent,                0,0,GENERIC_MASK},
    {"processingInstructions",xml_processingInstructions,1,0,GENERIC_MASK},
    {"prependChild",          xml_prependChild,          1,0,XML_MASK},
    {"propertyIsEnumerable",  xml_propertyIsEnumerable,  1,0,GENERIC_MASK},
    {"removeNamespace",       xml_removeNamespace,       1,0,XML_MASK},
    {"replace",               xml_replace,               2,0,XML_MASK},
    {"setChildren",           xml_setChildren,           1,0,XML_MASK},
    {"setLocalName",          xml_setLocalName,          1,0,XML_MASK},
    {"setName",               xml_setName,               1,0,XML_MASK},
    {"setNamespace",          xml_setNamespace,          1,0,XML_MASK},
    {js_text_str,             xml_text,                  0,0,GENERIC_MASK},
    {js_toString_str,         xml_toString,              0,0,GENERIC_MASK},
    {js_toXMLString_str,      xml_toXMLString,           0,0,GENERIC_MASK},
    {js_valueOf_str,          xml_valueOf,               0,0,GENERIC_MASK},
    {0,0,0,0,0}
};

static JSBool
CopyXMLSettings(JSContext *cx, JSObject *from, JSObject *to)
{
    int i;
    const char *name;
    jsval v;

    for (i = XML_IGNORE_COMMENTS; i < XML_PRETTY_INDENT; i++) {
        name = xml_static_props[i].name;
        if (!JS_GetProperty(cx, from, name, &v))
            return JS_FALSE;
        if (JSVAL_IS_BOOLEAN(v) && !JS_SetProperty(cx, to, name, &v))
            return JS_FALSE;
    }

    name = xml_static_props[i].name;
    if (!JS_GetProperty(cx, from, name, &v))
        return JS_FALSE;
    if (JSVAL_IS_NUMBER(v) && !JS_SetProperty(cx, to, name, &v))
        return JS_FALSE;
    return JS_TRUE;
}

static JSBool
SetDefaultXMLSettings(JSContext *cx, JSObject *obj)
{
    int i;
    jsval v;

    for (i = XML_IGNORE_COMMENTS; i < XML_PRETTY_INDENT; i++) {
        v = JSVAL_TRUE;
        if (!JS_SetProperty(cx, obj, xml_static_props[i].name, &v))
            return JS_FALSE;
    }
    v = INT_TO_JSVAL(2);
    return JS_SetProperty(cx, obj, xml_static_props[i].name, &v);
}

static JSBool
xml_settings(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    JSObject *settings;

    settings = JS_NewObject(cx, NULL, NULL, NULL);
    if (!settings)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(settings);
    return CopyXMLSettings(cx, obj, settings);
}

static JSBool
xml_setSettings(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                jsval *rval)
{
    jsval v;
    JSBool ok;
    JSObject *settings;

    v = argv[0];
    if (JSVAL_IS_NULL(v) || JSVAL_IS_VOID(v)) {
        cx->xmlSettingFlags = 0;
        ok = SetDefaultXMLSettings(cx, obj);
    } else {
        if (JSVAL_IS_PRIMITIVE(v))
            return JS_TRUE;
        settings = JSVAL_TO_OBJECT(v);
        cx->xmlSettingFlags = 0;
        ok = CopyXMLSettings(cx, settings, obj);
    }
    if (ok)
        cx->xmlSettingFlags |= XSF_CACHE_VALID;
    return ok;
}

static JSBool
xml_defaultSettings(JSContext *cx, JSObject *obj, uintN argc, jsval *argv,
                    jsval *rval)
{
    JSObject *settings;

    settings = JS_NewObject(cx, NULL, NULL, NULL);
    if (!settings)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(settings);
    return SetDefaultXMLSettings(cx, settings);
}

static JSFunctionSpec xml_static_methods[] = {
    {"settings",         xml_settings,          0,0,0},
    {"setSettings",      xml_setSettings,       1,0,0},
    {"defaultSettings",  xml_defaultSettings,   0,0,0},
    {0,0,0,0,0}
};

static JSBool
XML(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    jsval v;
    JSXML *xml, *copy;
    JSObject *xobj, *vobj;
    JSClass *clasp;

    v = argv[0];
    if (JSVAL_IS_NULL(v) || JSVAL_IS_VOID(v))
        v = STRING_TO_JSVAL(cx->runtime->emptyString);

    xobj = ToXML(cx, v);
    if (!xobj)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(xobj);
    xml = (JSXML *) JS_GetPrivate(cx, xobj);

    if ((cx->fp->flags & JSFRAME_CONSTRUCTING) && !JSVAL_IS_PRIMITIVE(v)) {
        vobj = JSVAL_TO_OBJECT(v);
        clasp = OBJ_GET_CLASS(cx, vobj);
        if (clasp == &js_XMLClass ||
            (clasp->flags & JSCLASS_DOCUMENT_OBSERVER)) {
            /* No need to lock obj, it's newly constructed and thread local. */
            copy = DeepCopy(cx, xml, obj, 0);
            if (!copy)
                return JS_FALSE;
            JS_ASSERT(copy->object == obj);
            JS_ASSERT(copy->markflag == JSXML_MARK_CLEAR);
            *rval = OBJECT_TO_JSVAL(obj);
            return JS_TRUE;
        }
    }
    return JS_TRUE;
}

static JSBool
XMLList(JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval)
{
    jsval v;
    JSObject *vobj, *listobj;
    JSXML *xml, *list;

    v = argv[0];
    if (JSVAL_IS_NULL(v) || JSVAL_IS_VOID(v))
        v = STRING_TO_JSVAL(cx->runtime->emptyString);

    if ((cx->fp->flags & JSFRAME_CONSTRUCTING) && !JSVAL_IS_PRIMITIVE(v)) {
        vobj = JSVAL_TO_OBJECT(v);
        if (OBJECT_IS_XML(cx, vobj)) {
            xml = (JSXML *) JS_GetPrivate(cx, vobj);
            if (xml->xml_class == JSXML_CLASS_LIST) {
                listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
                if (!listobj)
                    return JS_FALSE;
                *rval = OBJECT_TO_JSVAL(listobj);

                list = (JSXML *) JS_GetPrivate(cx, listobj);
                if (!Append(cx, list, xml))
                    return JS_FALSE;
                return JS_TRUE;
            }
        }
    }

    listobj = ToXMLList(cx, v);
    if (!listobj)
        return JS_FALSE;
    *rval = OBJECT_TO_JSVAL(listobj);
    return JS_TRUE;
}

#define JSXML_LIST_SIZE     (offsetof(JSXML, u) + sizeof(struct JSXMLListVar))
#define JSXML_ELEMENT_SIZE  (offsetof(JSXML, u) + sizeof(struct JSXMLVar))
#define JSXML_LEAF_SIZE     (offsetof(JSXML, u) + sizeof(JSString *))

static size_t sizeof_JSXML[JSXML_CLASS_LIMIT] = {
    JSXML_LIST_SIZE,        /* JSXML_CLASS_LIST */
    JSXML_ELEMENT_SIZE,     /* JSXML_CLASS_ELEMENT */
    JSXML_LEAF_SIZE,        /* JSXML_CLASS_ATTRIBUTE */
    JSXML_LEAF_SIZE,        /* JSXML_CLASS_PROCESSING_INSTRUCTION */
    JSXML_LEAF_SIZE,        /* JSXML_CLASS_TEXT */
    JSXML_LEAF_SIZE         /* JSXML_CLASS_COMMENT */
};

#ifdef DEBUG_notme
JSCList xml_leaks = JS_INIT_STATIC_CLIST(&xml_leaks);
uint32  xml_serial;
#endif

JSXML *
js_NewXML(JSContext *cx, JSXMLClass xml_class)
{
    JSXML *xml;

    xml = (JSXML *) JS_malloc(cx, sizeof_JSXML[xml_class]);
    if (!xml)
        return NULL;

    xml->object = NULL;
    xml->domnode = NULL;
    xml->parent = NULL;
    xml->name = NULL;
    xml->markflag = JSXML_MARK_SINGLE_OWNER;
    xml->xml_class = xml_class;
    xml->xml_flags = 0;
    if (JSXML_CLASS_HAS_VALUE(xml_class)) {
        xml->xml_value = cx->runtime->emptyString;
    } else {
        XMLARRAY_INIT(cx, &xml->xml_kids, 0);
        if (xml_class == JSXML_CLASS_LIST) {
            xml->xml_target = NULL;
            xml->xml_targetprop = NULL;
        } else {
            XMLARRAY_INIT(cx, &xml->xml_namespaces, 0);
            XMLARRAY_INIT(cx, &xml->xml_attrs, 0);
        }
    }

#ifdef DEBUG_notme
    JS_APPEND_LINK(&xml->links, &xml_leaks);
    xml->serial = xml_serial++;
#endif
    METER(xml_stats.xml);
    METER(xml_stats.livexml);
    return xml;
}

void
js_DestroyXML(JSContext *cx, JSXML *xml)
{
    JSXMLArrayElemDtor xmldtor, nsdtor;

    if (xml->markflag > JSXML_MARK_SINGLE_OWNER)
        return;

    if (xml->name && xml->markflag != JSXML_MARK_DOOMED)
        js_DestroyXMLQName(cx, xml->name);

    if (JSXML_HAS_KIDS(xml)) {
        if (xml->markflag == JSXML_MARK_DOOMED) {
            xmldtor = nsdtor = NULL;
        } else {
            xmldtor = (JSXMLArrayElemDtor) js_DestroyXML;
            nsdtor = (JSXMLArrayElemDtor) js_DestroyXMLNamespace;
        }
        XMLARRAY_FINISH(cx, &xml->xml_kids, xmldtor);
        if (xml->xml_class == JSXML_CLASS_ELEMENT) {
            XMLARRAY_FINISH(cx, &xml->xml_namespaces, nsdtor);
            XMLARRAY_FINISH(cx, &xml->xml_attrs, xmldtor);
        }
    }

#ifdef DEBUG_notme
    JS_REMOVE_LINK(&xml->links);
#endif

    JS_free(cx, xml);
    UNMETER(xml_stats.livexml);
}

void
js_FinalizeDoomedXML(JSContext *cx)
{
    JSRuntime *rt;
    JSXMLNamespace *ns, *nextns;
    JSXMLQName *qn, *nextqn;
    JSXML *xml, *nextxml;

    rt = cx->runtime;

    for (ns = rt->gcDoomedNamespaces; ns; ns = nextns) {
        JS_ASSERT(ns->markflag == JSXML_MARK_DOOMED);
        nextns = (JSXMLNamespace *) ns->object;
        ns->object = NULL;
        js_DestroyXMLNamespace(cx, ns);
    }
    rt->gcDoomedNamespaces = NULL;

    for (qn = rt->gcDoomedQNames; qn; qn = nextqn) {
        JS_ASSERT(qn->markflag == JSXML_MARK_DOOMED);
        nextqn = (JSXMLQName *) qn->object;
        qn->object = NULL;
        js_DestroyXMLQName(cx, qn);
    }
    rt->gcDoomedQNames = NULL;

    for (xml = rt->gcDoomedXML; xml; xml = nextxml) {
        JS_ASSERT(xml->markflag == JSXML_MARK_DOOMED);
        nextxml = (JSXML *) xml->object;
        xml->object = NULL;
        js_DestroyXML(cx, xml);
    }
    rt->gcDoomedXML = NULL;
}

JSObject *
js_ParseNodeToXMLObject(JSContext *cx, JSParseNode *pn)
{
    jsval nsval;
    JSXMLNamespace *ns;
    JSXMLArray nsarray;
    JSXML *xml;

    if (!js_GetDefaultXMLNamespace(cx, &nsval))
        return NULL;
    JS_ASSERT(!JSVAL_IS_PRIMITIVE(nsval));
    ns = (JSXMLNamespace *) JS_GetPrivate(cx, JSVAL_TO_OBJECT(nsval));

    if (!XMLARRAY_INIT(cx, &nsarray, 1))
        return NULL;

    XMLARRAY_APPEND(cx, &nsarray, ns);
    xml = ParseNodeToXML(cx, pn, &nsarray, XSF_PRECOMPILED_ROOT);
    XMLARRAY_FINISH(cx, &nsarray, NULL);
    if (!xml)
        return NULL;

    return xml->object;
}

JSObject *
js_NewXMLObject(JSContext *cx, JSXMLClass xml_class)
{
    JSXML *xml;
    JSObject *obj;

    xml = js_NewXML(cx, xml_class);
    if (!xml)
        return NULL;
    obj = js_GetXMLObject(cx, xml);
    if (!obj)
        js_DestroyXML(cx, xml);
    return obj;
}

static JSObject *
NewXMLObject(JSContext *cx, JSXML *xml)
{
    JSObject *obj;

    obj = js_NewObject(cx, &js_XMLClass, NULL, NULL);
    if (!obj || !JS_SetPrivate(cx, obj, xml)) {
        cx->newborn[GCX_OBJECT] = NULL;
        return NULL;
    }
    METER(xml_stats.xmlobj);
    METER(xml_stats.livexmlobj);
    return obj;
}

JSObject *
js_GetXMLObject(JSContext *cx, JSXML *xml)
{
    JSObject *obj;

    obj = xml->object;
    if (obj) {
        JS_ASSERT(JS_GetPrivate(cx, obj) == xml);
        return obj;
    }

    /*
     * A JSXML cannot be shared among threads unless it has an object.
     * A JSXML cannot be given an object unless:
     * (a) it has no parent; or
     * (b) its parent has no object (therefore is thread-private); or
     * (c) its parent's object is locked.
     *
     * Once given an object, a JSXML is immutable.
     */
    JS_ASSERT(!xml->parent ||
              !xml->parent->object ||
              JS_IS_OBJ_LOCKED(cx, xml->parent->object));

    obj = NewXMLObject(cx, xml);
    if (!obj)
        return NULL;
    xml->object = obj;
    xml->markflag = JSXML_MARK_CLEAR;
    return obj;
}

JSObject *
js_InitNamespaceClass(JSContext *cx, JSObject *obj)
{
    return JS_InitClass(cx, obj, NULL, &js_NamespaceClass.base, Namespace, 2,
                        namespace_props, namespace_methods, NULL, NULL);
}

JSObject *
js_InitQNameClass(JSContext *cx, JSObject *obj)
{
    if (!JS_InitClass(cx, obj, NULL, &js_AttributeNameClass, AttributeName, 2,
                      qname_props, qname_methods, NULL, NULL)) {
        return NULL;
    }

    if (!JS_InitClass(cx, obj, NULL, &js_AnyNameClass, AnyName, 0,
                      qname_props, qname_methods, NULL, NULL)) {
        return NULL;
    }

    return JS_InitClass(cx, obj, NULL, &js_QNameClass.base, QName, 2,
                        qname_props, qname_methods, NULL, NULL);
}

JSObject *
js_InitXMLClass(JSContext *cx, JSObject *obj)
{
    JSObject *proto, *pobj, *ctor;
    JSFunctionSpec *fs;
    JSFunction *fun;
    JSXML *xml;
    JSProperty *prop;
    JSScopeProperty *sprop;
    jsval cval, argv[1], junk;

    /* Define the isXMLName function. */
    if (!JS_DefineFunction(cx, obj, js_isXMLName_str, xml_isXMLName, 1, 0))
        return NULL;

    /* Define the XML class constructor and prototype. */
    proto = JS_InitClass(cx, obj, NULL, &js_XMLClass, XML, 1,
                         NULL, NULL,
                         xml_static_props, xml_static_methods);
    if (!proto)
        return NULL;

    /*
     * XXX Hack alert: expand JS_DefineFunctions here to copy fs->extra into
     * fun->spare, clearing fun->extra.  No xml_methods require extra local GC
     * roots allocated after actual arguments on the VM stack, but we need a
     * way to tell which methods work only on XML objects, which work only on
     * XMLList objects, and which work on either.
     */
    for (fs = xml_methods; fs->name; fs++) {
        fun = JS_DefineFunction(cx, proto, fs->name, fs->call, fs->nargs,
                                fs->flags);
        if (!fun)
            return NULL;
        fun->extra = 0;
        fun->spare = fs->extra;
    }

    xml = js_NewXML(cx, JSXML_CLASS_TEXT);
    if (!xml || !JS_SetPrivate(cx, proto, xml))
        return NULL;
    xml->object = proto;
    xml->markflag = JSXML_MARK_CLEAR;
    METER(xml_stats.xmlobj);
    METER(xml_stats.livexmlobj);

    /*
     * Prepare to set default settings on the XML constructor we just made.
     * NB: We can't use JS_GetConstructor, because it calls OBJ_GET_PROPERTY,
     * which is xml_getProperty, which creates a new XMLList every time!  We
     * must instead call js_LookupProperty directly.
     */
    if (!js_LookupProperty(cx, proto,
                           ATOM_TO_JSID(cx->runtime->atomState.constructorAtom),
                           &pobj, &prop)) {
        return NULL;
    }
    JS_ASSERT(prop);
    sprop = (JSScopeProperty *) prop;
    JS_ASSERT(SPROP_HAS_VALID_SLOT(sprop, OBJ_SCOPE(pobj)));
    cval = OBJ_GET_SLOT(cx, pobj, sprop->slot);
    OBJ_DROP_PROPERTY(cx, pobj, prop);
    JS_ASSERT(JSVAL_IS_FUNCTION(cx, cval));

    /* Set default settings. */
    ctor = JSVAL_TO_OBJECT(cval);
    argv[0] = JSVAL_VOID;
    if (!xml_setSettings(cx, ctor, 1, argv, &junk))
        return NULL;

    /* Define the XMLList function and give it the same prototype as XML. */
    fun = JS_DefineFunction(cx, obj, js_XMLList_str, XMLList, 1, 0);
    if (!fun)
        return NULL;
    if (!js_SetClassPrototype(cx, fun->object, proto,
                              JSPROP_READONLY | JSPROP_PERMANENT)) {
        return NULL;
    }
    return proto;
}

JSObject *
js_InitXMLClasses(JSContext *cx, JSObject *obj)
{
    if (!js_InitNamespaceClass(cx, obj) || !js_InitQNameClass(cx, obj))
        return NULL;
    return js_InitXMLClass(cx, obj);
}

JSBool
js_GetFunctionNamespace(JSContext *cx, jsval *vp)
{
    JSRuntime *rt;
    JSAtom *atom;
    JSString *prefix, *uri;
    JSObject *obj;

    /* An invalid URI, for internal use only, guaranteed not to collide. */
    static const char anti_uri[] = "@mozilla.org/js/function";

    rt = cx->runtime;
    atom = rt->atomState.lazy.functionNamespaceAtom;
    if (!atom) {
        atom = js_Atomize(cx, js_function_str, 8, 0);
        JS_ASSERT(atom);
        prefix = ATOM_TO_STRING(atom);

        atom = js_Atomize(cx, anti_uri, sizeof anti_uri - 1, ATOM_PINNED);
        if (!atom)
            return JS_FALSE;
        rt->atomState.lazy.functionNamespaceURIAtom = atom;

        uri = ATOM_TO_STRING(atom);
        obj = js_NewXMLNamespaceObject(cx, prefix, uri, JS_FALSE);
        if (!obj)
            return JS_FALSE;

        atom = js_AtomizeObject(cx, obj, ATOM_PINNED);
        if (!atom)
            return JS_FALSE;
        rt->atomState.lazy.functionNamespaceAtom = atom;
    }
    *vp = ATOM_KEY(atom);
    return JS_TRUE;
}

/*
 * Note the asymmetry between js_GetDefaultXMLNamespace and js_SetDefaultXML-
 * Namespace.  Get searches fp->scopeChain for JS_DEFAULT_XML_NAMESPACE_ID,
 * while Set sets JS_DEFAULT_XML_NAMESPACE_ID in fp->varobj (unless fp is a
 * lightweight function activation).  There's no requirement that fp->varobj
 * lie directly on fp->scopeChain, although it should be reachable using the
 * prototype chain from a scope object (cf. JSOPTION_VAROBJFIX in jsapi.h).
 *
 * If Get can't find JS_DEFAULT_XML_NAMESPACE_ID along the scope chain, it
 * creates a default namespace via 'new Namespace()'.  In contrast, Set uses
 * its v argument as the uri of a new Namespace, with "" as the prefix.  See
 * ECMA-357 12.1 and 12.1.1.  Note that if Set is called with a Namespace n,
 * the default XML namespace will be set to ("", n.uri).  So the uri string
 * is really the only usefully stored value of the default namespace.
 */
JSBool
js_GetDefaultXMLNamespace(JSContext *cx, jsval *vp)
{
    JSStackFrame *fp;
    JSObject *nsobj, *obj, *tmp;
    jsval v;

    fp = cx->fp;
    nsobj = fp->xmlNamespace;
    if (nsobj) {
        *vp = OBJECT_TO_JSVAL(nsobj);
        return JS_TRUE;
    }

    obj = NULL;
    for (tmp = fp->scopeChain; tmp; tmp = OBJ_GET_PARENT(cx, obj)) {
        obj = tmp;
        if (!OBJ_GET_PROPERTY(cx, obj, JS_DEFAULT_XML_NAMESPACE_ID, &v))
            return JS_FALSE;
        if (!JSVAL_IS_PRIMITIVE(v)) {
            fp->xmlNamespace = JSVAL_TO_OBJECT(v);
            *vp = v;
            return JS_TRUE;
        }
    }

    nsobj = js_ConstructObject(cx, &js_NamespaceClass.base, NULL, obj, 0, NULL);
    if (!nsobj)
        return JS_FALSE;
    v = OBJECT_TO_JSVAL(nsobj);
    if (obj && !OBJ_SET_PROPERTY(cx, obj, JS_DEFAULT_XML_NAMESPACE_ID, &v))
        return JS_FALSE;
    fp->xmlNamespace = nsobj;
    *vp = v;
    return JS_TRUE;
}

JSBool
js_SetDefaultXMLNamespace(JSContext *cx, jsval v)
{
    jsval argv[2];
    JSObject *nsobj, *varobj;
    JSStackFrame *fp;

    argv[0] = STRING_TO_JSVAL(cx->runtime->emptyString);
    argv[1] = v;
    nsobj = js_ConstructObject(cx, &js_NamespaceClass.base, NULL, NULL,
                               2, argv);
    if (!nsobj)
        return JS_FALSE;
    v = OBJECT_TO_JSVAL(nsobj);

    fp = cx->fp;
    varobj = fp->varobj;
    if (varobj) {
        if (!OBJ_SET_PROPERTY(cx, varobj, JS_DEFAULT_XML_NAMESPACE_ID, &v))
            return JS_FALSE;
    } else {
        JS_ASSERT(fp->fun && !(fp->fun->flags & JSFUN_HEAVYWEIGHT));
    }
    fp->xmlNamespace = JSVAL_TO_OBJECT(v);
    return JS_TRUE;
}

JSBool
js_ToAttributeName(JSContext *cx, jsval *vp)
{
    JSXMLQName *qn;

    qn = ToAttributeName(cx, *vp);
    if (!qn)
        return JS_FALSE;
    *vp = OBJECT_TO_JSVAL(qn->object);
    return JS_TRUE;
}

JSString *
js_EscapeAttributeValue(JSContext *cx, JSString *str)
{
    return EscapeAttributeValue(cx, NULL, str);
}

JSString *
js_AddAttributePart(JSContext *cx, JSBool isName, JSString *str, JSString *str2)
{
    size_t len, len2, newlen;
    jschar *chars;

    if (JSSTRING_IS_DEPENDENT(str) ||
        !(*js_GetGCThingFlags(str) & GCF_MUTABLE)) {
        str = js_NewStringCopyN(cx, JSSTRING_CHARS(str), JSSTRING_LENGTH(str),
                                0);
        if (!str)
            return NULL;
    }

    len = str->length;
    len2 = JSSTRING_LENGTH(str2);
    newlen = (isName) ? len + 1 + len2 : len + 2 + len2 + 1;
    chars = (jschar *) JS_realloc(cx, str->chars, (newlen+1) * sizeof(jschar));
    if (!chars)
        return NULL;

    /*
     * Reallocating str (because we know it has no other references) requires
     * purging any deflated string cached for it.
     */
    js_PurgeDeflatedStringCache(str);

    str->chars = chars;
    str->length = newlen;
    chars += len;
    if (isName) {
        *chars++ = ' ';
        js_strncpy(chars, JSSTRING_CHARS(str2), len2);
        chars += len2;
    } else {
        *chars++ = '=';
        *chars++ = '"';
        js_strncpy(chars, JSSTRING_CHARS(str2), len2);
        chars += len2;
        *chars++ = '"';
    }
    *chars = 0;
    return str;
}

JSString *
js_EscapeElementValue(JSContext *cx, JSString *str)
{
    return EscapeElementValue(cx, NULL, str);
}

JSString *
js_ValueToXMLString(JSContext *cx, jsval v)
{
    return ToXMLString(cx, v);
}

JSBool
js_GetAnyName(JSContext *cx, jsval *vp)
{
    JSRuntime *rt;
    JSAtom *atom;
    JSXMLQName *qn;
    JSObject *obj;

    rt = cx->runtime;
    atom = rt->atomState.lazy.anynameAtom;
    if (!atom) {
        qn = js_NewXMLQName(cx, rt->emptyString, rt->emptyString,
                            ATOM_TO_STRING(rt->atomState.starAtom));
        if (!qn)
            return JS_FALSE;

        obj = js_NewObject(cx, &js_AnyNameClass, NULL, NULL);
        if (!obj || !JS_SetPrivate(cx, obj, qn)) {
            cx->newborn[GCX_OBJECT] = NULL;
            return JS_FALSE;
        }
        qn->object = obj;
        qn->markflag = JSXML_MARK_CLEAR;
        METER(xml_stats.qnameobj);
        METER(xml_stats.liveqnameobj);

        atom = js_AtomizeObject(cx, obj, ATOM_PINNED);
        if (!atom)
            return JS_FALSE;
        rt->atomState.lazy.anynameAtom = atom;
    }
    *vp = ATOM_KEY(atom);
    return JS_TRUE;
}

JSBool
js_FindXMLProperty(JSContext *cx, jsval name, JSObject **objp, jsval *namep)
{
    JSXMLQName *qn;
    jsid funid, id;
    JSObject *obj, *pobj, *lastobj;
    JSProperty *prop;

    qn = ToXMLName(cx, name, &funid);
    if (!qn)
        return JS_FALSE;
    id = OBJECT_TO_JSID(qn->object);

    obj = cx->fp->scopeChain;
    do {
        if (!OBJ_LOOKUP_PROPERTY(cx, obj, id, &pobj, &prop))
            return JS_FALSE;
        if (prop) {
            OBJ_DROP_PROPERTY(cx, pobj, prop);

            if (OBJECT_IS_XML(cx, pobj)) {
                *objp = pobj;
                *namep = ID_TO_VALUE(id);
                return JS_TRUE;
            }
        }

        lastobj = obj;
    } while ((obj = OBJ_GET_PARENT(cx, obj)) != NULL);

    if (JS_HAS_STRICT_OPTION(cx)) {
        JSString *str = js_ValueToString(cx, name);
        if (!str ||
            !JS_ReportErrorFlagsAndNumber(cx,
                                          JSREPORT_WARNING|JSREPORT_STRICT,
                                          js_GetErrorMessage, NULL,
                                          JSMSG_UNDEFINED_XML_NAME,
                                          JS_GetStringBytes(str))) {
            return JS_FALSE;
        }
    }

    *objp = lastobj;
    *namep = JSVAL_VOID;
    return JS_TRUE;
}

JSBool
js_GetXMLProperty(JSContext *cx, JSObject *obj, jsval name, jsval *vp)
{
    return GetProperty(cx, obj, name, vp);
}

JSBool
js_SetXMLProperty(JSContext *cx, JSObject *obj, jsval name, jsval *vp)
{
    return PutProperty(cx, obj, name, vp);
}

static JSXML *
GetPrivate(JSContext *cx, JSObject *obj, const char *method)
{
    JSXML *xml;

    xml = (JSXML *) JS_GetInstancePrivate(cx, obj, &js_XMLClass, NULL);
    if (!xml) {
        JS_ReportErrorNumber(cx, js_GetErrorMessage, NULL,
                             JSMSG_INCOMPATIBLE_METHOD,
                             js_XML_str, method, OBJ_GET_CLASS(cx, obj)->name);
    }
    return xml;
}

JSBool
js_GetXMLDescendants(JSContext *cx, JSObject *obj, jsval id, jsval *vp)
{
    JSXML *xml, *list;

    xml = GetPrivate(cx, obj, "descendants internal method");
    if (!xml)
        return JS_FALSE;

    list = Descendants(cx, xml, id);
    if (!list)
        return JS_FALSE;
    *vp = OBJECT_TO_JSVAL(list->object);
    return JS_TRUE;
}

JSBool
js_DeleteXMLListElements(JSContext *cx, JSObject *listobj)
{
    JSXML *list;
    uint32 n;
    jsval junk;

    list = (JSXML *) JS_GetPrivate(cx, listobj);
    for (n = list->xml_kids.length; n != 0; --n) {
        if (!DeleteProperty(cx, listobj, INT_TO_JSID(0), &junk))
            return JS_FALSE;
    }
    return JS_TRUE;
}

JSBool
js_FilterXMLList(JSContext *cx, JSObject *obj, jsbytecode *pc, jsval *vp)
{
    JSBool ok, match;
    JSStackFrame *fp;
    JSObject *scobj, *listobj, *resobj, *withobj, *kidobj;
    JSXML *xml, *list, *result, *kid;
    uint32 i, n;

    ok = JS_EnterLocalRootScope(cx);
    if (!ok)
        return JS_FALSE;

    /* All control flow after this point must exit via label out or bad. */
    fp = cx->fp;
    scobj = fp->scopeChain;
    xml = GetPrivate(cx, obj, "filtering predicate operator");
    if (!xml)
        goto bad;

    if (xml->xml_class == JSXML_CLASS_LIST) {
        list = xml;
    } else {
        listobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
        if (!listobj)
            goto bad;
        list = (JSXML *) JS_GetPrivate(cx, listobj);
        ok = Append(cx, list, xml);
        if (!ok)
            goto out;
    }

    resobj = js_NewXMLObject(cx, JSXML_CLASS_LIST);
    if (!resobj)
        goto bad;
    result = (JSXML *) JS_GetPrivate(cx, resobj);

    /* Hoist the scope chain update out of the loop over kids. */
    withobj = js_NewObject(cx, &js_WithClass, NULL, scobj);
    if (!withobj)
        goto bad;
    fp->scopeChain = withobj;

    for (i = 0, n = list->xml_kids.length; i < n; i++) {
        kid = XMLARRAY_MEMBER(&list->xml_kids, i, JSXML);
        kidobj = js_GetXMLObject(cx, kid);
        if (!kidobj)
            goto bad;
        OBJ_SET_PROTO(cx, withobj, kidobj);
        ok = js_Interpret(cx, pc, vp);
        if (!ok)
            goto out;
        ok = js_ValueToBoolean(cx, *vp, &match);
        if (!ok)
            goto out;
        if (match) {
            ok = Append(cx, result, kid);
            if (!ok)
                goto out;
        }
    }

    *vp = OBJECT_TO_JSVAL(resobj);

out:
    fp->scopeChain = scobj;
    JS_LeaveLocalRootScope(cx);
    return ok;
bad:
    ok = JS_FALSE;
    goto out;
}

JSObject *
js_ValueToXMLObject(JSContext *cx, jsval v)
{
    return ToXML(cx, v);
}

JSObject *
js_ValueToXMLListObject(JSContext *cx, jsval v)
{
    return ToXMLList(cx, v);
}

JSObject *
js_CloneXMLObject(JSContext *cx, JSObject *obj)
{
    uintN flags;
    JSXML *xml;

    if (!GetXMLSettingFlags(cx, &flags))
        return NULL;
    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (flags & (XSF_IGNORE_COMMENTS |
                 XSF_IGNORE_PROCESSING_INSTRUCTIONS |
                 XSF_IGNORE_WHITESPACE)) {
        xml = DeepCopy(cx, xml, NULL, flags);
        if (!xml)
            return NULL;
        return xml->object;
    }
    return NewXMLObject(cx, xml);
}

JSObject *
js_NewXMLSpecialObject(JSContext *cx, JSXMLClass xml_class, JSString *name,
                       JSString *value)
{
    JSObject *obj;
    JSXML *xml;
    JSXMLQName *qn;

    obj = js_NewXMLObject(cx, xml_class);
    if (!obj)
        return NULL;
    xml = (JSXML *) JS_GetPrivate(cx, obj);
    if (name) {
        qn = js_NewXMLQName(cx, cx->runtime->emptyString, NULL, name);
        if (!qn)
            return NULL;
        xml->name = qn;
    }
    xml->xml_value = value;
    return obj;
}

#endif /* JS_HAS_XML_SUPPORT */