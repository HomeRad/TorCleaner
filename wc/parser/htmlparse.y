%{
/* SAX parser, optimized for WebCleaner */
#include <malloc.h>
#include <string.h>
#include <stdio.h>
#include "htmlsax.h"

#define YYSTYPE PyObject*
#define YYPARSE_PARAM scanner
#define YYLEX_PARAM scanner
extern int htmllexStart(void** scanner, const char* s, int slen, void* data);
extern int htmllexStop(void* scanner);
extern int yylex(YYSTYPE* yylvalp, void* scanner);
extern void* yyget_extra(void*);
#define YYERROR_VERBOSE 1
extern char* stpcpy(char* src, const char* dest);
int yyerror(char* msg);

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
    {
        UserData* ud = (UserData*)yyget_extra(scanner);
        PyObject* callback = PyObject_GetAttrString(ud->handler, "comment");
        PyObject* arglist = Py_BuildValue("(O)", $2);
        if (PyEval_CallObject(callback, arglist)==NULL) {
	    ud->error = 1;
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
        }
        Py_DECREF(arglist);
    }
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

    /* feed data to lexer and parse */
    htmllexStart(&scanner, s, slen, (UserData*)self->userData);
    yyparse(scanner);
    htmllexStop(scanner);

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

int yyerror (char* msg) {
    fprintf(stderr, "htmllex: error: %s\n", msg);
    return 0;
}

int main (void) {
    void* scanner;
    UserData userData;
    userData.handler = NULL;
    userData.error = 0;
    userData.exc_type = NULL;
    userData.exc_val = NULL;
    userData.exc_tb = NULL;
    yydebug=1;
    htmllexStart(&scanner, "<html>", 6, &userData);
    yyparse(scanner);
    return htmllexStop(scanner);
}
