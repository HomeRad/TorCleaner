/* Find recognizable tokens in (probably bad formatted) HTML streams.
   Unrecognizable character data is passed on as a TEXT token. 
*/

%{
#include <string.h>
#include <stdlib.h>
#include "Python.h"
#define YYSTYPE PyObject*
#include "htmlparse.h"
/*#define SETLVAL \
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng); \
    yyset_lval(&s, yy_globals)
*/
#define SETLVAL \
    printf("huii %s\n", yytext)

%}

%option 8bit
%option debug
%option align
%option fast
%option noyywrap
%option noyymore
%option nounput
%option noreject
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
    SETLVAL;
    BEGIN(S_INNER);
    return T_ANGLE_END_OPEN;
}

<INITIAL>"<!--" { 
    SETLVAL;
    BEGIN(S_IGNORE_COMMENT);
    return T_COMMENT_START;
}


<INITIAL>"<!DOCTYPE" {  
    SETLVAL;
    BEGIN(S_IGNORE_DOCTYPE);
    return T_DOCTYPE_START;
}

<INITIAL>"<![CDATA[" { 
    SETLVAL;
    BEGIN(S_IGNORE_CDATA);
    return T_CDATA_START;
}

<INITIAL>"<?" { 
    SETLVAL;
    BEGIN(S_IGNORE_PI);
    return T_PI_OPEN;
}

<INITIAL>"<" {
    SETLVAL;
    BEGIN(S_INNER);
    return T_ANGLE_OPEN;
}

<INITIAL>[^<]+ {
    SETLVAL;
    return T_TEXT;
}


<S_INNER>"/>" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_ANGLE_END_CLOSE;
}

<S_INNER>">" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_INNER>{RX_EQUAL} {
    SETLVAL;
    BEGIN(S_ATTRVAL);
    return T_EQUAL;
}

<S_INNER>{RX_NAME} {
    SETLVAL;
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
    SETLVAL;
    BEGIN(S_INNER);
    return T_NAME;
}

<S_ATTRVAL>">" { 
    SETLVAL;
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_ATTRVAL>[ \t\r\n]* {}



<S_IGNORE_PI>{RX_NAME} {
    SETLVAL;
    BEGIN(S_PI_COLLECT);
    return T_NAME;
}

<S_PI_COLLECT>"?>" { 
    SETLVAL;
    BEGIN(INITIAL);
    return T_PI_CLOSE;
}

<S_PI_COLLECT>[^?]* { 
    SETLVAL;
    return T_TEXT;
}


<S_IGNORE_COMMENT>"-->" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_COMMENT_END;
}

<S_IGNORE_COMMENT>"-" {
    /* handle any hanging minus signs E.g. i - 2; --a; etc. */
    SETLVAL;
    return T_TEXT;
}

<S_IGNORE_COMMENT>[^\-]* {
    SETLVAL;
    return T_TEXT;
}

<S_IGNORE_CDATA>"]]>" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_CDATA_END;
}

<S_IGNORE_CDATA>"]" {
    SETLVAL;
    return T_TEXT;
}

<S_IGNORE_CDATA>[^\]]* {
    SETLVAL;
    return T_TEXT;
}

<S_IGNORE_DOCTYPE>">" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_IGNORE_DOCTYPE>[^\>]* {
    SETLVAL;
    return T_TEXT;
}


<S_APOSSTRING>\' {
    SETLVAL;
    BEGIN(S_INNER);
    return T_STRING;
}

<S_APOSSTRING>[^']* { 
    SETLVAL;
    return T_VALUE;
}


<S_STRING>\" {
    SETLVAL;
    BEGIN(S_INNER);
    return T_STRING;
}

<S_STRING>[^"]* { 
    SETLVAL;
    return T_VALUE;
}


<S_ERROR_RECOVER>">" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}


<S_ERROR_RECOVER>[^>]* {
    /* ignore all this till recover */
    SETLVAL;
    return T_TEXT;
}

%%

void yyerror (char* msg) {
    fprintf(stderr, "htmllex: error: %s\n", msg);
}

