/* Find recognizable tokens in (probably bad formatted) HTML streams.
   Unrecognizable character data is passed on as a TEXT token. 
*/

%{
#include <string.h>
#include <stdlib.h>
#include "htmlsax.h"

#define YYSTYPE PyObject*
#define YY_EXTRA_TYPE UserData*

#define CLEAR_BUF(a) \
    a = PyMem_Resize(a, char, 1); \
    if (!a) return T_ERROR; \
    a[0] = '\0';

#define SETLVAL {\
    PyObject* s = PyString_FromString(yyextra->tmp_buf); \
    if (s==NULL) return T_ERROR; \
    CLEAR_BUF(yyextra->tmp_buf); \
    *yylval = s; \
    }

#define APPEND_TO_TMP {\
    int len = strlen(yyextra->tmp_buf); \
    yyextra->tmp_buf = PyMem_Resize(yyextra->tmp_buf, char, len+yyleng+1); \
    strncat(yyextra->tmp_buf, yytext, yyleng); \
    }

#define LOWER_TMP {\
    char* p = yyextra->tmp_buf; \
    while (*p) { *p = tolower(*p); p++; } \
    }

#define PYSTRING_TMP(a) \
    a = PyString_FromString(yyextra->tmp_buf); \
    if (!a) { return T_ERROR; }

#define SET_ATTR_LVAL \
    *yylval = Py_BuildValue("(OO)", yyextra->tmp_tag, yyextra->tmp_attrs); \
    if ((*yylval)==NULL) return T_ERROR

#define FLUSH_ATTRS \
    if (strlen(yyextra->tmp_buf)) { \
        PYSTRING_TMP(yyextra->tmp_attrname); \
	CLEAR_BUF(yyextra->tmp_buf); \
	if (!yyextra->tmp_attrval) { \
	    Py_INCREF(Py_None); \
	    yyextra->tmp_attrval = Py_None; \
	} \
        if (PyDict_SetItem(yyextra->tmp_attrs, yyextra->tmp_attrname, Py_None)==-1) { return T_ERROR; } \
    } \
    yyextra->tmp_attrname = yyextra->tmp_attrval = NULL;

#define UPDATE_BUFPOS yyextra->bufpos += yyleng
#define RETURN(tok) yyextra->nextpos = yyextra->bufpos; return tok

#include "htmlparse.h"
/* Find out if and how we must quote the value as an HTML attribute.
 - quote if it contains white space or <>
 - quote with " if it contains '
 - quote with ' if it contains "

 val is a Python String object
*/
static PyObject* quote_string (PyObject* val) {
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
%}

%option 8bit outfile="htmllex.c"
%option align fast
%option debug
%option nounput nomain noyywrap noyymore noreject
%option reentrant-bison never-interactive
%option warn

%x S_ERROR
%x S_PI
%x S_COMMENT
%x S_DOCTYPE
%x S_CDATA
%x S_TAGSTART
%x S_TAGEND
%x S_SCRIPT
%x S_ATTR1
%x S_ATTR2
%x S_ATTR3
%x S_ATTR4
%x S_ATTR5
%x S_APOSSTRING
%x S_STRING

RX_WHITE_SPACE	[\n\r\ \t\b\012]
RX_EQUAL	=
RX_NAME	[a-zA-Z]([-a-zA-Z0-9_])*
RX_DATA [-a-zA-Z0-9_]+

%%

  /*********************** EOF ************************/
<<EOF>> {
    return T_WAIT;
}

  /*********************** COMMENT ************************/
<INITIAL>"<!--" {
    UPDATE_BUFPOS;
    BEGIN(S_COMMENT);
}

<S_COMMENT>"-->" {
    UPDATE_BUFPOS;
    SETLVAL;
    BEGIN(INITIAL);
    RETURN(T_COMMENT);
}

<S_COMMENT>"-" {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

<S_COMMENT>[^\-]* {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

  /*********************** DOCTYPE ************************/
<INITIAL>"<!DOCTYPE" {
    UPDATE_BUFPOS;
    BEGIN(S_DOCTYPE);
}

<S_DOCTYPE>">" {
    UPDATE_BUFPOS;
    SETLVAL;
    BEGIN(INITIAL);
    RETURN(T_DOCTYPE);
}

<S_DOCTYPE>[^\>]* {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

  /*********************** CDATA ************************/
<INITIAL>"<![CDATA[" { 
    UPDATE_BUFPOS;
    BEGIN(S_CDATA);
}

<S_CDATA>"]]>" {
    UPDATE_BUFPOS;
    SETLVAL;
    BEGIN(INITIAL);
    RETURN(T_CDATA);
}

<S_CDATA>"]" {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

<S_CDATA>[^\]]* {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

  /*********************** PI ************************/
<INITIAL>"<?" {
    UPDATE_BUFPOS;
    BEGIN(S_PI);
}

<S_PI>"?>" {
    UPDATE_BUFPOS;
    SETLVAL;
    BEGIN(INITIAL);
    RETURN(T_PI);
}

<S_PI>[^\?]*|\? {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

  /*********************** TAGSTART ************************/
<INITIAL><{RX_WHITE_SPACE}* {
    UPDATE_BUFPOS;
    yyextra->tmp_attrs = PyDict_New();
    if (!yyextra->tmp_attrs) return T_ERROR;
    BEGIN(S_TAGSTART);
}

<S_TAGSTART>{RX_NAME} {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

<S_TAGSTART>{RX_WHITE_SPACE}+ {
    UPDATE_BUFPOS;
    LOWER_TMP;
    PYSTRING_TMP(yyextra->tmp_tag);
    CLEAR_BUF(yyextra->tmp_buf);
    BEGIN(S_ATTR1);
}

<S_TAGSTART>"/>" {
    UPDATE_BUFPOS;
    LOWER_TMP;
    PYSTRING_TMP(yyextra->tmp_tag);
    CLEAR_BUF(yyextra->tmp_buf);
    BEGIN(INITIAL);
    SET_ATTR_LVAL;
    RETURN(T_ELEMENT_START_END);
}

<S_TAGSTART>">" {
    UPDATE_BUFPOS;
    LOWER_TMP;
    PYSTRING_TMP(yyextra->tmp_tag);
    if (strcmp("script", yyextra->tmp_buf)==0)
	BEGIN(S_SCRIPT);
    else
	BEGIN(INITIAL);
    CLEAR_BUF(yyextra->tmp_buf);
    SET_ATTR_LVAL;
    RETURN(T_ELEMENT_START);
}

<S_TAGSTART>. {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
    BEGIN(S_ERROR);
}

  /*********************** SCRIPT ************************/
<S_SCRIPT><\/{RX_WHITE_SPACE}*[Ss][Cc][Rr][Ii][Pp][Tt]{RX_WHITE_SPACE}*> {
    UPDATE_BUFPOS;
    SETLVAL;
    BEGIN(INITIAL);
    RETURN(T_SCRIPT);
}

<S_SCRIPT>[^<]*|< {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

  /*********************** ATTRS ************************/
<S_ATTR1>{RX_NAME} {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
    BEGIN(S_ATTR2);
}

<S_ATTR1,S_ATTR2,S_ATTR3>"/>" {
    UPDATE_BUFPOS;
    FLUSH_ATTRS;
    BEGIN(INITIAL);
    SET_ATTR_LVAL;
    RETURN(T_ELEMENT_START_END);
}

<S_ATTR1,S_ATTR2,S_ATTR3>">" {
    UPDATE_BUFPOS;
    FLUSH_ATTRS;
    BEGIN(INITIAL);
    SET_ATTR_LVAL;
    RETURN(T_ELEMENT_START);
}

<S_ATTR2>{RX_DATA} {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

<S_ATTR2>{RX_WHITE_SPACE}+ {
    UPDATE_BUFPOS;
    PYSTRING_TMP(yyextra->tmp_attrname);
    CLEAR_BUF(yyextra->tmp_buf);
    BEGIN(S_ATTR3);
}

<S_ATTR2,S_ATTR3>{RX_EQUAL}{RX_WHITE_SPACE}* {
    UPDATE_BUFPOS;
    PYSTRING_TMP(yyextra->tmp_attrname);
    CLEAR_BUF(yyextra->tmp_buf);
    BEGIN(S_ATTR4);
}

<S_ATTR1,S_ATTR2>. {
    /* this also skips whitespace! */
    UPDATE_BUFPOS;
}

<S_ATTR3>{RX_NAME} {
    UPDATE_BUFPOS;
    Py_INCREF(Py_None);
    if (PyDict_SetItem(yyextra->tmp_attrs, yyextra->tmp_attrname, Py_None)==-1) { return T_ERROR; }
    APPEND_TO_TMP;
    BEGIN(S_ATTR2);
}

<S_ATTR4>\" {
    UPDATE_BUFPOS;
    BEGIN(S_STRING);
}


<S_ATTR4>\' {
    UPDATE_BUFPOS;
    BEGIN(S_APOSSTRING);
}


<S_ATTR4>[^\012 \t\b\r\n>\'\"]+ {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
    BEGIN(S_ATTR5);
}

<S_ATTR5>[^\012 \t\b\r\n>]+ {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

<S_ATTR5>">" {
    UPDATE_BUFPOS;
    PYSTRING_TMP(yyextra->tmp_attrval);
    CLEAR_BUF(yyextra->tmp_buf);
    if (PyDict_SetItem(yyextra->tmp_attrs, yyextra->tmp_attrname, yyextra->tmp_attrval)==-1) { return T_ERROR; }
    BEGIN(INITIAL);
    SET_ATTR_LVAL;
    RETURN(T_ELEMENT_START);
}

<S_ATTR5>"/>" {
    UPDATE_BUFPOS;
    PYSTRING_TMP(yyextra->tmp_attrval);
    CLEAR_BUF(yyextra->tmp_buf);
    if (PyDict_SetItem(yyextra->tmp_attrs, yyextra->tmp_attrname, yyextra->tmp_attrval)==-1) { return T_ERROR; }
    BEGIN(INITIAL);
    SET_ATTR_LVAL;
    RETURN(T_ELEMENT_START_END);
}

<S_ATTR5>{RX_WHITE_SPACE}+ {
    UPDATE_BUFPOS;
    if (PyDict_SetItem(yyextra->tmp_attrs, yyextra->tmp_attrname, yyextra->tmp_attrval)==-1) { return T_ERROR; }
    BEGIN(S_ATTR1);
}

<S_APOSSTRING>\' {
    UPDATE_BUFPOS;
    PYSTRING_TMP(yyextra->tmp_attrval);
    CLEAR_BUF(yyextra->tmp_buf);
    yyextra->tmp_attrval = quote_string(yyextra->tmp_attrval);
    if (!yyextra->tmp_attrval) { return T_ERROR; }
    if (PyDict_SetItem(yyextra->tmp_attrs, yyextra->tmp_attrname, yyextra->tmp_attrval)==-1) { return T_ERROR; }
    BEGIN(S_ATTR1);
}

<S_APOSSTRING>[^']* { 
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}


<S_STRING>\" {
    UPDATE_BUFPOS;
    PYSTRING_TMP(yyextra->tmp_attrval);
    CLEAR_BUF(yyextra->tmp_buf);
    yyextra->tmp_attrval = quote_string(yyextra->tmp_attrval);
    if (!yyextra->tmp_attrval) { return T_ERROR; }
    if (PyDict_SetItem(yyextra->tmp_attrs, yyextra->tmp_attrname, yyextra->tmp_attrval)==-1) { return T_ERROR; }
    yyextra->tmp_attrval = yyextra->tmp_attrname = NULL;
    BEGIN(S_ATTR1);
}

<S_STRING>[^"]* { 
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

  /*********************** TAGEND ************************/
<INITIAL>"</"{RX_WHITE_SPACE} {
    UPDATE_BUFPOS;
    BEGIN(S_TAGEND);
}

<S_TAGEND>{RX_NAME} {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

<S_TAGEND>">" {
    UPDATE_BUFPOS;
    SETLVAL;
    RETURN(T_ELEMENT_END);
}

<S_TAGEND>"<"{RX_WHITE_SPACE} {
    UPDATE_BUFPOS;
    BEGIN(S_TAGSTART);
}

<S_TAGEND>. {
    UPDATE_BUFPOS;
}

  /*********************** ERROR ************************/
<S_ERROR>[^>]* {
    UPDATE_BUFPOS;
    APPEND_TO_TMP;
}

<S_ERROR>">" {
    UPDATE_BUFPOS;
    SETLVAL;
    BEGIN(INITIAL);
    RETURN(T_TEXT);
}

  /*********************** END ************************/
%%

int htmllexInit (void** scanner, UserData* data) {
    yylex_init(scanner);
    yyset_extra(data, *scanner);
    return 0;
}

/* prepare scanner for calls to yylex() */
int htmllexStart (void* scanner, UserData* data, const char* s, int slen) {
    /* append s to data buffer and scan those bytes */
    int len = strlen(data->buf)+slen+1;
    data->buf = PyMem_Resize(data->buf, char, len);
    strncat(data->buf, s, slen);
    /* reset userdata */
    data->bufpos = 0;
    data->nextpos = 0;
    data->exc_type = NULL;
    data->exc_val = NULL;
    data->exc_tb = NULL;
    yy_scan_bytes(data->buf, len, scanner);
    return 0;
}

/* delete scanned buffer data */
int htmllexStop (UserData* data) {
    if (data->nextpos<=0) return 0;
    else {
	int len = strlen(data->buf);
	int i, j;
	for (i=data->nextpos,j=0; i<len; i++,j++) {
            data->buf[j] = data->buf[i];
	}
	data->buf[j] = '\0';
	data->buf = PyMem_Resize(data->buf, char, len-data->nextpos+1);
    }
    return 0;
}

int htmllexDestroy (void* scanner) {
    yylex_destroy(scanner);
    return 0;
}

