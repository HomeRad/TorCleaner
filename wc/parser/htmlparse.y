%{
/* SAX parser, optimized for WebCleaner */
#include <malloc.h>
#include <string.h>
#include <stdio.h>
#include "Python.h"

/* require Python >= 2.0 */
#ifndef PY_VERSION_HEX
#error please install Python >= 2.0
#endif

#if PY_VERSION_HEX < 0x02000000
#error please install Python >= 2.0
#endif

#define YYSTYPE PyObject*
#define YYPARSE_PARAM scanner
extern int yylex_init(void** scanner);
extern int yy_scan_bytes(const char* s, int slen, void* scanner);
extern int yylex_destroy(void* scanner);
extern int yylex(void* scanner);
extern void yyerror(char *msg);

/* user_data type for SAX calls */
typedef struct {
    /* the Python SAX class instance */
    PyObject* handler;
    /* error flag */
    int error;
    /* stored Python exception (if error occurred) */
    PyObject* exc_type;
    PyObject* exc_val;
    PyObject* exc_tb;
} UserData;


/* parser type definition */
typedef struct {
    PyObject_HEAD
    UserData* userData;
} parser_object;


staticforward PyTypeObject parser_type;

%}

/* parser options */
%debug
%verbose
%defines
%output="htmlparse.c"
%pure_parser

%token T_TEXT
%token T_EOF
%token T_COMMENT_START
%token T_COMMENT_END
%token T_ANGLE_OPEN
%token T_ANGLE_CLOSE
%token T_ANGLE_END_CLOSE
%token T_ANGLE_END_OPEN
%token T_NAME
%token T_EQUAL
%token T_VALUE
%token T_STRING
%token T_PI_OPEN
%token T_PI_CLOSE
%token T_CDATA_START
%token T_CDATA_END
%token T_DOCTYPE_START

%%

elements: element {}
    | elements element {}
    ;


element: element_start {}
   | element_end   {}   /* HTML may or may not have these. */
   | comment       {}
   | pi            {}
   | cdata         {}
   | doctype       {}
   | T_TEXT { printf("XXX element text\n"); }
   | T_EOF {}
   ;


comment: T_COMMENT_START comment_text T_COMMENT_END
    { printf("XXX comment\n"); }
    ;


comment_text: T_TEXT { $$ = $1; }
    | comment_text T_TEXT
    {
        PyString_ConcatAndDel(&$1, $2);
        $$ = $1;
    }
    ;


element_start: T_ANGLE_OPEN T_NAME attributes angle_end
    { printf("XXX element_start\n"); }
    ;


/* handle both normal and empty tags */
angle_end: T_ANGLE_CLOSE {}
    | T_ANGLE_END_CLOSE {}
    ;


element_end: T_ANGLE_END_OPEN T_NAME T_ANGLE_CLOSE
    { printf("XXX element_end\n"); }
    ;


/* return type: a Python dictionary with HTML attributes*/
attributes: /* empty */ {
        PyObject* dict = PyDict_New();
        // XXX error check
        $$ = dict;
    }
    | attribute attributes
    {
        PyObject* name = PyTuple_GET_ITEM($1, 0);
        PyObject* val = PyTuple_GET_ITEM($1, 1);
        PyDict_SetItem($2, name, val);
        $$ = $2;
    }
    ;


/* return type: a Python tuple (name, value).
 * value can be None
 * value is appropriate quoted (has only quotes if needed)
 */
attribute: T_NAME T_EQUAL T_VALUE T_STRING
    {
        PyObject* lname = PyObject_CallMethod($1, "lower", NULL);
        PyObject* tup = Py_BuildValue("(ss)", lname, $3);
        // XXX error
        $$ = tup;
    }
    | T_NAME T_EQUAL T_STRING
    {
        PyObject* lname = PyObject_CallMethod($1, "lower", NULL);
        PyObject* tup = Py_BuildValue("(ss)", lname, $3);
        // XXX error
        $$ = tup;
    }
    | T_NAME T_EQUAL T_NAME
    {
        PyObject* lname = PyObject_CallMethod($1, "lower", NULL);
        PyObject* tup = Py_BuildValue("(ss)", lname, $3);
        // XXX error
        $$ = tup;
    }
    | T_NAME
    {
        PyObject* lname = PyObject_CallMethod($1, "lower", NULL);
        PyObject* tup = Py_BuildValue("(sO)", lname, Py_None);
        // XXX error
        $$ = tup;
    }
    ;


pi: T_PI_OPEN T_NAME T_TEXT T_PI_CLOSE
    {
        printf("XXX pi 1\n");
    }
    | T_PI_OPEN T_NAME T_PI_CLOSE
    {
        printf("XXX pi 2\n");
    }
    ;


/* eventually we want to make this into a pluggable lexer/parser switch. */


cdata: T_CDATA_START text T_CDATA_END {
        printf("XXX cdata\n");
    }
    ;


text: /* empty */ { $$ = PyString_FromString(""); }
    | text T_TEXT
    {
        PyString_ConcatAndDel(&$1, $2);
        $$ = $1;
    }
    ;


/* TODO: This needs to resolve startEntity, DeclHandlers etc. For now just report TEXT */
doctype: T_DOCTYPE_START T_TEXT T_ANGLE_CLOSE
    {
        printf("XXX doctype\n");
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
	return NULL;
    }
    p->userData = PyMem_New(UserData, sizeof(UserData));
    p->userData->handler = handler;
    p->userData->error = 0;
    p->userData->exc_type = NULL;
    p->userData->exc_val = NULL;
    p->userData->exc_tb = NULL;
    return (PyObject*) p;
}


static void parser_dealloc(parser_object* self)
{
    PyMem_Del(self->userData);
    PyMem_DEL(self);
}


static PyObject* parser_flush(parser_object* self, PyObject* args) {
    /* flush parser buffers */
    int res=0;
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
        return NULL;
    }
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;

    if (self->userData->error!=0) {
        self->userData->error = 0;
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
    void* scanner;
    if (!PyArg_ParseTuple(args, "t#", &s, &slen)) {
	PyErr_SetString(PyExc_TypeError, "string arg required");
	return NULL;
    }
    
    /* reset error state */
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;

    /* feed data to lexer and parse */
    yylex_init(&scanner);
    yy_scan_bytes(s, slen, scanner);
    yydebug = 1;
    yyparse(scanner);
    yylex_destroy(scanner);

    /* check error state */
    if (self->userData->error!=0) {
        self->userData->error = 0;
        if (self->userData->exc_type!=NULL) {
	    /* note: we give away these objects, so dont decref */
            PyErr_Restore(self->userData->exc_type,
        		  self->userData->exc_val,
        		  self->userData->exc_tb);
        }
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* parser_reset(parser_object* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
	return NULL;
    }
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
}
