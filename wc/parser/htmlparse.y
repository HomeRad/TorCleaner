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
//%debug
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
%token T_QUOTE
%token T_APOS
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
   | T_TEXT
   {
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
   | T_EOF {}
   ;


comment: T_COMMENT_START comment_text T_COMMENT_END
    {
	UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "comment")==1) {
            callback = PyObject_GetAttrString(ud->handler, "comment");
            if (callback==NULL) { error=1; goto finish_comment; }
            result = PyObject_CallFunction(callback, "O", $2);
            if (result==NULL) { error=1; goto finish_comment; }
        }
    finish_comment:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF($2);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    ;


comment_text: T_TEXT { $$ = $1; }
    | comment_text T_TEXT
    {
        PyString_ConcatAndDel(&$1, $2);
        $$ = $1;
    }
    ;


element_start: T_ANGLE_OPEN T_NAME attributes T_ANGLE_CLOSE
    {
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
	PyObject* ltag = PyObject_CallMethod($2, "lower", NULL);
        if (ltag==NULL) { error=1; goto finish_start1; }
        if (PyObject_HasAttrString(ud->handler, "startElement")==1) {
            callback = PyObject_GetAttrString(ud->handler, "startElement");
            if (callback==NULL) { error=1; goto finish_start1; }
            result = PyObject_CallFunction(callback, "OO", ltag, $3);
            if (result==NULL) { error=1; goto finish_start1; }
        }
    finish_start1:
        Py_XDECREF(ltag);
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF($2);
        Py_DECREF($3);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    | T_ANGLE_OPEN T_NAME attributes T_ANGLE_END_CLOSE
    {
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        PyObject* ltag = PyObject_CallMethod($2, "lower", NULL);
        if (ltag==NULL) { error=1; goto finish_start2; }
        if (PyObject_HasAttrString(ud->handler, "startElement")==1) {
            callback = PyObject_GetAttrString(ud->handler, "startElement");
            if (callback==NULL) { error=1; goto finish_start2; }
            result = PyObject_CallFunction(callback, "OO", ltag, $3);
            if (result==NULL) { error=1; goto finish_start2; }
        }
        if (PyObject_HasAttrString(ud->handler, "endElement")==1) {
            callback = PyObject_GetAttrString(ud->handler, "endElement");
            if (callback==NULL) { error=1; goto finish_start2; }
            result = PyObject_CallFunction(callback, "O", ltag);
            if (result==NULL) { error=1; goto finish_start2; }
        }
    finish_start2:
        Py_XDECREF(ltag);
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF($2);
        Py_DECREF($3);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    ;


element_end: T_ANGLE_END_OPEN T_NAME T_ANGLE_CLOSE
    {
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        PyObject* ltag = PyObject_CallMethod($2, "lower", NULL);
        if (ltag==NULL) { error=1; goto finish_end; }
        if (PyObject_HasAttrString(ud->handler, "endElement")==1) {
            callback = PyObject_GetAttrString(ud->handler, "endElement");
            if (callback==NULL) { error=1; goto finish_end; }
            result = PyObject_CallFunction(callback, "O", ltag);
            if (result==NULL) { error=1; goto finish_end; }
        }
    finish_end:
        Py_XDECREF(ltag);
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF($2);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    ;


/* return type: a Python dictionary with HTML attributes*/
attributes: /* empty */ {
        UserData* ud = yyget_extra(scanner);
        PyObject* dict = PyDict_New();
        if (dict==NULL) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
        $$ = dict;
    }
    | attribute attributes
    {
        UserData* ud = yyget_extra(scanner);
        PyObject* name = NULL;
        PyObject* val = NULL;
        int error = 0;
        name = PyTuple_GET_ITEM($1, 0);
        if (name==NULL) { error = 1; goto finish_attributes; }
        val = PyTuple_GET_ITEM($1, 1);
        if (val==NULL) { error = 1; goto finish_attributes; }
        if (PyDict_SetItem($2, name, val)==-1) { error = 1; goto finish_attributes; }
        $$ = $2;
    finish_attributes:
        Py_DECREF($1);
	if (error) {
	    Py_XDECREF(name);
	    Py_XDECREF(val);
            Py_XDECREF($2);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    ;


/* return type: a Python tuple (name, value).
 * value can be None
 * value is appropriate quoted (has only quotes if needed)
 */
attribute: T_NAME T_EQUAL T_QUOTE T_VALUE T_QUOTE
    {
        UserData* ud = yyget_extra(scanner);
	PyObject* lname = NULL;
        PyObject* val = NULL;
        PyObject* tup = NULL;
	int error = 0;
        lname = PyObject_CallMethod($1, "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr1; }
	val = quote_string($3);
	if (val==NULL) { error = 1; goto finish_attr1; }
        tup = Py_BuildValue("(OO)", lname, val);
        if (tup==NULL) { error = 1; goto finish_attr1; }
        $$ = tup;
    finish_attr1:
	Py_DECREF($1);
	if (val!=$3) {
	    Py_DECREF($3);
	}
	if (error) {
            Py_XDECREF(tup);
	    Py_XDECREF(lname);
            Py_XDECREF(val);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    | T_NAME T_EQUAL T_APOS T_VALUE T_APOS
    {
        UserData* ud = yyget_extra(scanner);
	PyObject* lname = NULL;
        PyObject* val = NULL;
        PyObject* tup = NULL;
	int error = 0;
        lname = PyObject_CallMethod($1, "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr1b; }
	val = quote_string($3);
	if (val==NULL) { error = 1; goto finish_attr1b; }
        tup = Py_BuildValue("(OO)", lname, val);
        if (tup==NULL) { error = 1; goto finish_attr1b; }
        $$ = tup;
    finish_attr1b:
        Py_DECREF($1);
	if (val!=$3) {
	    Py_DECREF($3);
	}
	if (error) {
            Py_XDECREF(tup);
	    Py_XDECREF(lname);
            Py_XDECREF(val);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    | T_NAME T_EQUAL T_QUOTE T_QUOTE
    {
        UserData* ud = yyget_extra(scanner);
	PyObject* lname = NULL;
        PyObject* val = NULL;
        PyObject* tup = NULL;
        int error = 0;
	lname = PyObject_CallMethod($1, "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr2; }
	val = PyString_FromString("''");
	if (val==NULL) { error = 1; goto finish_attr2; }
        tup = Py_BuildValue("(OO)", lname, val);
        if (tup==NULL) { error = 1; goto finish_attr2; }
        $$ = tup;
    finish_attr2:
        Py_DECREF($1);
	if (error) {
	    Py_XDECREF(lname);
	    Py_XDECREF(val);
	    Py_XDECREF(tup);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    | T_NAME T_EQUAL T_APOS T_APOS
    {
        UserData* ud = yyget_extra(scanner);
	PyObject* lname = NULL;
        PyObject* val = NULL;
        PyObject* tup = NULL;
        int error = 0;
	lname = PyObject_CallMethod($1, "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr2b; }
	val = PyString_FromString("''");
	if (val==NULL) { error = 1; goto finish_attr2b; }
        tup = Py_BuildValue("(OO)", lname, val);
        if (tup==NULL) { error = 1; goto finish_attr2b; }
        $$ = tup;
    finish_attr2b:
        Py_DECREF($1);
	if (error) {
	    Py_XDECREF(lname);
	    Py_XDECREF(val);
	    Py_XDECREF(tup);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    | T_NAME T_EQUAL T_NAME
    {
        UserData* ud = yyget_extra(scanner);
        PyObject* lname = NULL;
        PyObject* tup = NULL;
        int error = 0;
        lname = PyObject_CallMethod($1, "lower", NULL);
        if (lname==NULL) { error = 1; goto finish_attr3; }
        tup = Py_BuildValue("(OO)", lname, $3);
        if (tup==NULL) { error = 1; goto finish_attr3; }
        $$ = tup;
    finish_attr3:
        Py_DECREF($1);
	if (error) {
	    Py_XDECREF(lname);
            Py_XDECREF(tup);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    | T_NAME
    {
        UserData* ud = yyget_extra(scanner);
        PyObject* lname = NULL;
        PyObject* tup = NULL;
        int error = 0;
        lname = PyObject_CallMethod($1, "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr4; }
        Py_INCREF(Py_None);
        tup = Py_BuildValue("(OO)", lname, Py_None);
        if (tup==NULL) { error = 1; goto finish_attr4; }
        $$ = tup;
    finish_attr4:
        Py_DECREF($1);
	if (error) {
	    Py_XDECREF(lname);
            Py_XDECREF(tup);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    ;


pi: T_PI_OPEN T_NAME T_TEXT T_PI_CLOSE
    {
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "pi")==1) {
            callback = PyObject_GetAttrString(ud->handler, "pi");
            if (callback==NULL) { error=1; goto finish_pi1; }
            result = PyObject_CallFunction(callback, "OO", $2, $3);
            if (result==NULL) { error=1; goto finish_pi1; }
        }
    finish_pi1:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF($2);
        Py_DECREF($3);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    | T_PI_OPEN T_NAME T_PI_CLOSE
    {
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "pi")==1) {
            callback = PyObject_GetAttrString(ud->handler, "pi");
            if (callback==NULL) { error=1; goto finish_pi2; }
            result = PyObject_CallFunction(callback, "O", $2);
            if (result==NULL) { error=1; goto finish_pi2; }
        }
    finish_pi2:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF($2);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    ;


cdata: T_CDATA_START text T_CDATA_END {
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "cdata")==1) {
            callback = PyObject_GetAttrString(ud->handler, "cdata");
            if (callback==NULL) { error=1; goto finish_cdata; }
            result = PyObject_CallFunction(callback, "O", $2);
            if (result==NULL) { error=1; goto finish_cdata; }
        }
    finish_cdata:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF($2);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    }
    ;


text: /* empty */ {
        UserData* ud = yyget_extra(scanner);
        PyObject* result = PyString_FromString("");
        if (result==NULL) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
        $$ = result;
    }
    | text T_TEXT
    {
        UserData* ud = yyget_extra(scanner);
        PyString_ConcatAndDel(&$1, $2);
        if ($1==NULL) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
        $$ = $1;
    }
    ;


/* TODO: This needs to resolve startEntity, DeclHandlers etc. For now just report TEXT */
doctype: T_DOCTYPE_START T_TEXT T_ANGLE_CLOSE
    {
	UserData* ud = yyget_extra(scanner);
	PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "doctype")==1) {
            callback = PyObject_GetAttrString(ud->handler, "doctype");
            if (callback==NULL) { error=1; goto finish_doctype; }
            result = PyObject_CallFunction(callback, "O", $2);
            if (result==NULL) { error=1; goto finish_doctype; }
        }
    finish_doctype:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF($2);
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
    if (yyparse(self->scanner)!=0) {
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
    //yydebug = 1;
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
