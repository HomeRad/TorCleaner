%{
/* Copyright (C) 2000-2003  Bastian Kleineidam

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
 Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
*/
/* SAX parser, optimized for WebCleaner */
#include "htmlsax.h"
#include <string.h>
#include <stdio.h>

/* bison type definitions */
#define YYSTYPE PyObject*
#define YYPARSE_PARAM scanner
#define YYLEX_PARAM scanner
extern int yylex(YYSTYPE* yylvalp, void* scanner);
extern int htmllexInit (void** scanner, UserData* data);
extern int htmllexDebug (void** scanner, int debug);
extern int htmllexStart (void* scanner, UserData* data, const char* s, int slen);
extern int htmllexStop (void* scanner, UserData* data);
extern int htmllexDestroy (void* scanner);
extern void* yyget_extra(void*);
#define YYERROR_VERBOSE 1

/* standard error reporting, indicating an internal error */
static int yyerror (char* msg) {
    fprintf(stderr, "htmlsax: internal parse error: %s\n", msg);
    return 0;
}

/* wc.parser.resolve_entities */
static PyObject* resolve_entities;

/* macros for easier scanner state manipulation */

/* test whether tag does not need an HTML end tag */
#define NO_HTML_END_TAG(tag) !(strcmp(tag, "area")==0 || \
    strcmp(tag, "base")==0 || \
    strcmp(tag, "basefont")==0 || \
    strcmp(tag, "br")==0 || \
    strcmp(tag, "col")==0 || \
    strcmp(tag, "frame")==0 || \
    strcmp(tag, "hr")==0 || \
    strcmp(tag, "img")==0 || \
    strcmp(tag, "input")==0 || \
    strcmp(tag, "isindex")==0 || \
    strcmp(tag, "link")==0 || \
    strcmp(tag, "meta")==0 || \
    strcmp(tag, "param")==0)

/* clear buffer b, returning NULL on error */
#define CLEAR_BUF(b) \
    b = PyMem_Resize(b, char, 1); \
    if (b==NULL) return NULL; \
    (b)[0] = '\0'

#define CHECK_ERROR(ud, label) \
if (ud->error && PyObject_HasAttrString(ud->handler, "error")==1) { \
	callback = PyObject_GetAttrString(ud->handler, "error"); \
	if (!callback) { error=1; goto label; } \
	result = PyObject_CallFunction(callback, "O", ud->error); \
	if (!result) { error=1; goto label; } \
    }

/* generic callback macro */
#define CALLBACK(ud, attr, format, arg, label) \
    if (PyObject_HasAttrString(ud->handler, attr)==1) { \
	callback = PyObject_GetAttrString(ud->handler, attr); \
	if (callback==NULL) { error=1; goto label; } \
	result = PyObject_CallFunction(callback, format, arg); \
	if (result==NULL) { error=1; goto label; } \
	Py_DECREF(callback); \
	Py_DECREF(result); \
        callback=result=NULL; \
    }

/* parser type definition */
typedef struct {
    PyObject_HEAD
    UserData* userData;
    void* scanner;
} parser_object;

staticforward PyTypeObject parser_type;

/* use Pythons memory management */
#define malloc PyMem_Malloc
#define realloc PyMem_Realloc
#define free PyMem_Free

%}

/* parser options */
%verbose
%debug
%defines
%output="htmlparse.c"
%pure_parser

%token T_WAIT
%token T_ERROR
%token T_TEXT
%token T_ELEMENT_START
%token T_ELEMENT_START_END
%token T_ELEMENT_END
%token T_SCRIPT
%token T_STYLE
%token T_PI
%token T_COMMENT
%token T_CDATA
%token T_DOCTYPE

/* the finish_ labels are for error recovery */
%%

elements: element {}
    | elements element {}
    ;

element: T_WAIT { YYACCEPT; /* wait for more lexer input */ }
| T_ERROR
{
    /* an error occured in the scanner, the python exception must be set */
    UserData* ud = yyget_extra(scanner);
    PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    YYABORT;
}
| T_ELEMENT_START
{
    /* $1 is a PyTuple (<tag>, <attrs>)
       <tag> is a PyString, <attrs> is a PyDict */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    PyObject* tag = PyTuple_GET_ITEM($1, 0);
    PyObject* attrs = PyTuple_GET_ITEM($1, 1);
    int error = 0;
    if (!tag || !attrs) { error = 1; goto finish_start; }
    if (PyObject_HasAttrString(ud->handler, "startElement")==1) {
	callback = PyObject_GetAttrString(ud->handler, "startElement");
	if (!callback) { error=1; goto finish_start; }
	result = PyObject_CallFunction(callback, "OO", tag, attrs);
	if (!result) { error=1; goto finish_start; }
	Py_DECREF(callback);
        Py_DECREF(result);
        callback=result=NULL;
    }
    CHECK_ERROR(ud, finish_start);
finish_start:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_XDECREF(tag);
    Py_XDECREF(attrs);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_ELEMENT_START_END
{
    /* $1 is a PyTuple (<tag>, <attrs>)
       <tag> is a PyString, <attrs> is a PyDict */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    PyObject* tag = PyTuple_GET_ITEM($1, 0);
    PyObject* attrs = PyTuple_GET_ITEM($1, 1);
    int error = 0;
    char* tagname;
    if (!tag || !attrs) { error = 1; goto finish_start_end; }
    if (PyObject_HasAttrString(ud->handler, "startElement")==1) {
	callback = PyObject_GetAttrString(ud->handler, "startElement");
	if (!callback) { error=1; goto finish_start_end; }
	result = PyObject_CallFunction(callback, "OO", tag, attrs);
	if (!result) { error=1; goto finish_start_end; }
	Py_DECREF(callback);
        Py_DECREF(result);
        callback=result=NULL;
    }
    tagname = PyString_AS_STRING(tag);
    if (PyObject_HasAttrString(ud->handler, "endElement")==1 &&
	NO_HTML_END_TAG(tagname)) {
	callback = PyObject_GetAttrString(ud->handler, "endElement");
	if (callback==NULL) { error=1; goto finish_start_end; }
	result = PyObject_CallFunction(callback, "O", tag);
	if (result==NULL) { error=1; goto finish_start_end; }
	Py_DECREF(callback);
        Py_DECREF(result);
        callback=result=NULL;
    }
    CHECK_ERROR(ud, finish_start_end);
finish_start_end:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_XDECREF(tag);
    Py_XDECREF(attrs);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_ELEMENT_END
{
    /* $1 is a PyString */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    char* tagname = PyString_AS_STRING($1);
    if (PyObject_HasAttrString(ud->handler, "endElement")==1 &&
	NO_HTML_END_TAG(tagname)) {
	callback = PyObject_GetAttrString(ud->handler, "endElement");
	if (callback==NULL) { error=1; goto finish_end; }
	result = PyObject_CallFunction(callback, "O", $1);
	if (result==NULL) { error=1; goto finish_end; }
	Py_DECREF(callback);
	Py_DECREF(result);
        callback=result=NULL;
    }
    CHECK_ERROR(ud, finish_end);
finish_end:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_COMMENT
{
    /* $1 is a PyString */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    CALLBACK(ud, "comment", "O", $1, finish_comment);
    CHECK_ERROR(ud, finish_comment);
finish_comment:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_PI
{
    /* $1 is a PyString */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    CALLBACK(ud, "pi", "O", $1, finish_pi);
    CHECK_ERROR(ud, finish_pi);
finish_pi:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_CDATA
{
    /* $1 is a PyString */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    CALLBACK(ud, "cdata", "O", $1, finish_cdata);
    CHECK_ERROR(ud, finish_cdata);
finish_cdata:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_DOCTYPE
{
    /* $1 is a PyString */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    CALLBACK(ud, "doctype", "O", $1, finish_doctype);
    CHECK_ERROR(ud, finish_doctype);
finish_doctype:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_SCRIPT
{
    /* $1 is a PyString */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    CALLBACK(ud, "characters", "O", $1, finish_script);
    CALLBACK(ud, "endElement", "s", "script", finish_script);
    CHECK_ERROR(ud, finish_script);
finish_script:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_STYLE
{
    /* $1 is a PyString */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    CALLBACK(ud, "characters", "O", $1, finish_style);
    CALLBACK(ud, "endElement", "s", "style", finish_style);
    CHECK_ERROR(ud, finish_style);
finish_style:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_TEXT
{
    /* $1 is a PyString */
    /* Remember this is also called as a lexer error fallback */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    CALLBACK(ud, "characters", "O", $1, finish_characters);
    CHECK_ERROR(ud, finish_characters);
finish_characters:
    Py_XDECREF(ud->error);
    ud->error = NULL;
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
;

%%

/* disable python memory interface */
#undef malloc
#undef realloc
#undef free

/* create parser */
static PyObject* htmlsax_parser_new(PyObject* self, PyObject* args) {
    PyObject* handler;
    parser_object* p;
    if (!PyArg_ParseTuple(args, "O", &handler)) {
	return NULL;
    }
    p = PyObject_New(parser_object, &parser_type);
    if (!p) {
	PyErr_SetString(PyExc_TypeError, "Allocating parser object failed");
	return NULL;
    }
    Py_INCREF(handler);
    /* reset userData */
    p->userData = PyMem_New(UserData, sizeof(UserData));
    p->userData->handler = handler;
    p->userData->buf = NULL;
    CLEAR_BUF(p->userData->buf);
    p->userData->nextpos = 0;
    p->userData->bufpos = 0;
    p->userData->tmp_buf = NULL;
    CLEAR_BUF(p->userData->tmp_buf);
    p->userData->tmp_tag = p->userData->tmp_attrname =
	p->userData->tmp_attrval = p->userData->tmp_attrs =
	p->userData->lexbuf = NULL;
    p->userData->resolve_entities = resolve_entities;
    p->userData->exc_type = NULL;
    p->userData->exc_val = NULL;
    p->userData->exc_tb = NULL;
    p->userData->error = NULL;
    p->scanner = NULL;
    htmllexInit(&(p->scanner), p->userData);
    return (PyObject*) p;
}


static void parser_dealloc(PyObject* self) {
    parser_object* p = (parser_object*)self;
    htmllexDestroy(p->scanner);
    Py_DECREF(p->userData->handler);
    PyMem_Del(p->userData->buf);
    PyMem_Del(p->userData->tmp_buf);
    PyMem_Del(p->userData);
    PyObject_Del(p);
}


static PyObject* parser_flush(PyObject* self, PyObject* args) {
    /* flush parser buffers */
    int res = 0;
    parser_object* p = (parser_object*)self;
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
        return NULL;
    }
    /* reset parser variables */
    CLEAR_BUF(p->userData->tmp_buf);
    Py_XDECREF(p->userData->tmp_tag);
    Py_XDECREF(p->userData->tmp_attrs);
    Py_XDECREF(p->userData->tmp_attrval);
    Py_XDECREF(p->userData->tmp_attrname);
    p->userData->tmp_tag = p->userData->tmp_attrs =
	p->userData->tmp_attrval = p->userData->tmp_attrname = NULL;
    p->userData->bufpos = 0;
    if (strlen(p->userData->buf)) {
        int error = 0;
	PyObject* s = PyString_FromString(p->userData->buf);
	PyObject* callback = NULL;
	PyObject* result = NULL;
	/* reset buffer */
	CLEAR_BUF(p->userData->buf);
	if (s==NULL) { error=1; goto finish_flush; }
	if (PyObject_HasAttrString(p->userData->handler, "characters")==1) {
	    callback = PyObject_GetAttrString(p->userData->handler, "characters");
	    if (callback==NULL) { error=1; goto finish_flush; }
	    result = PyObject_CallFunction(callback, "O", s);
	    if (result==NULL) { error=1; goto finish_flush; }
	}
    finish_flush:
	Py_XDECREF(callback);
	Py_XDECREF(result);
	Py_XDECREF(s);
	if (error==1) {
	    return NULL;
	}
    }
    return Py_BuildValue("i", res);
}


/* feed a chunk of data to the parser */
static PyObject* parser_feed(PyObject* self, PyObject* args) {
    /* set up the parse string */
    int slen = 0;
    char* s = NULL;
    parser_object* p = (parser_object*)self;
    if (!PyArg_ParseTuple(args, "t#", &s, &slen)) {
	PyErr_SetString(PyExc_TypeError, "string arg required");
	return NULL;
    }
    /* parse */
    if (htmllexStart(p->scanner, p->userData, s, slen)!=0) {
	PyErr_SetString(PyExc_MemoryError, "could not start scanner");
 	return NULL;
    }
    if (yyparse(p->scanner)!=0) {
        if (p->userData->exc_type!=NULL) {
            /* note: we give away these objects, so don't decref */
            PyErr_Restore(p->userData->exc_type,
        		  p->userData->exc_val,
        		  p->userData->exc_tb);
        }
        htmllexStop(p->scanner, p->userData);
        return NULL;
    }
    if (htmllexStop(p->scanner, p->userData)!=0) {
	PyErr_SetString(PyExc_MemoryError, "could not stop scanner");
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}


/* reset the parser. This will erase all buffered data! */
static PyObject* parser_reset(PyObject* self, PyObject* args) {
    parser_object* p = (parser_object*)self;
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
	return NULL;
    }
    if (htmllexDestroy(p->scanner)!=0) {
        PyErr_SetString(PyExc_MemoryError, "could not destroy scanner data");
        return NULL;
    }
    /* reset buffer */
    CLEAR_BUF(p->userData->buf);
    CLEAR_BUF(p->userData->tmp_buf);
    p->userData->bufpos =
        p->userData->nextpos = 0;
    p->userData->tmp_tag = p->userData->tmp_attrs =
        p->userData->tmp_attrval = p->userData->tmp_attrname = NULL;
    p->scanner = NULL;
    if (htmllexInit(&(p->scanner), p->userData)!=0) {
        PyErr_SetString(PyExc_MemoryError, "could not initialize scanner data");
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}


/* set the debug level, if its >0, debugging is on, =0 means off */
static PyObject* parser_debug(PyObject* self, PyObject* args) {
    int debug;
    parser_object* p = (parser_object*)self;
    if (!PyArg_ParseTuple(args, "i", &debug)) {
        return NULL;
    }
    yydebug = debug;
    debug = htmllexDebug(&(p->scanner), debug);
    return PyInt_FromLong((long)debug);
}


/* type interface */
static PyMethodDef parser_methods[] = {
    /* incremental parsing */
    {"feed",  parser_feed, METH_VARARGS, "feed data to parse incremental"},
    /* reset the parser (no flushing) */
    {"reset", parser_reset, METH_VARARGS, "reset the parser (no flushing)"},
    /* flush the parser buffers */
    {"flush", parser_flush, METH_VARARGS, "flush parser buffers"},
    /* set debugging on/off */
    {"debug", parser_debug, METH_VARARGS, "set debug level"},
    {NULL, NULL, 0, NULL}
};


static PyObject* parser_getattr(PyObject* self, char* name) {
    return Py_FindMethod(parser_methods, self, name);
}


static PyTypeObject parser_type = {
    PyObject_HEAD_INIT(NULL)
    0, /* ob_size */
    "parser", /* tp_name */
    sizeof(parser_object), /* tp_size */
    0, /* tp_itemsize */
    /* methods */
    parser_dealloc, /* tp_dealloc */
    0, /* tp_print */
    parser_getattr, /* tp_getattr */
    0,          /* tp_setattr */
    0,          /*tp_compare*/
    0,          /*tp_repr*/
    0,          /*tp_as_number*/
    0,          /*tp_as_sequence*/
    0,          /*tp_as_mapping*/
    0,          /*tp_hash */
};


/* python module interface */
static PyMethodDef htmlsax_methods[] = {
    {"new_parser", htmlsax_parser_new, METH_VARARGS,
     "Create a new HTML parser object."},
    {NULL, NULL, 0, NULL}
};


/* initialization of the htmlsaxhtmlop module */
DL_EXPORT(void) inithtmlsax(void) {
    PyObject* m;
    Py_InitModule("htmlsax", htmlsax_methods);
    if (!(m = PyImport_ImportModule("wc.parser")))
        return;
    if (!(resolve_entities = PyObject_GetAttrString(m, "resolve_entities")))
        return;
}
