/* Find recognizable tokens in (probably bad formatted) HTML streams.
   Unrecognizable character data is passed on as a TEXT token. 
*/

%{
#include <string.h>
#include <stdlib.h>
#include "Python.h"
#define YYSTYPE PyObject*
#define YY_NO_UNPUT 1
#include "htmlparse.h"
%}

%option 8bit
%option debug
%option align
%option fast
%option noyywrap
%option outfile="htmllex.c"
%option never-interactive

/* The INNER state represents all possibilities between any two angle
 * brackets <  INNER >
 */
%x S_INNER
/* we saw an EQUAL sign after a name, now we can be any where until the
 * next bit of whitespace (unquoted)
 */
%x S_ATTRVAL
/* PIs do recognize a name, then possibly some text */
%x S_IGNORE_PI
/* collect the rest of the PI if there is any */
%x S_PI_COLLECT
/* Here we ignore content (esp. markup) between some kinds of brackets and
 * just report it as TEXT
 */
%x S_IGNORE_COMMENT
%x S_IGNORE_DOCTYPE
%x S_IGNORE_CDATA
/* capture a string bounded by apostrophes "'" Aka single quotes
 * Ignore things like double quotes
 */
%x S_APOSSTRING
/* capture a string bounded by double quotes
 * Ignore things like single quotes
 */
%x S_STRING
/**
 * Try to recover from some scanner unmatch. Scan ahead for a closing '>'
 */
%x S_ERROR_RECOVER

RX_WHITE_SPACE	[\n\r\ \t\b\012]
RX_EQUAL	=
RX_NAME	[a-zA-Z]([-a-zA-Z0-9_])*

%%

<INITIAL><<EOF>> {
    return EOF;
}

<INITIAL>"</" {
    BEGIN(S_INNER);
    return T_ANGLE_END_OPEN;
}

<INITIAL>"<!--" { 
    BEGIN(S_IGNORE_COMMENT);
    return T_COMMENT_START;
}


<INITIAL>"<!DOCTYPE" {  
    BEGIN(S_IGNORE_DOCTYPE);
    return T_DOCTYPE_START;
}

<INITIAL>"<![CDATA[" { 
    BEGIN(S_IGNORE_CDATA);
    return T_CDATA_START;
}

<INITIAL>"<?" { 
    BEGIN(S_IGNORE_PI);
    return T_PI_OPEN;
}

<INITIAL>"<" {
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    BEGIN(S_INNER);
    return T_ANGLE_OPEN;
}

<INITIAL>[^<]+ {
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_TEXT;
}


<S_INNER>"/>" {
    BEGIN(INITIAL);
    return T_ANGLE_END_CLOSE;
}

<S_INNER>">" {
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_INNER>{RX_EQUAL} {
    BEGIN(S_ATTRVAL);
    return T_EQUAL;
}

<S_INNER>{RX_NAME} {
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_NAME;
}

<S_INNER>{RX_WHITE_SPACE}* {
    /* ignore whitespace */
}


<S_ATTRVAL>\" {
    BEGIN(S_STRING);
}


<S_ATTRVAL>\' {
    BEGIN(S_APOSSTRING);
}


<S_ATTRVAL>[^ \t\r\n>\'\"]+ {
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    BEGIN(S_INNER);
    return T_NAME;
}

<S_ATTRVAL>">" { 
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_ATTRVAL>[ \t\r\n]* {}



<S_IGNORE_PI>{RX_NAME} {
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    BEGIN(S_PI_COLLECT);
    return T_NAME;
}

<S_PI_COLLECT>"?>" { 
    BEGIN(INITIAL);
    return T_PI_CLOSE;
}

<S_PI_COLLECT>[^?]* { 
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_TEXT;
}


<S_IGNORE_COMMENT>"-->" {
    BEGIN(INITIAL);
    return T_COMMENT_END;
}

<S_IGNORE_COMMENT>"-" {
    /* handle any hanging minus signs E.g. i - 2; --a; etc. */
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_TEXT;   /* this has to be handled correctly in parser */
}

<S_IGNORE_COMMENT>[^\-]* {
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_TEXT;
}

<S_IGNORE_CDATA>"]]>" {
    BEGIN(INITIAL);
    return T_CDATA_END;
}

<S_IGNORE_CDATA>"]" {
    return T_TEXT;
}

<S_IGNORE_CDATA>[^\]]* {
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_TEXT;
}

<S_IGNORE_DOCTYPE>">" {
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_IGNORE_DOCTYPE>[^\>]* {
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_TEXT;
}


<S_APOSSTRING>\' {
    BEGIN(S_INNER);
    return T_STRING;
}

<S_APOSSTRING>[^']* { 
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_VALUE;
}


<S_STRING>\" {
    BEGIN(S_INNER);
    return T_STRING;
}

<S_STRING>[^"]* { 
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_VALUE;
}


<S_ERROR_RECOVER>">" {
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}


<S_ERROR_RECOVER>[^>]* {
    /* ignore all this till recover */
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng);
    // XXX error
    yyset_lval(&s, yy_globals);
    return T_TEXT;
}

%%
