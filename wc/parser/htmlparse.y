/* bla */
%{
/* SAX parser, optimized for WebCleaner */
#include <malloc.h>
#include <string.h>
#include <stdio.h>
#include "htmlsax.h"

#define YYSTYPE PyObject*
#define YYPARSE_PARAM scanner
#define YYLEX_PARAM scanner
extern int htmllexInit(void** scanner, void* data);
extern int htmllexStart(void* scanner, const char* s, int slen);
extern int htmllexStop(void* scanner);
extern int yylex(YYSTYPE* yylvalp, void* scanner);
extern void* yyget_extra(void*);
extern void* yyget_lval(void*);
#define YYERROR_VERBOSE 1
extern char* stpcpy(char* src, const char* dest);
int yyerror(char* msg);
PyObject* quote_string (PyObject* val);

/* parser type definition */
typedef struct {
    PyObject_HEAD
    UserData* userData;
    void* scanner;
} parser_object;

staticforward PyTypeObject parser_type;

%}

/* parser options */
%debug
%verbose
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
%token T_PI
%token T_COMMENT
%token T_CDATA
%token T_DOCTYPE

%%

elements: element {}
    | elements element {}
    ;

element: T_WAIT { YYACCEPT; /* wait for more lexer input */ }
| T_ERROR
{
    /* a python error occured in the scanner */
    UserData* ud = yyget_extra(scanner);
    PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    YYABORT;
}
| T_ELEMENT_START
{
    /* $1 is a tuple (<tag>, <attrs>) */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    PyObject* ltag = PyTuple_GET_ITEM($1, 0);
    PyObject* attrs = PyTuple_GET_ITEM($1, 1);
    int error = 0;
    if (!ltag || !attrs) { error = 1; goto finish_start; }
    if (PyObject_HasAttrString(ud->handler, "startElement")==1) {
	callback = PyObject_GetAttrString(ud->handler, "startElement");
	if (!callback) { error=1; goto finish_start; }
	result = PyObject_CallFunction(callback, "OO", ltag, attrs);
	if (!result) { error=1; goto finish_start; }
    }
finish_start:
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_XDECREF(ltag);
    Py_XDECREF(attrs);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_ELEMENT_START_END
{
    /* $1 is a tuple (<tag>, <attrs>) */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    PyObject* ltag = PyTuple_GET_ITEM($1, 0);
    PyObject* attrs = PyTuple_GET_ITEM($1, 1);
    int error = 0;
    if (!ltag || !attrs) { error = 1; goto finish_start_end; }
    if (PyObject_HasAttrString(ud->handler, "startElement")==1) {
	callback = PyObject_GetAttrString(ud->handler, "startElement");
	if (!callback) { error=1; goto finish_start_end; }
	result = PyObject_CallFunction(callback, "OO", ltag, attrs);
	if (!result) { error=1; goto finish_start_end; }
	Py_DECREF(callback);
        Py_DECREF(result);
        callback=result=NULL;
    }
    if (PyObject_HasAttrString(ud->handler, "endElement")==1) {
	callback = PyObject_GetAttrString(ud->handler, "endElement");
	if (callback==NULL) { error=1; goto finish_start_end; }
	result = PyObject_CallFunction(callback, "O", ltag);
	if (result==NULL) { error=1; goto finish_start_end; }
    }
finish_start_end:
    Py_XDECREF(callback);
    Py_XDECREF(result);
    Py_XDECREF(ltag);
    Py_XDECREF(attrs);
    Py_DECREF($1);
    if (error) {
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	YYABORT;
    }
}
| T_ELEMENT_END
{
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (PyObject_HasAttrString(ud->handler, "endElement")==1) {
	callback = PyObject_GetAttrString(ud->handler, "endElement");
	if (callback==NULL) { error=1; goto finish_end; }
	result = PyObject_CallFunction(callback, "O", $1);
	if (result==NULL) { error=1; goto finish_end; }
    }
finish_end:
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
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (PyObject_HasAttrString(ud->handler, "comment")==1) {
	callback = PyObject_GetAttrString(ud->handler, "comment");
	if (callback==NULL) { error=1; goto finish_comment; }
	result = PyObject_CallFunction(callback, "O", $1);
	if (result==NULL) { error=1; goto finish_comment; }
    }
finish_comment:
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
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (PyObject_HasAttrString(ud->handler, "pi")==1) {
	callback = PyObject_GetAttrString(ud->handler, "pi");
	if (callback==NULL) { error=1; goto finish_pi; }
	result = PyObject_CallFunction(callback, "O", $1);
	if (result==NULL) { error=1; goto finish_pi; }
    }
finish_pi:
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
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (PyObject_HasAttrString(ud->handler, "cdata")==1) {
	callback = PyObject_GetAttrString(ud->handler, "cdata");
	if (callback==NULL) { error=1; goto finish_cdata; }
	result = PyObject_CallFunction(callback, "O", $1);
	if (result==NULL) { error=1; goto finish_cdata; }
    }
finish_cdata:
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
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (PyObject_HasAttrString(ud->handler, "doctype")==1) {
	callback = PyObject_GetAttrString(ud->handler, "doctype");
	if (callback==NULL) { error=1; goto finish_doctype; }
	result = PyObject_CallFunction(callback, "O", $1);
	if (result==NULL) { error=1; goto finish_doctype; }
    }
finish_doctype:
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
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (PyObject_HasAttrString(ud->handler, "characters")==1) {
	callback = PyObject_GetAttrString(ud->handler, "characters");
	if (callback==NULL) { error=1; goto finish_script; }
	result = PyObject_CallFunction(callback, "O", $1);
	if (result==NULL) { error=1; goto finish_script; }
	Py_DECREF(callback);
	Py_DECREF(result);
        callback=result=NULL;
    }
    if (PyObject_HasAttrString(ud->handler, "endElement")==1) {
	callback = PyObject_GetAttrString(ud->handler, "endElement");
	if (callback==NULL) { error=1; goto finish_script; }
	result = PyObject_CallFunction(callback, "s", "script");
	if (result==NULL) { error=1; goto finish_script; }
    }
finish_script:
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
    /* Remember this is also called as a lexer error fallback */
    UserData* ud = yyget_extra(scanner);
    PyObject* callback = NULL;
    PyObject* result = NULL;
    int error = 0;
    if (PyObject_HasAttrString(ud->handler, "characters")==1) {
	callback = PyObject_GetAttrString(ud->handler, "characters");
	if (callback==NULL) { error=1; goto finish_characters; }
	result = PyObject_CallFunction(callback, "O", $1);
	if (result==NULL) { error=1; goto finish_characters; }
    }
finish_characters:
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

/* create parser */
static PyObject* htmlsax_parser(PyObject* self, PyObject* args) {
    PyObject* handler;
    parser_object* p;
    if (!PyArg_ParseTuple(args, "O", &handler)) {
	PyErr_SetString(PyExc_TypeError, "SAX2 handler object arg required");
	return NULL;
    }

    if (!(p=PyObject_NEW(parser_object, &parser_type))) {
	PyErr_SetString(PyExc_TypeError, "Allocating parser object failed");
	return NULL;
    }
    p->userData = PyMem_New(UserData, sizeof(UserData));
    p->userData->handler = handler;
    p->userData->buf = PyMem_New(char, 1);
    if (!p->userData->buf) return PyErr_NoMemory();
    p->userData->buf[0] = '\0';
    p->userData->tmp = PyMem_New(char, 1);
    if (!p->userData->tmp) return PyErr_NoMemory();
    p->userData->tmp[0] = '\0';
    p->userData->exc_type = NULL;
    p->userData->exc_val = NULL;
    p->userData->exc_tb = NULL;
    p->scanner = NULL;
    htmllexInit(&(p->scanner), p->userData);
    return (PyObject*) p;
}


static void parser_dealloc(parser_object* self)
{
    PyMem_Del(self->userData);
    PyMem_DEL(self);
}


static PyObject* parser_flush(parser_object* self, PyObject* args) {
    /* flush parser buffers */
    int res=0, error;
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
        return NULL;
    }
    if (self->userData->buf) {
	PyObject* s = PyString_FromString(self->userData->buf);
	PyObject* callback = NULL;
	PyObject* result = NULL;
	if (s==NULL) return NULL;
	if (PyObject_HasAttrString(self->userData->handler, "characters")==1) {
	    callback = PyObject_GetAttrString(self->userData->handler, "characters");
	    if (callback==NULL) return NULL;
	    result = PyObject_CallFunction(callback, "O", s);
	    if (result==NULL) return NULL;
	}
	Py_DECREF(callback);
	Py_DECREF(result);
	Py_DECREF(s);
    }
    htmllexStop(self->scanner);
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;
    error = 0;
    if (error!=0) {
        if (self->userData->exc_type!=NULL) {
            /* note: we give away these objects, so dont decref */
            PyErr_Restore(self->userData->exc_type,
        		  self->userData->exc_val,
        		  self->userData->exc_tb);
        }
        return NULL;
    }
    return Py_BuildValue("i", res);
}


/* feed a chunk of data to the parser */
static PyObject* parser_feed(parser_object* self, PyObject* args) {
    /* set up the parse string */
    int slen;
    char* s;
    if (!PyArg_ParseTuple(args, "t#", &s, &slen)) {
	PyErr_SetString(PyExc_TypeError, "string arg required");
	return NULL;
    }

    /* reset error state */
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;
    
    /* parse */
    htmllexStart(self->scanner, s, slen);
    yyparse(self->scanner);
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* parser_reset(parser_object* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
	return NULL;
    }
    htmllexStop(self->scanner);
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;
    self->scanner = NULL;
    htmllexInit(&(self->scanner), self->userData);
    Py_INCREF(Py_None);
    return Py_None;
}


/* type interface */

static PyMethodDef parser_methods[] = {
    /* incremental parsing */
    {"feed",  (PyCFunction) parser_feed, METH_VARARGS},
    /* reset the parser (no flushing) */
    {"reset", (PyCFunction) parser_reset, METH_VARARGS},
    /* flush the parser buffers */
    {"flush", (PyCFunction) parser_flush, METH_VARARGS},
    {NULL, NULL}
};


static PyObject* parser_getattr(parser_object* self, char* name) {
    return Py_FindMethod(parser_methods, (PyObject*) self, name);
}


statichere PyTypeObject parser_type = {
    PyObject_HEAD_INIT(NULL)
    0, /* ob_size */
    "parser", /* tp_name */
    sizeof(parser_object), /* tp_size */
    0, /* tp_itemsize */
    /* methods */
    (destructor)parser_dealloc, /* tp_dealloc */
    0, /* tp_print */
    (getattrfunc)parser_getattr, /* tp_getattr */
    0 /* tp_setattr */
};


/* python module interface */

static PyMethodDef htmlsax_methods[] = {
    {"parser", htmlsax_parser, METH_VARARGS},
    {NULL, NULL}
};


/* initialization of the htmlsaxhtmlop module */

void inithtmlsax(void) {
    Py_InitModule("htmlsax", htmlsax_methods);
    yydebug = 1;
}

int yyerror (char* msg) {
    fprintf(stderr, "htmlsax: error: %s\n", msg);
    return 0;
}

/* Find out if and how we must quote the value as an HTML attribute.
 - quote if it contains white space or <>
 - quote with " if it contains '
 - quote with ' if it contains "

 val is a Python String object
*/
PyObject* quote_string (PyObject* val) {
    char* quote = NULL;
    int len = PyString_GET_SIZE(val);
    char* internal = PyString_AS_STRING(val);
    int i;
    PyObject* prefix;
    for (i=0; i<len; i++) {
	if (isspace(internal[i]) && !quote) {
            quote = "\"";
	}
	else if (internal[i]=='\'') {
	    quote = "\"";
            break;
	}
	else if (internal[i]=='"') {
	    quote = "'";
            break;
	}
    }
    if (quote==NULL) {
        return val;
    }
    // quote suffix
    if ((prefix = PyString_FromString(quote))==NULL) return NULL;
    PyString_Concat(&val, prefix);
    if (val==NULL) {
        Py_DECREF(prefix);
	return NULL;
    }
    // quote prefix
    PyString_ConcatAndDel(&prefix, val);
    if (prefix==NULL) {
        Py_DECREF(val);
	return NULL;
    }
    return prefix;
}
