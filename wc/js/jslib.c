/* Spidermonkey JavaScript wrapper class, ported from BFilter.
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
#ifdef WIN32
#define XP_PC
#else
#define XP_UNIX
#endif
#include <jsapi.h>

/* javascript exception */
static PyObject* JSError;

/* class type definition and check macro*/
staticforward PyTypeObject JSEnvType;
#define check_jsenvobject(v) if (!((v)->ob_type == &JSEnvType)) { \
    PyErr_SetString(PyExc_TypeError, "function arg not a JSEnv object"); \
    return NULL; \
    }

/* generic JS class stub */
static JSClass generic_class = {
    "generic", 0,
    JS_PropertyStub, JS_PropertyStub, JS_PropertyStub, JS_PropertyStub,
    JS_EnumerateStub, JS_ResolveStub, JS_ConvertStub, JS_FinalizeStub
};

static const int BRANCH_LIMIT = 1000;

typedef struct {
    PyObject_HEAD
    PyObject* listeners;
    PyObject* document_cookie; // cookie string
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


static JSEnvObject* getEnvironment (JSContext* cx) {
    return (JSEnvObject*)JS_GetPrivate(cx, JS_GetGlobalObject(cx));
}


static int dispatchOutput (JSEnvObject* env, PyObject* output) {
    PyObject* keys;
    int size;
    PyObject* listener = NULL;
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (!(keys = PyMapping_Keys(env->listeners))) return -1;
    size = PySequence_Size(keys);
    for (int i=0; i<size; i++) {
        if (!(listener = PySequence_GetItem(keys, i))) { error=-1; goto disp_error; }
        if (!(callback = PyObject_GetAttrString(listener, "processData"))) { error=-1; goto disp_error; }
        if (!(result = PyObject_CallFunction(callback, "O", output))) { error=-1; goto disp_error; }
    }
disp_error:
    Py_XDECREF(keys);
    Py_XDECREF(listener);
    Py_XDECREF(callback);
    Py_XDECREF(result);
    return error;
}


static int dispatchPopupNotification (JSEnvObject* env) {
    PyObject* keys;
    int size;
    PyObject* listener = NULL;
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (!(keys = PyMapping_Keys(env->listeners))) return -1;
    size = PySequence_Size(keys);
    for (int i=0; i<PySequence_Size(keys); i++) {
        if (!(listener = PySequence_GetItem(keys, i))) { error=-1; goto dispp_error; }
        if (!(callback = PyObject_GetAttrString(listener, "processPopup"))) { error=-1; goto dispp_error; }
        if (!(result = PyObject_CallFunction(callback, ""))) { error=-1; goto dispp_error; }
    }
dispp_error:
    Py_XDECREF(keys);
    Py_XDECREF(listener);
    Py_XDECREF(callback);
    Py_XDECREF(result);
    return error;
}


static void errorReporter (JSContext *cx, const char *msg, JSErrorReport *report) {
    PyObject* sys;
    PyObject* stderr;
    int skip_chars;
    if (!(sys = PyImport_ImportModule("sys"))) return;
    if (!(stderr = PyObject_GetAttrString(sys, "stderr"))) return;
    PyFile_WriteString(msg, stderr);
    PyFile_WriteString("\n", stderr);
    if (report->linebuf) {
        PyFile_WriteString(report->linebuf, stderr);
        PyFile_WriteString("\n", stderr);
        skip_chars = report->tokenptr - report->linebuf;
        for (int i=0; i<skip_chars; i++) {
            PyFile_WriteString(" ", stderr);
        }
        PyFile_WriteString("^\n", stderr);
    }
}


static JSBool branchCallback (JSContext *cx, JSScript *script) {
    JSEnvObject* env = getEnvironment(cx);
    if (++(env->branch_cnt) < BRANCH_LIMIT) {
        return JS_TRUE;
    }
    // infinite loop?
    env->branch_cnt = 0;
    return JS_FALSE; // terminate the script
}


static JSBool cookieGetter (JSContext* cx, JSObject* obj, jsval id, jsval* vp) {
    JSEnvObject* env = getEnvironment(cx);
    if (env->document_cookie) {
        JSString* cookie = JS_NewStringCopyN(cx, PyString_AsString(env->document_cookie),
                                             PyString_Size(env->document_cookie));
        if (cookie) {
            *vp = STRING_TO_JSVAL(cookie);
            return JS_TRUE;
        }
    }
    *vp = JSVAL_NULL;
    return JS_FALSE;
}


static JSBool cookieSetter (JSContext* cx, JSObject* obj, jsval id, jsval* vp) {
    JSEnvObject* env = getEnvironment(cx);
    char* cookie = JS_GetStringBytes(JS_ValueToString(cx, *vp));
    if (!env->document_cookie) {
        env->document_cookie = PyString_FromString(cookie);
    }
    else {
        Py_DECREF(env->document_cookie);
        // ok, I know this is a wrong behavior, but it's enough to convince
        // some scripts that getting/setting a cookie works
        env->document_cookie = PyString_FromFormat("%s %s", ";", cookie);
    }
    return JS_TRUE;
}


static JSBool onloadSetter (JSContext *cx, JSObject *obj, jsval id, jsval *vp) {
    JSEnvObject* env = getEnvironment(cx);
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
	// remember: SetItem has ownership of delay now
	Py_DECREF(functup);
	return JS_FALSE;
    }
    if (!(funcname = PyString_FromFormat("%s%s", JS_GetFunctionName(func), "()"))) { 
	Py_DECREF(functup);
	return JS_FALSE;
    }
    if (PyTuple_SetItem(functup, 1, funcname)!=0) {
	// remember: SetItem has ownership of delay and funcname now
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
    JSEnvObject* env = getEnvironment(cx);
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
	// remember: SetItem has ownership of delay now
	Py_DECREF(functup);
	return JS_FALSE;
    }
    if (!(funcname = PyString_FromFormat("%s%s", JS_GetFunctionName(func), "()"))) {
        Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyTuple_SetItem(functup, 1, funcname)!=0) {
	// remember: SetItem has ownership of delay and funcname now
	Py_DECREF(functup);
        return JS_FALSE;
    }
    if (PyList_Append(env->scheduled_actions, functup)!=0) {
	Py_DECREF(functup);
	return JS_FALSE;
    }
    return JS_TRUE;
}


static JSBool javaEnabled (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    *rval = JSVAL_FALSE;
    return JS_TRUE;
}


static JSBool windowOpen (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    int res = dispatchPopupNotification(getEnvironment(cx));
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
    env = getEnvironment(cx);
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
    return (dispatchOutput(getEnvironment(cx), data)==0 ? JS_TRUE : JS_FALSE);
}


static JSBool documentWriteln (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    PyObject* data;
    *rval = JSVAL_VOID;
    if (argc < 1)
        return JS_TRUE;
    data = PyString_FromFormat("%s\r\n", JS_GetStringBytes(JS_ValueToString(cx, argv[0])));
    if (!data) return JS_FALSE;
    return (dispatchOutput(getEnvironment(cx), data)==0 ? JS_TRUE : JS_FALSE);
}


static JSBool imageConstructor (JSContext *cx, JSObject *obj, uintN argc, jsval *argv, jsval *rval) {
    JSObject* image_obj = JS_NewObject(cx, &getEnvironment(cx)->image_class, 0, 0);
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
            res = dispatchPopupNotification(getEnvironment(cx));
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
    PyObject* sys;
    PyObject* stderr;
    *rval = JSVAL_VOID;
    if (argc < 1)
        return JS_TRUE;
    if (!(sys = PyImport_ImportModule("sys"))) return JS_TRUE;
    if (!(stderr = PyObject_GetAttrString(sys, "stderr"))) return JS_TRUE;
    PyFile_WriteString("JS: wcDebugLog(", stderr);
    PyFile_WriteString(JS_GetStringBytes(JS_ValueToString(cx, argv[0])), stderr);
    PyFile_WriteString(")\n", stderr);
    return JS_TRUE;
}


static PyObject* JSEnv_attachListener (JSEnvObject* self, PyObject* args) {
    PyObject* item;
    if (!PyArg_ParseTuple(args, "O", &item)) {
	PyErr_SetString(PyExc_TypeError, "listener arg required");
        return NULL;
    }
    Py_INCREF(item);
    Py_INCREF(Py_None);
    PyDict_SetItem(self->listeners, item, Py_None);
    Py_INCREF(item);
    return item;
}


static PyObject* JSEnv_detachListener (JSEnvObject* self, PyObject* args) {
    PyObject* item;
    if (!PyArg_ParseTuple(args, "O", &item)) {
	PyErr_SetString(PyExc_TypeError, "listener arg required");
        return NULL;
    }
    // XXX error code? decref?
    if (PyDict_DelItem(self->listeners, item)!=0) return NULL;
    Py_INCREF(Py_None);
    return Py_None;
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


static void executeScheduledActions (JSEnvObject* self) {
    // XXX error checking!
    jsval rval;
    for (int i=0; i<PyList_Size(self->scheduled_actions); i++) {
        PyObject* func;
        PyObject* tup = PyList_GetItem(self->scheduled_actions, i);
        if (!tup) {
            // XXX error
            continue;
        }
        Py_INCREF(tup);
        if (!(func = PyTuple_GetItem(tup, 1))) {
            // XXX error
            Py_DECREF(tup);
            continue;
        }
        Py_INCREF(func);
        JS_EvaluateScript(self->ctx, self->global_obj,
                          PyString_AsString(func),
                          PyString_Size(func), "[unknown]", 1, &rval);
        Py_DECREF(func);
        Py_DECREF(tup);
    }
    Py_DECREF(self->scheduled_actions);
    self->scheduled_actions = PyList_New(0);
}


static PyObject* JSEnv_executeScript (JSEnvObject* self, PyObject* args) {
    PyObject* script;
    PyObject* version;
    jsval rval;
    JSBool res;
    if (!PyArg_ParseTuple(args, "OO", &script, &version)) {
	PyErr_SetString(PyExc_TypeError, "script and version arg required");
        return NULL;
    }
    setJSVersion(self->ctx, PyFloat_AsDouble(version));
    res = JS_EvaluateScript(self->ctx, self->global_obj,
                            PyString_AsString(script),
                            PyString_Size(script),
                            "[unknown]", 1, &rval);
    executeScheduledActions(self);
    if (res == JS_TRUE) {
        return PyInt_FromLong(1);
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* JSEnv_executeScriptAsFunction (JSEnvObject* self, PyObject* args) {
    PyObject* script;
    PyObject* version;
    jsval rval;
    JSBool res;
    JSFunction* func;
    if (!PyArg_ParseTuple(args, "OO", &script, &version)) {
	PyErr_SetString(PyExc_TypeError, "script and version arg required");
        return NULL;
    }
    setJSVersion(self->ctx, PyFloat_AsDouble(version));
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
    if (!PyArg_ParseTuple(args, "OOO", &name, &action, &target)) {
	PyErr_SetString(PyExc_TypeError, "name, action and target arg required");
        return NULL;
    }
    if (!(form_obj=JS_NewObject(self->ctx, &self->form_class, 0, 0))) {
	PyErr_SetString(JSError, "JS_NewObject failed");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, form_obj, "name", STRING_TO_JSVAL(JS_NewStringCopyN(self->ctx, PyString_AsString(name), PyString_Size(name))), 0, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not set form.name property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, form_obj, "action", STRING_TO_JSVAL(JS_NewStringCopyN(self->ctx, PyString_AsString(action), PyString_Size(action))), 0, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
	PyErr_SetString(JSError, "Could not set form.action property");
        return NULL;
    }
    if (JS_DefineProperty(self->ctx, form_obj, "target", STRING_TO_JSVAL(JS_NewStringCopyN(self->ctx, PyString_AsString(target), PyString_Size(target))), 0, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)
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

/* destroy JS engine */
static void destroy (JSEnvObject* env) {
    if (env->ctx) JS_DestroyContext(env->ctx);
    if (env->runtime) JS_DestroyRuntime(env->runtime);
}


/** set python memory exception and destroy JS engine */
static PyObject* shutdown (JSEnvObject* env, char* msg) {
    destroy(env);
    PyErr_SetString(JSError, msg);
    return NULL;
}


/* create */
static PyObject* JSEnv_new(PyObject* self, PyObject* args) {
    JSEnvObject* env;
    // local objects
    JSObject* location_obj;
    JSObject* nav_obj;
    JSObject* flash_mimetype_obj;
    JSObject* flash_plugin_obj;
    JSObject* screen_obj;
    JSObject* body_obj;
    JSObject* frames_obj;
    JSObject* history_array;
    JSObject* images_array;
    JSObject* mimetypes_array;
    JSObject* plugins_array;
    jsval flash_mimetype_jsval;
    jsval flash_plugin_jsval;

    // init structure
    if (!PyArg_ParseTuple(args,":new_jsenv"))
        return NULL;
    if (!(env=PyObject_New(JSEnvObject, &JSEnvType))) {
        return NULL;
    }
    env->listeners = NULL;
    env->document_cookie = NULL;
    env->scheduled_actions = NULL;
    env->runtime = NULL;
    env->ctx = NULL;
    env->global_class = generic_class;
    env->global_class.name = "Window";
    env->global_class.flags = JSCLASS_HAS_PRIVATE;
    env->document_class = generic_class;
    env->document_class.name = "HTMLDocument";
    env->body_class = generic_class;
    env->body_class.name = "Body";
    env->navigator_class = generic_class;
    env->navigator_class.name = "Navigator";
    env->location_class = generic_class;
    env->location_class.name = "Location";
    env->screen_class = generic_class;
    env->screen_class.name = "Screen";
    env->image_class = generic_class;
    env->image_class.name = "HTMLImageElement";
    env->form_class = generic_class;
    env->form_class.name = "HTMLFormElement";
    env->mimetype_class = generic_class;
    env->mimetype_class.name = "MimeType";
    env->plugin_class = generic_class;
    env->plugin_class.name = "Plugin";
    env->branch_cnt = 0;
    // init python objects
    if (!(env->listeners=PyDict_New())) {
        return NULL;
    }
    if (!(env->scheduled_actions=PyList_New(0))) {
        return NULL;
    }
    // init JS engine
    if (!(env->runtime=JS_NewRuntime(500L*1024L))) {
        return shutdown(env, "Could not initialize JS runtime");
    }
    if (!(env->ctx=JS_NewContext(env->runtime, 8192))) {
        return shutdown(env, "Could not initialize JS context");
    }

    // configure JS engine
    JS_SetErrorReporter(env->ctx, &errorReporter);
    JS_SetBranchCallback(env->ctx, &branchCallback);

    // init global object
    if (!(env->global_obj=JS_NewObject(env->ctx, &env->global_class, NULL, NULL))) {
        return shutdown(env, "Could not initialize global object");
    }
    if (JS_InitStandardClasses(env->ctx, env->global_obj)==JS_FALSE) {
        return shutdown(env, "Could not init standard classes");
    }
    if (JS_SetPrivate(env->ctx, env->global_obj, env)==JS_FALSE) {
        return shutdown(env, "Could not set private env var");
    }
    if (JS_DefineProperty(env->ctx, env->global_obj, "self",
                          OBJECT_TO_JSVAL(env->global_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set global self property");
    }
    if (JS_DefineProperty(env->ctx, env->global_obj, "window",
                          OBJECT_TO_JSVAL(env->global_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set global window property");
    }
    if (JS_DefineProperty(env->ctx, env->global_obj, "top",
                          OBJECT_TO_JSVAL(env->global_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set global top property");
    }
    if (JS_DefineProperty(env->ctx, env->global_obj, "parent",
                          OBJECT_TO_JSVAL(env->global_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set global parent property");
    }
    if (JS_DefineProperty(env->ctx, env->global_obj, "onload",
                          JSVAL_NULL, 0, &onloadSetter,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set global onload property");
    }
    if (JS_DefineProperty(env->ctx, env->global_obj, "onunload",
                          JSVAL_NULL, 0, &onunloadSetter,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set global onunload property");
    }
    if (!(history_array=JS_NewArrayObject(env->ctx, 0, 0))) {
        return shutdown(env, "Could not create history array object");
    }
    if (JS_DefineProperty(env->ctx, env->global_obj, "history",
                          OBJECT_TO_JSVAL(history_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set global history property");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "open", &windowOpen, 1,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global open function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "setTimeout",
                           &setTimeout, 2, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global setTimeout function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "setInterval",
                           &setTimeout, 2, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global setInterval function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "clearTimeout",
                           &doNothing, 1, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global clearTimeout function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "clearInterval",
                           &doNothing, 1, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global clearInterval function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "focus", &doNothing,
                           0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global focus function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "blur", &doNothing, 0,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global blur function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "resizeTo", &doNothing,
                           2, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global resizeTo function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "moveTo", &doNothing,
                           2, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global moveTo function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "Image",
                           &imageConstructor, 0,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global Image function");
    }
    if (!JS_DefineFunction(env->ctx, env->global_obj, "wcDebugLog",
                           &wcDebugLog, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set global wcDebugLog function");
    }
    // init location object
    if (!(location_obj=JS_DefineObject(env->ctx, env->global_obj, "location",
                                       &env->location_class, 0,
                                       JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        return shutdown(env, "Could not create location object");
    }
    if (JS_DefineProperty(env->ctx, location_obj, "protocol",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "http:")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set location.protocol property");
    }
    if (JS_DefineProperty(env->ctx, location_obj, "host",
                          JS_GetEmptyStringValue(env->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set location.host property");
    }
    if (JS_DefineProperty(env->ctx, location_obj, "port",
                          INT_TO_JSVAL(80), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set location.port property");
    }
    if (JS_DefineProperty(env->ctx, location_obj, "pathname",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "/")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set location.pathname property");
    }
    if (JS_DefineProperty(env->ctx, location_obj, "hash",
                          JS_GetEmptyStringValue(env->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set location.hash property");
    }
    if (JS_DefineProperty(env->ctx, location_obj, "href",
                          JS_GetEmptyStringValue(env->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set location.href property");
    }
    if (JS_DefineProperty(env->ctx, location_obj, "search",
                          JS_GetEmptyStringValue(env->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set location.search property");
    }
    // init navigator object
    if (!(nav_obj=JS_DefineObject(env->ctx, env->global_obj, "navigator",
                                  &env->navigator_class, 0,
                                  JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        return shutdown(env, "Could not create nav object");
    }
    if (JS_DefineFunction(env->ctx, nav_obj, "javaEnabled", &javaEnabled, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set navigator.javaEnabled property");
    }
    if (JS_DefineProperty(env->ctx, nav_obj, "appCodeName",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "Mozilla")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set navigator.appCodeName property");
    }
    if (JS_DefineProperty(env->ctx, nav_obj, "appName",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "Netscape")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set navigator.appName property");
    }
    if (JS_DefineProperty(env->ctx, nav_obj, "appVersion",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "3.01 (Windows; en-US)")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set navigator.appVersion property");
    }
    if (JS_DefineProperty(env->ctx, nav_obj, "userAgent",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "Mozilla/3.01Gold (Win95; I)")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set navigator.userAgent property");
    }
    if (JS_DefineProperty(env->ctx, nav_obj, "platform",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "Windows")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set navigator.userAgent property");
    }

    // init flash objects
    if (!(mimetypes_array=JS_NewArrayObject(env->ctx, 0, 0))) {
        return shutdown(env, "Could not create mimetypes array object");
    }
    if (JS_DefineProperty(env->ctx, nav_obj, "mimeTypes",
                          OBJECT_TO_JSVAL(mimetypes_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set navigator.mimeTypes property");
    }
    if (!(plugins_array=JS_NewArrayObject(env->ctx, 0, 0))) {
        return shutdown(env, "Could not create plugins array object");
    }
    if (JS_DefineProperty(env->ctx, nav_obj, "plugins",
                          OBJECT_TO_JSVAL(plugins_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set navigator.plugins property");
    }
    if (!(flash_mimetype_obj=JS_DefineObject(env->ctx, mimetypes_array, "application/x-shockwave-flash",
                                             &env->mimetype_class, 0,
                                             JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        return shutdown(env, "Could not create flash mimetype object");
    }
    flash_mimetype_jsval = OBJECT_TO_JSVAL(flash_mimetype_obj);
    if (JS_SetElement(env->ctx, mimetypes_array, 0, &flash_mimetype_jsval)
        ==JS_FALSE) {
        return shutdown(env, "Could not set mimetype array element");
    }
    if (JS_DefineProperty(env->ctx, flash_mimetype_obj, "description",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "Shockwave Flash")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set flash description property");
    }
    if (JS_DefineProperty(env->ctx, flash_mimetype_obj, "type",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "application/x-shockwave-flash")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set flash type property");
    }
    if (JS_DefineProperty(env->ctx, flash_mimetype_obj, "suffixes",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "swf")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set flash suffixes property");
    }
    if (!(flash_plugin_obj=JS_DefineObject(env->ctx, flash_mimetype_obj, "enabledPlugin",
                                           &env->plugin_class, 0,
                                           JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        return shutdown(env, "Could not create flash plugin object");
    }
    flash_plugin_jsval = OBJECT_TO_JSVAL(flash_plugin_obj);
    if (JS_SetElement(env->ctx, plugins_array, 0, &flash_plugin_jsval)
        ==JS_FALSE) {
        return shutdown(env, "Could not set plugin array element");
    }
    if (JS_DefineProperty(env->ctx, flash_plugin_obj, "name",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "Shockwave Flash")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set enabledPlugin.name property");
    }
    if (JS_DefineProperty(env->ctx, flash_plugin_obj, "description",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "Shockwave Flash 5.0 r50")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set enabledPlugin.description property");
    }
    if (JS_DefineProperty(env->ctx, flash_plugin_obj, "length",
                          INT_TO_JSVAL(1), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set enabledPlugin.length property");
    }
    if (!JS_DefineFunction(env->ctx, flash_plugin_obj, "refresh",
                           &doNothing, 0, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set enabledPlugin.refresh function");
    }

    // init screen object
    if (!(screen_obj=JS_DefineObject(env->ctx, env->global_obj, "screen",
                                     &env->screen_class, 0,
                                     JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        return shutdown(env, "Could not create screen object");
    }
    if (JS_DefineProperty(env->ctx, screen_obj, "width",
                          INT_TO_JSVAL(1024), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set screen.width property");
    }
    if (JS_DefineProperty(env->ctx, screen_obj, "height",
                          INT_TO_JSVAL(768), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set screen.height property");
    }
    if (JS_DefineProperty(env->ctx, screen_obj, "availWidth",
                          INT_TO_JSVAL(1014), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set screen.availWidth property");
    }
    if (JS_DefineProperty(env->ctx, screen_obj, "availHeight",
                          INT_TO_JSVAL(720), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set screen.availHeight property");
    }
    if (JS_DefineProperty(env->ctx, screen_obj, "colorDepth",
                          INT_TO_JSVAL(16), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set screen.colorDepth property");
    }
    if (JS_DefineProperty(env->ctx, screen_obj, "pixelDepth",
                          INT_TO_JSVAL(16), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set screen.pixelDepth property");
    }

    // init frames object
    if (!(frames_obj=JS_NewArrayObject(env->ctx, 0, 0))) {
        return shutdown(env, "Could not create frames object");
    }
    if (JS_DefineProperty(env->ctx, env->global_obj, "frames",
                          OBJECT_TO_JSVAL(frames_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set global frames property");
    }

    // init document object
    if (!(env->doc_obj=JS_DefineObject(env->ctx, env->global_obj, "document",
                                       &env->document_class, 0,
                                       JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        return shutdown(env, "Could not create document object");
    }
    if (JS_DefineProperty(env->ctx, env->doc_obj, "cookie",
                          JS_GetEmptyStringValue(env->ctx), &cookieGetter, &cookieSetter,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set document.cookie property");
    }
    if (JS_DefineProperty(env->ctx, env->doc_obj, "location",
                          OBJECT_TO_JSVAL(location_obj), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set document.location property");
    }
    if (JS_DefineProperty(env->ctx, env->doc_obj, "domain",
                          JS_GetEmptyStringValue(env->ctx), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set document.domain property");
    }
    if (JS_DefineProperty(env->ctx, env->doc_obj, "referrer",
                          STRING_TO_JSVAL(JS_NewStringCopyZ(env->ctx, "http://imadoofus/")), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set document.referrer property");
    }
    if (!(images_array=JS_NewArrayObject(env->ctx, 0, 0))) {
        return shutdown(env, "Could not create images array");
    }
    if (JS_DefineProperty(env->ctx, env->doc_obj, "images",
                          OBJECT_TO_JSVAL(images_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_PERMANENT|JSPROP_READONLY)
        ==JS_FALSE) {
        return shutdown(env, "Could not set document.images property");
    }
    if (!JS_DefineFunction(env->ctx, env->doc_obj, "write", &documentWrite, 1,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set document.write function");
    }
    if (!JS_DefineFunction(env->ctx, env->doc_obj, "writeln",
                           &documentWriteln, 1, JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set document.writeln function");
    }
    if (!JS_DefineFunction(env->ctx, env->doc_obj, "open", &doNothing, 0,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set document.open function");
    }
    if (!JS_DefineFunction(env->ctx, env->doc_obj, "close", &doNothing, 0,
                           JSPROP_ENUMERATE|JSPROP_PERMANENT)) {
        return shutdown(env, "Could not set document.close function");
    }

    // init body object
    if (!(body_obj=JS_DefineObject(env->ctx, env->doc_obj, "body",
                                   &env->body_class, 0,
                                   JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT))) {
        return shutdown(env, "Could not create document.body object");
    }
    if (JS_DefineProperty(env->ctx, body_obj, "clientHeight",
                          INT_TO_JSVAL(768), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set body.clientHeight property");
    }
    if (JS_DefineProperty(env->ctx, body_obj, "clientWidth",
                          INT_TO_JSVAL(1024), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set body.clientWidth property");
    }

    // init form array
    if (!(env->form_array=JS_NewArrayObject(env->ctx, 0, 0))) {
        return shutdown(env, "Could not create form array");
    }
    if (JS_DefineProperty(env->ctx, env->doc_obj, "forms",
                          OBJECT_TO_JSVAL(env->form_array), 0, 0,
                          JSPROP_ENUMERATE|JSPROP_READONLY|JSPROP_PERMANENT)
        ==JS_FALSE) {
        return shutdown(env, "Could not set doc forms property");
    }

    return (PyObject*)env;
}


/* destroy */
static void JSEnv_dealloc(PyObject* self) {
    JSEnvObject* env = (JSEnvObject*)self;
    destroy(env);
    Py_DECREF(env->listeners);
    PyObject_Del(env);
}


/* public JSEnv object methods */
static PyMethodDef JSEnv_methods[] = {
    {"attachListener", (PyCFunction)JSEnv_attachListener, METH_VARARGS, "attach listener"},
    {"detachListener", (PyCFunction)JSEnv_detachListener, METH_VARARGS, "detach listener"},
    {"executeScript", (PyCFunction)JSEnv_executeScript, METH_VARARGS, "execute script"},
    {"executeScriptAsFunction", (PyCFunction)JSEnv_executeScriptAsFunction, METH_VARARGS, "execute script as function"},
    {"addForm", (PyCFunction)JSEnv_addForm, METH_VARARGS, "add form element"},
    {NULL, NULL, 0, NULL}
};


static PyObject* JSEnv_getattr(PyObject* self, char* name) {
    return Py_FindMethod(JSEnv_methods, self, name);
}


/* object type definition */
static PyTypeObject JSEnvType = {
    PyObject_HEAD_INIT(NULL)
    0, /* ob_size */
    "JSEnv", /* tp_name */
    sizeof(JSEnvObject), /* tp_size */
    0, /* tp_itemsize */
    /* methods */
    JSEnv_dealloc, /* tp_dealloc */
    0,          /* tp_print */
    JSEnv_getattr, /* tp_getattr */
    0,          /* tp_setattr */
    0,          /* tp_compare */
    0,          /* tp_repr */
    0,          /* tp_as_number */
    0,          /* tp_as_sequence */
    0,          /* tp_as_mapping */
    0,          /* tp_hash */
};


/* python module interface */
static PyMethodDef jslib_methods[] = {
    {"new_jsenv", JSEnv_new, METH_VARARGS, "Create a new JSEnv object."},
    {NULL, NULL}
};


/* initialization of the module */
DL_EXPORT(void) initjslib(void) {
    PyObject *m, *d;
    JSEnvType.ob_type = &PyType_Type;
    m = Py_InitModule("jslib", jslib_methods);
    d = PyModule_GetDict(m);
    JSError = PyErr_NewException("jslib.error", NULL, NULL);
    PyDict_SetItemString(d, "error", JSError);
}

#ifdef WIN32
#undef XP_PC
#else
#undef XP_UNIX
#endif
