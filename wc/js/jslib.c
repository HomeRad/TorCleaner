/* Spidermonkey JavaScript wrapper class, ported from BFilter.
   Homepage: http://www.mozilla.org/js/spidermonkey/
   Copyright for BFilter follows:

   BFilter - a smart ad-filtering web proxy
   Copyright (C) 2002-2003  Joseph Artsimovich <joseph_a@mail.ru>

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

#include <Python.h>
#include "structmember.h"
#ifdef WIN32
#define XP_PC
#else
#define XP_UNIX
#endif
#include <jsapi.h>

/* size for JS_NewRuntime() */
#define RUNTIME_SIZE 0x400000L
/* size for JS_NewContext() */
#define STACK_CHUNK_SIZE 8192

/* javascript exception */
static PyObject* JSError;

/* class type definition and check macro */
staticforward PyTypeObject JSEnvType;
#define check_jsenvobject(v) if (!((v)->ob_type == &JSEnvType)) { \
    PyErr_SetString(PyExc_TypeError, "function arg not a JSEnv object"); \
    return NULL; \
    }

/* generic JS class stub */
static JSClass generic_class = {
    "generic",          /* name */
    0,                  /* flags */
    JS_PropertyStub,    /* add property */
    JS_PropertyStub,    /* del property */
    JS_PropertyStub,    /* get property */
    JS_PropertyStub,    /* set property */
    JS_EnumerateStub,   /* enumerate */
    JS_ResolveStub,     /* resolve */
    JS_ConvertStub,     /* convert */
    JS_FinalizeStub     /* finalize */
};

/* hard branching limit to avoid recursive loops */
static const int BRANCH_LIMIT = 20000;

/* object for JS environment */
typedef struct {
    PyObject_HEAD
    PyObject* listeners;
    PyObject* document_cookie; /* cookie string */
    PyObject* scheduled_actions;
    JSRuntime* runtime;
    JSContext* ctx;
    JSClass global_class;
    JSClass document_class;
    JSClass body_class;
    JSClass navigator_class;
    JSClass location_class;
    JSClass screen_class;
    JSClass image_class;
    JSClass form_class;
    JSClass mimetype_class;
    JSClass plugin_class;
    JSObject* global_obj;
    JSObject* doc_obj;
    JSObject* form_array;
    int branch_cnt;
} JSEnvObject;


/* macro for environment access */
#define get_environment(cx) ((JSEnvObject*)JS_GetPrivate(cx, JS_GetGlobalObject(cx)))


/* apply python callbacks for JS output */
static int dispatchOutput (JSEnvObject* env, PyObject* output) {
    PyObject* iterator = NULL;
    PyObject* item = NULL;
    if ((iterator = PyObject_GetIter(env->listeners))==NULL) {
        return -1;
    }
    while ((item = PyIter_Next(iterator))!=NULL) {
        PyObject* callback;
        PyObject* result;
        if ((callback = PyObject_GetAttrString(item, "js_process_data"))==NULL) {
            Py_DECREF(item);
            Py_DECREF(iterator);
            return -1;
        }
        if ((result = PyObject_CallFunction(callback, "O", output))==NULL) {
            Py_DECREF(callback);
            Py_DECREF(item);
            Py_DECREF(iterator);
            return -1;
        }
        /* release references when done */
        Py_DECREF(item);
        Py_DECREF(result);
        Py_DECREF(callback);
    }
    Py_DECREF(iterator);
    return 0;
}


/* apply python callbacks for JS popups */
static int dispatchPopupNotification (JSEnvObject* env) {
    PyObject* iterator = NULL;
    PyObject* item = NULL;
    if ((iterator = PyObject_GetIter(env->listeners))==NULL) {
        return -1;
    }
    while ((item = PyIter_Next(iterator))!=NULL) {
        PyObject* callback;
        PyObject* result;
        if ((callback = PyObject_GetAttrString(item, "js_process_popup"))==NULL) {
            Py_DECREF(item);
            Py_DECREF(iterator);
            return -1;
        }
        if ((result = PyObject_CallFunction(callback, ""))==NULL) {
            Py_DECREF(callback);
            Py_DECREF(item);
            Py_DECREF(iterator);
            return -1;
        }
        /* release references when done */
        Py_DECREF(item);
        Py_DECREF(result);
        Py_DECREF(callback);
    }
    Py_DECREF(iterator);
    return 0;
}


static int dispatchError (JSEnvObject* env, PyObject* err) {
    PyObject* iterator = NULL;
    PyObject* item = NULL;
    if ((iterator = PyObject_GetIter(env->listeners))==NULL) {
        return -1;
    }
    while ((item = PyIter_Next(iterator))!=NULL) {
        PyObject* callback;
        PyObject* result;
        /* do something with item */
        if ((callback = PyObject_GetAttrString(item, "js_process_error"))==NULL) {
            Py_DECREF(item);
            Py_DECREF(iterator);
            return -1;
        }
        if ((result = PyObject_CallFunction(callback, "O", err))==NULL) {
            Py_DECREF(callback);
            Py_DECREF(item);
            Py_DECREF(iterator);
            return -1;
        }
        /* release references when done */
        Py_DECREF(item);
        Py_DECREF(result);
        Py_DECREF(callback);
    }
    Py_DECREF(iterator);
    return 0;
}


static void errorReporter (JSContext* cx, const char* msg,
                           JSErrorReport* report) {
    PyObject* cStringIO = NULL;
    PyObject* io = NULL;
    PyObject* err = NULL;
    int skip_chars;
    if (!(cStringIO = PyImport_ImportModule("cStringIO"))) goto rep_error;
    if (!(io = PyObject_CallMethod(cStringIO, "StringIO", NULL))) goto rep_error;
    PyFile_WriteString(msg, io);
    PyFile_WriteString("\n", io);
    if (report->linebuf) {
		int i;
        PyFile_WriteString(report->linebuf, io);
        PyFile_WriteString("\n", io);
        skip_chars = report->tokenptr - report->linebuf;
        for (i=0; i<skip_chars; i++) {
            PyFile_WriteString(" ", io);
        }
        PyFile_WriteString("^\n", io);
    }
    if (!(err = PyObject_CallMethod(io, "getvalue", NULL))) goto rep_error;
    dispatchError(get_environment(cx), err);
rep_error:
    Py_XDECREF(err);
    Py_XDECREF(io);
    Py_XDECREF(cStringIO);
}


/* callback to prevent recursive loops */
static JSBool branchCallback (JSContext *cx, JSScript *script) {
    JSEnvObject* env = get_environment(cx);
    if (++(env->branch_cnt) < BRANCH_LIMIT) {
        return JS_TRUE;
    }
    /* infinite loop? */
    env->branch_cnt = 0;
    return JS_FALSE; /* terminate the script */
}


static JSBool cookieGetter (JSContext* cx, JSObject* obj, jsval id, jsval* vp) {
    JSEnvObject* env = get_environment(cx);
    if (env->document_cookie) {
        JSString* cookie = JS_NewStringCopyN(cx, PyString_AsString(env->document_cookie),
                                             PyString_Size(env->document_cookie));
        if (cookie) {
            *vp = STRING_TO_JSVAL(cookie);
            return JS_TRUE;
        }
    }
    *vp = STRING_TO_JSVAL(JS_NewStringCopyZ(cx, ""));
    return JS_TRUE;
}


static JSBool cookieSetter (JSContext* cx, JSObject* obj, jsval id, jsval* vp) {
    JSEnvObject* env = get_environment(cx);
    char* cookie = JS_GetStringBytes(JS_ValueToString(cx, *vp));
    if (!env->document_cookie) {
        env->document_cookie = PyString_FromString(cookie);
    }
    else {
        Py_DECREF(env->document_cookie);
        /* ok, I know this is a wrong behavior, but it's enough to convince
         * some scripts that getting/setting a cookie works */
        env->document_cookie = PyString_FromFormat("%s %s", ";", cookie);
    }
    return JS_TRUE;
}


static JSBool onloadSetter (JSContext *cx, JSObject *obj, jsval id, jsval *vp) {
    JSEnvObject* env = get_environment(cx);
    PyObject* functup;
    PyObject* delay = NULL;
    PyObject* funcname = NULL;
    JSFunction* func = JS_ValueToFunction(cx, *vp);
    if (!func) return JS_FALSE;
    if (!(functup = PyTuple_New(2))) return JS_FALSE;
    if (!(delay = PyInt_FromLong(2000))) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyTuple_SetItem(functup, 0, delay)!=0) {
	/* remember: SetItem has ownership of delay now */
	Py_DECREF(functup);
	return JS_FALSE;
    }
    if (!(funcname = PyString_FromFormat("%s%s", JS_GetFunctionName(func), "()"))) {
	Py_DECREF(functup);
	return JS_FALSE;
    }
    if (PyTuple_SetItem(functup, 1, funcname)!=0) {
	/* remember: SetItem has ownership of delay and funcname now */
	Py_DECREF(functup);
	return JS_FALSE;
    }
    if (PyList_Append(env->scheduled_actions, functup)!=0) {
	Py_DECREF(functup);
	return JS_FALSE;
    }
    return JS_TRUE;
}


static JSBool onunloadSetter (JSContext *cx, JSObject *obj, jsval id, jsval *vp) {
    JSEnvObject* env = get_environment(cx);
    PyObject* functup;
    PyObject* delay = NULL;
    PyObject* funcname = NULL;
    JSFunction* func = JS_ValueToFunction(cx, *vp);
    if (!func) return JS_FALSE;
    if (!(functup = PyTuple_New(2))) return JS_FALSE;
    if (!(delay = PyInt_FromLong(2000))) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyTuple_SetItem(functup, 0, delay)!=0) {
	/* remember: SetItem has ownership of delay now */
	Py_DECREF(functup);
	return JS_FALSE;
    }
    if (!(funcname = PyString_FromFormat("%s%s", JS_GetFunctionName(func), "()"))) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyTuple_SetItem(functup, 1, funcname)!=0) {
	/* remember: SetItem has ownership of delay and funcname now */
	Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyList_Append(env->scheduled_actions, functup)!=0) {
	Py_DECREF(functup);
	return JS_FALSE;
    }
    return JS_TRUE;
}


/* Disable Java */
static JSBool javaEnabled (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    *rval = JSVAL_FALSE;
    return JS_TRUE;
}


/* Dispatch notification about an opened window. */
static JSBool windowOpen (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    int res = dispatchPopupNotification(get_environment(cx));
    *rval = JSVAL_NULL;
    return (res==0 ? JS_TRUE : JS_FALSE);
}


static JSBool setTimeout (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    JSEnvObject* env;
    PyObject* functup = NULL;
    PyObject* delay = NULL;
    PyObject* funcname = NULL;
    static int idc = 1;
    *rval = INT_TO_JSVAL(idc++);
    if (argc < 2)
        return JS_TRUE;
    env = get_environment(cx);
    if (!(functup = PyTuple_New(2))) return JS_FALSE;
    if (!(delay = PyInt_FromLong(JSVAL_TO_INT(argv[1])))) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyTuple_SetItem(functup, 0, delay)!=0) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    if (!(funcname = PyString_FromString(JS_GetStringBytes(JS_ValueToString(cx, argv[0]))))) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyTuple_SetItem(functup, 1, funcname)!=0) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyList_Append(env->scheduled_actions, functup)!=0) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    return JS_TRUE;
}


static JSBool documentWrite (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    PyObject* data;
    *rval = JSVAL_VOID;
    if (argc < 1)
        return JS_TRUE;
    data = PyString_FromString(JS_GetStringBytes(JS_ValueToString(cx, argv[0])));
    if (!data) return JS_FALSE;
    return (dispatchOutput(get_environment(cx), data)==0 ? JS_TRUE : JS_FALSE);
}


static JSBool documentWriteln (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    PyObject* data;
    *rval = JSVAL_VOID;
    if (argc < 1)
        return JS_TRUE;
    data = PyString_FromFormat("%s\r\n", JS_GetStringBytes(JS_ValueToString(cx, argv[0])));
    if (!data) return JS_FALSE;
    return (dispatchOutput(get_environment(cx), data)==0 ? JS_TRUE : JS_FALSE);
}


static JSBool imageConstructor (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    JSObject* image_obj = JS_NewObject(cx, &get_environment(cx)->image_class, 0, 0);
    if (!image_obj)
        return JS_FALSE;
    if (JS_DefineProperty(cx, image_obj, "complete", JSVAL_TRUE, 0, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT|JSPROP_READONLY)
        ==JS_FALSE) {
        return JS_FALSE;
    }
    *rval = OBJECT_TO_JSVAL(image_obj);
    return JS_TRUE;
}


static JSBool formSubmit (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    jsval target;
    int res = 1;
    JS_GetProperty(cx, obj, "target", &target);
    if (JSVAL_IS_STRING(target)) {
        if (JS_GetStringLength(JSVAL_TO_STRING(target)) > 0) {
            res = dispatchPopupNotification(get_environment(cx));
        }
    }
    *rval = JSVAL_VOID;
    return (res==0 ? JS_TRUE : JS_FALSE);
}


static JSBool doNothing (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    *rval = JSVAL_VOID;
    return JS_TRUE;
}


static JSBool wcDebugLog (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    PyObject* _sys;
    PyObject* _stderr;
    *rval = JSVAL_VOID;
    if (argc < 1)
        return JS_TRUE;
    if (!(_sys = PyImport_ImportModule("sys"))) return JS_TRUE;
    if (!(_stderr = PyObject_GetAttrString(_sys, "stderr"))) return JS_TRUE;
    PyFile_WriteString("JS: wcDebugLog(", _stderr);
    PyFile_WriteString(JS_GetStringBytes(JS_ValueToString(cx, argv[0])), _stderr);
    PyFile_WriteString(")\n", _stderr);
    return JS_TRUE;
}


static void setJSVersion (JSContext* ctx, double vers) {
    JSVersion jsv;
    if (vers==1.0) {
        jsv = JSVERSION_1_0;
    } else if (vers == 1.1) {
        jsv = JSVERSION_1_1;
    } else if (vers == 1.2) {
        jsv = JSVERSION_1_2;
    } else if (vers == 1.3) {
        jsv = JSVERSION_1_3;
    } else if (vers == 1.4) {
        jsv = JSVERSION_1_4;
    } else if (vers == 1.5) {
        jsv = JSVERSION_1_5;
    } else {
        jsv = JSVERSION_DEFAULT;
    }
    JS_SetVersion(ctx, jsv);
}


static int executeScheduledActions (JSEnvObject* self) {
    jsval rval;
    int len = PyList_Size(self->scheduled_actions);
    int i;
    for (i=0; i<len; i++) {
        PyObject* func;
        PyObject* tup = PyList_GetItem(self->scheduled_actions, i);
        if (!tup) {
            return -1;
        }
        Py_INCREF(tup);
        if (!(func = PyTuple_GetItem(tup, 1))) {
            Py_DECREF(tup);
            return -1;
        }
        Py_INCREF(func);
        JS_EvaluateScript(self->ctx, self->global_obj,
                          PyString_AsString(func),
                          PyString_Size(func), "[unknown]", 1, &rval);
        Py_DECREF(func);
        Py_DECREF(tup);
    }
    if (len < PyList_Size(self->scheduled_actions)) {
        /* XXX warning: the scheduled actions have registered other
         * actions recursively. These are ignored. */
    }
    Py_DECREF(self->scheduled_actions);
    self->scheduled_actions = PyList_New(0);
    return 0;
}


/* destroy JS engine */
static void destroy (JSEnvObject* env) {
    if (env->ctx) JS_DestroyContext(env->ctx);
    if (env->runtime) JS_DestroyRuntime(env->runtime);
}


/** set python memory exception and destroy JS engine */
static void shutdown (JSEnvObject* self, char* msg) {
    PyErr_SetString(JSError, msg);
    Py_DECREF(self);
}


/* create JSEnv object */
static PyObject* JSEnv_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    JSEnvObject* self;
    /* local objects */
    JSObject* location_obj;
    JSObject* nav_obj;
    JSObject* flash_mimetype_obj;
    JSObject* flash_plugin_obj;
    JSObject* screen_obj;
    JSObject* body_obj;
    JSObject* frames_obj;
    JSObject* history_array;
    JSObject* images_array;
    JSObject* layers_array;
    JSObject* mimetypes_array;
    JSObject* plugins_array;
    jsval flash_mimetype_jsval;
    jsval flash_plugin_jsval;
    /* alloc JSEnv object */
    self = (JSEnvObject*)type->tp_alloc(type, 0);
    if (NULL == self) {
        return NULL;
    }
    /* init python objects */
    self->listeners = PyList_New(0);
    if (NULL == self->listeners)
    {
        Py_DECREF(self);
        return NULL;
    }
    if ((self->scheduled_actions = PyList_New(0))==NULL) {
        Py_DECREF(self);
        return NULL;
    }
    self->document_cookie = NULL;
    self->runtime = NULL;
    self->ctx = NULL;
    self->global_class = generic_class;
    self->global_class.name = "Window";
    self->global_class.flags = JSCLASS_HAS_PRIVATE;
    self->document_class = generic_class;
    self->document_class.name = "HTMLDocument";
    self->body_class = generic_class;
    self->body_class.name = "Body";
    self->navigator_class = generic_class;
    self->navigator_class.name = "Navigator";
    self->location_class = generic_class;
    self->location_class.name = "Location";
    self->screen_class = generic_class;
    self->screen_class.name = "Screen";
    self->image_class = generic_class;
    self->image_class.name = "HTMLImageElement";
    self->form_class = generic_class;
    self->form_class.name = "HTMLFormElement";
    self->mimetype_class = generic_class;
    self->mimetype_class.name = "MimeType";
    self->plugin_class = generic_class;
    self->plugin_class.name = "Plugin";
    self->branch_cnt = 0;
    /* init JS engine */
    self->runtime = JS_NewRuntime(RUNTIME_SIZE);
    if (NULL == self->runtime) {
        shutdown(self, "Could not initialize JS runtime");
        return NULL;
    }
    self->ctx = JS_NewContext(self->runtime, STACK_CHUNK_SIZE);
    if (NULL == self->ctx) {
        shutdown(self, "Could not initialize JS context");
        return NULL;
    }

    /* configure JS engine */
    JS_SetErrorReporter(self->ctx, &errorReporter);
    JS_SetBranchCallback(self->ctx, &branchCallback);

    /* init global object */
    self->global_obj = JS_NewObject(self->ctx, &self->global_class, NULL, NULL);
    if (NULL == self->global_obj) {
        shutdown(self, "Could not initialize global object");
        return NULL;
    }
    if (JS_InitStandardClasses(self->ctx, self->global_obj)==JS_FALSE) {
        shutdown(self, "Could not init standard classes");
        return NULL;
    }
    if (JS_SetPrivate(self->ctx, self->global_obj, self)==JS_FALSE) {
        shutdown(self, "Could not set private env var");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->global_obj, "self",
                          OBJECT_TO_JSVAL(self->global_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set global self property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->global_obj, "window",
                          OBJECT_TO_JSVAL(self->global_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set global window property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->global_obj, "top",
                          OBJECT_TO_JSVAL(self->global_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set global top property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->global_obj, "parent",
                          OBJECT_TO_JSVAL(self->global_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set global parent property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->global_obj, "onload",
                          JSVAL_NULL, 0, &onloadSetter,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set global onload property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->global_obj, "onunload",
                          JSVAL_NULL, 0, &onunloadSetter,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set global onunload property");
        return NULL;
    }
    if (!(history_array=JS_NewArrayObject(self->ctx, 0, 0))) {
        shutdown(self, "Could not create history array object");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->global_obj, "history",
                          OBJECT_TO_JSVAL(history_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set global history property");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "open", &windowOpen,
                           1, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global open function");
        return NULL;
    }
    /* note: window.createPopup() is an IE extension */
    if (!JS_DefineFunction(self->ctx, self->global_obj, "createPopup", &windowOpen,
                           0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global createPopup function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "setTimeout", &setTimeout,
                           2, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global setTimeout function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "setInterval", &setTimeout,
                           2, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global setInterval function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "clearTimeout", &doNothing,
                           1, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global clearTimeout function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "clearInterval", &doNothing,
                           1, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global clearInterval function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "alert", &windowOpen,
                           1, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global alert function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "focus", &doNothing,
                           0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global focus function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "blur", &doNothing,
                           0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global blur function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "resizeTo", &doNothing,
                           2, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global resizeTo function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "moveTo", &doNothing,
                           2, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global moveTo function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "Image", &imageConstructor,
                           0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global Image function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->global_obj, "wcDebugLog", &wcDebugLog,
                           0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set global wcDebugLog function");
        return NULL;
    }
    /* init location object */
    if (!(location_obj=JS_DefineObject(self->ctx, self->global_obj, "location",
                                       &self->location_class, 0,
                                       JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        shutdown(self, "Could not create location object");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, location_obj, "protocol",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "http:")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set location.protocol property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, location_obj, "host",
                          JS_GetEmptyStringValue(self->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set location.host property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, location_obj, "hostname",
                          JS_GetEmptyStringValue(self->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set location.hostname property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, location_obj, "port",
                          INT_TO_JSVAL(80), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set location.port property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, location_obj, "pathname",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "/")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set location.pathname property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, location_obj, "hash",
                          JS_GetEmptyStringValue(self->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set location.hash property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, location_obj, "href",
                          JS_GetEmptyStringValue(self->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set location.href property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, location_obj, "search",
                          JS_GetEmptyStringValue(self->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set location.search property");
        return NULL;
    }
    /* init navigator object */
    if (!(nav_obj=JS_DefineObject(self->ctx, self->global_obj, "navigator",
                                  &self->navigator_class, 0,
                                  JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        shutdown(self, "Could not create nav object");
        return NULL;
    }
    if (JS_DefineFunction(self->ctx, nav_obj, "javaEnabled", &javaEnabled, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set navigator.javaEnabled property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, nav_obj, "appCodeName",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "Mozilla")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set navigator.appCodeName property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, nav_obj, "appName",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "Netscape")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set navigator.appName property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, nav_obj, "appVersion",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "3.01 (Windows; en-US)")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set navigator.appVersion property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, nav_obj, "userAgent",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "Mozilla/3.01Gold (Win95; I)")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set navigator.userAgent property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, nav_obj, "platform",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "Windows")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set navigator.userAgent property");
        return NULL;
    }

    /* init flash objects */
    if (!(mimetypes_array=JS_NewArrayObject(self->ctx, 0, 0))) {
        shutdown(self, "Could not create mimetypes array object");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, nav_obj, "mimeTypes",
                          OBJECT_TO_JSVAL(mimetypes_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set navigator.mimeTypes property");
        return NULL;
    }
    if (!(plugins_array=JS_NewArrayObject(self->ctx, 0, 0))) {
        shutdown(self, "Could not create plugins array object");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, nav_obj, "plugins",
                          OBJECT_TO_JSVAL(plugins_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set navigator.plugins property");
        return NULL;
    }
    if (!(flash_mimetype_obj=JS_DefineObject(self->ctx, mimetypes_array, "application/x-shockwave-flash",
                                             &self->mimetype_class, 0,
                                             JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        shutdown(self, "Could not create flash mimetype object");
        return NULL;
    }
    flash_mimetype_jsval = OBJECT_TO_JSVAL(flash_mimetype_obj);
    if (JS_SetElement(self->ctx, mimetypes_array, 0, &flash_mimetype_jsval)
        ==JS_FALSE) {
        shutdown(self, "Could not set mimetype array element");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, flash_mimetype_obj, "description",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "Shockwave Flash")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set flash description property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, flash_mimetype_obj, "type",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "application/x-shockwave-flash")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set flash type property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, flash_mimetype_obj, "suffixes",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "swf")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set flash suffixes property");
        return NULL;
    }
    if (!(flash_plugin_obj=JS_DefineObject(self->ctx, flash_mimetype_obj, "enabledPlugin",
                                           &self->plugin_class, 0,
                                           JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        shutdown(self, "Could not create flash plugin object");
        return NULL;
    }
    flash_plugin_jsval = OBJECT_TO_JSVAL(flash_plugin_obj);
    if (JS_SetElement(self->ctx, plugins_array, 0, &flash_plugin_jsval)
        ==JS_FALSE) {
        shutdown(self, "Could not set plugin array element");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, plugins_array, "Shockwave Flash",
                          flash_plugin_jsval, 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set plugin array string");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, flash_plugin_obj, "name",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "Shockwave Flash")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set enabledPlugin.name property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, flash_plugin_obj, "description",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "Shockwave Flash 5.0 r50")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set enabledPlugin.description property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, flash_plugin_obj, "length",
                          INT_TO_JSVAL(1), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set enabledPlugin.length property");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, flash_plugin_obj, "refresh",
                           &doNothing, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set enabledPlugin.refresh function");
        return NULL;
    }

    /* init screen object */
    if (!(screen_obj=JS_DefineObject(self->ctx, self->global_obj, "screen",
                                     &self->screen_class, 0,
                                     JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        shutdown(self, "Could not create screen object");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, screen_obj, "width",
                          INT_TO_JSVAL(1024), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set screen.width property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, screen_obj, "height",
                          INT_TO_JSVAL(768), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set screen.height property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, screen_obj, "availWidth",
                          INT_TO_JSVAL(1014), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set screen.availWidth property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, screen_obj, "availHeight",
                          INT_TO_JSVAL(720), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set screen.availHeight property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, screen_obj, "colorDepth",
                          INT_TO_JSVAL(16), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set screen.colorDepth property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, screen_obj, "pixelDepth",
                          INT_TO_JSVAL(16), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set screen.pixelDepth property");
        return NULL;
    }

    /* init frames object */
    if (!(frames_obj=JS_NewArrayObject(self->ctx, 0, 0))) {
        shutdown(self, "Could not create frames object");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->global_obj, "frames",
                          OBJECT_TO_JSVAL(frames_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set global frames property");
        return NULL;
    }

    /* init document object */
    if (!(self->doc_obj=JS_DefineObject(self->ctx, self->global_obj, "document",
                                       &self->document_class, 0,
                                       JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        shutdown(self, "Could not create document object");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->doc_obj, "cookie",
                          JS_GetEmptyStringValue(self->ctx), &cookieGetter, &cookieSetter,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set document.cookie property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->doc_obj, "location",
                          OBJECT_TO_JSVAL(location_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set document.location property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->doc_obj, "domain",
                          JS_GetEmptyStringValue(self->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set document.domain property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->doc_obj, "referrer",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "http://imadoofus/")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set document.referrer property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->doc_obj, "URL",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(self->ctx, "http://imadoofus/")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set document.URL property");
        return NULL;
    }
    if (!(images_array=JS_NewArrayObject(self->ctx, 0, 0))) {
        shutdown(self, "Could not create images array");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->doc_obj, "images",
                          OBJECT_TO_JSVAL(images_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT|JSPROP_READONLY)
        ==JS_FALSE) {
        shutdown(self, "Could not set document.images property");
        return NULL;
    }
    if (!(layers_array=JS_NewArrayObject(self->ctx, 0, 0))) {
        shutdown(self, "Could not create layers array");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->doc_obj, "layers",
                          OBJECT_TO_JSVAL(layers_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT|JSPROP_READONLY)
        ==JS_FALSE) {
        shutdown(self, "Could not set document.layers property");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->doc_obj, "write", &documentWrite, 1,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set document.write function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->doc_obj, "writeln",
                           &documentWriteln, 1, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set document.writeln function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->doc_obj, "open", &doNothing, 0,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set document.open function");
        return NULL;
    }
    if (!JS_DefineFunction(self->ctx, self->doc_obj, "close", &doNothing, 0,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        shutdown(self, "Could not set document.close function");
        return NULL;
    }

    /* init body object */
    if (!(body_obj=JS_DefineObject(self->ctx, self->doc_obj, "body",
                                   &self->body_class, 0,
                                   JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        shutdown(self, "Could not create document.body object");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, body_obj, "clientHeight",
                          INT_TO_JSVAL(768), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set body.clientHeight property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, body_obj, "clientWidth",
                          INT_TO_JSVAL(1024), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set body.clientWidth property");
        return NULL;
    }

    /* init form array */
    if (!(self->form_array=JS_NewArrayObject(self->ctx, 0, 0))) {
        shutdown(self, "Could not create form array");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, self->doc_obj, "forms",
                          OBJECT_TO_JSVAL(self->form_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        shutdown(self, "Could not set doc forms property");
        return NULL;
    }
    return (PyObject*) self;
}


/* initialize JSEnv object */
static int JSEnv_init (JSEnvObject* self, PyObject* args, PyObject* kwds) {
        /* init structure */
    if (!PyArg_ParseTuple(args, ":JSEnv.__init__"))
        return -1;
    return 0;
}


/* traverse all used subobjects participating in reference cycles */
static int JSEnv_traverse (JSEnvObject* self, visitproc visit, void* arg) {
    if (self->listeners && visit(self->listeners, arg) < 0) {
        return -1;
    }
    return 0;
}


/* clear all used subobjects participating in reference cycles */
static int JSEnv_clear (JSEnvObject* self) {
    Py_XDECREF(self->listeners);
    Py_XDECREF(self->scheduled_actions);
    return 0;
}


/* destroy */
static void JSEnv_dealloc (JSEnvObject* self) {
    destroy(self);
    JSEnv_clear(self);
    self->ob_type->tp_free((PyObject*)self);
}


static PyObject* JSEnv_executeScript (JSEnvObject* self, PyObject* args) {
    PyObject* script;
    double version;
    jsval rval;
    JSBool res;
    if (!PyArg_ParseTuple(args, "Sd", &script, &version)) {
	PyErr_SetString(PyExc_TypeError, "script and version arg required");
        return NULL;
    }
    setJSVersion(self->ctx, version);
    res = JS_EvaluateScript(self->ctx, self->global_obj,
                            PyString_AsString(script),
                            PyString_Size(script),
                            "[unknown]", 1, &rval);
    if (executeScheduledActions(self) < 0) {
        return NULL;
    }
    if (res == JS_TRUE) {
        return PyInt_FromLong(1);
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* JSEnv_executeScriptAsFunction (JSEnvObject* self, PyObject* args) {
    PyObject* script;
    double version;
    jsval rval;
    JSBool res;
    JSFunction* func;
    if (!PyArg_ParseTuple(args, "Sd", &script, &version)) {
	PyErr_SetString(PyExc_TypeError, "script and version arg required");
        return NULL;
    }
    setJSVersion(self->ctx, version);
    func = JS_CompileFunction(self->ctx, self->global_obj, 0, 0, 0,
                                          PyString_AsString(script),
                                          PyString_Size(script),
                                          "[unknown]", 1);
    if (!func) {
	PyErr_SetString(JSError, "JS_CompileFunction failed");
        return NULL;
    }
    res = JS_CallFunction(self->ctx, self->global_obj, func, 0, 0, &rval);
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* JSEnv_addForm (JSEnvObject* self, PyObject* args) {
    PyObject* name;
    PyObject* action;
    PyObject* target;
    JSObject* form_obj;
    jsval form_jsval;
    jsuint nforms;
    if (!PyArg_ParseTuple(args, "SSS", &name, &action, &target)) {
	PyErr_SetString(PyExc_TypeError, "name, action and target arg required");
        return NULL;
    }
    if (!(form_obj=JS_NewObject(self->ctx, &self->form_class, 0, 0))) {
	PyErr_SetString(JSError, "JS_NewObject failed");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, form_obj, "name",
                          STRING_TO_JSVAL(JS_NewStringCopyN(self->ctx, PyString_AsString(name), PyString_Size(name))), 0, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not set form.name property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, form_obj, "action",
                          STRING_TO_JSVAL(JS_NewStringCopyN(self->ctx, PyString_AsString(action), PyString_Size(action))), 0, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not set form.action property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, form_obj, "target",
                          STRING_TO_JSVAL(JS_NewStringCopyN(self->ctx, PyString_AsString(target), PyString_Size(target))), 0, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not set form.target property");
        return NULL;
    }
    if (JS_DefineFunction(self->ctx, form_obj, "submit", &formSubmit, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not set form.submit property");
        return NULL;
    }
    if (JS_DefineFunction(self->ctx, form_obj, "reset", &doNothing, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not set form.reset property");
        return NULL;
    }
    form_jsval = OBJECT_TO_JSVAL(form_obj);
    nforms = 0;
    if (JS_GetArrayLength(self->ctx, self->form_array, &nforms)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not get form array length");
        return NULL;
    }
    if (JS_SetElement(self->ctx, self->form_array, nforms, &form_jsval)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not set form array");
        return NULL;
    }
    if (PyString_Size(name)>0) {
        if (JS_DefineProperty(self->ctx, self->form_array, PyString_AsString(name), OBJECT_TO_JSVAL(form_obj), 0, 0, JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
            ==JS_FALSE) {
            PyErr_SetString(JSError, "Could not set form array property");
            return NULL;
        }
        if (JS_DefineProperty(self->ctx, self->doc_obj, PyString_AsString(name), OBJECT_TO_JSVAL(form_obj), 0, 0, JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
            ==JS_FALSE) {
            PyErr_SetString(JSError, "Could not set document property");
            return NULL;
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMemberDef JSEnv_members[] = {
    {"listeners", T_OBJECT_EX, offsetof(JSEnvObject, listeners), 0,
     "set of listener objects"},
    {NULL}  /* Sentinel */
};


/* public JSEnv object methods */
static PyMethodDef JSEnv_methods[] = {
    {"executeScript", (PyCFunction)JSEnv_executeScript, METH_VARARGS, "execute script"},
    {"executeScriptAsFunction", (PyCFunction)JSEnv_executeScriptAsFunction, METH_VARARGS, "execute script as function"},
    {"addForm", (PyCFunction)JSEnv_addForm, METH_VARARGS, "add form element"},
    {NULL} /* Sentinel */
};


/* object type definition */
static PyTypeObject JSEnvType = {
    PyObject_HEAD_INIT(NULL)
    0,              /* ob_size */
    "wc.js.jslib.JSEnv",  /* tp_name */
    sizeof(JSEnvObject), /* tp_size */
    0,              /* tp_itemsize */
    /* methods */
    (destructor)JSEnv_dealloc, /* tp_dealloc */
    0,              /* tp_print */
    0,              /* tp_getattr */
    0,              /* tp_setattr */
    0,              /* tp_compare */
    0,              /* tp_repr */
    0,              /* tp_as_number */
    0,              /* tp_as_sequence */
    0,              /* tp_as_mapping */
    0,              /* tp_hash */
    0,              /* tp_call */
    0,              /* tp_str */
    0,              /* tp_getattro */
    0,              /* tp_setattro */
    0,              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | 
      Py_TPFLAGS_HAVE_GC, /* tp_flags */
    "JavaScript Environment object", /* tp_doc */
    (traverseproc)JSEnv_traverse,    /* tp_traverse */
    (inquiry)JSEnv_clear, /* tp_clear */
    0,              /* tp_richcompare */
    0,              /* tp_weaklistoffset */
    0,              /* tp_iter */
    0,              /* tp_iternext */
    JSEnv_methods,  /* tp_methods */
    JSEnv_members,  /* tp_members */
    0,              /* tp_getset */
    0,              /* tp_base */
    0,              /* tp_dict */
    0,              /* tp_descr_get */
    0,              /* tp_descr_set */
    0,              /* tp_dictoffset */
    (initproc)JSEnv_init,  /* tp_init */
    0,              /* tp_alloc */
    JSEnv_new,      /* tp_new */
};


/* python module interface */
static PyMethodDef jslib_methods[] = {
    {NULL} /* Sentinel */
};


#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
/* initialization of the module */
PyMODINIT_FUNC initjslib (void) {
    PyObject *m;
    if (PyType_Ready(&JSEnvType) < 0) {
        return;
    }
    if ((m = Py_InitModule3("jslib", jslib_methods, "JavaScript Environment module"))==NULL) {
        return;
    }
    Py_INCREF(&JSEnvType);
    if (PyModule_AddObject(m, "JSEnv", (PyObject *)&JSEnvType)==-1) {
        /* init error */
        PyErr_Print();
        return;
    }
    JSError = PyErr_NewException("wc.js.jslib.error", NULL, NULL);
    if (PyModule_AddObject(m, "error", JSError)==-1) {
        /* init error */
        PyErr_Print();
        return;
    }
}

#ifdef WIN32
#undef XP_PC
#else
#undef XP_UNIX
#endif
