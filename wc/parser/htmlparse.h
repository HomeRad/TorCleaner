/* A Bison parser, made from htmlparse.y, by GNU bison 1.50.  */

/* Skeleton parser for Yacc-like parsing with Bison,
   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002 Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place - Suite 330,
   Boston, MA 02111-1307, USA.  */

/* As a special exception, when this file is copied by Bison into a
   Bison output file, you may use that output file without restriction.
   This special exception was added by the Free Software Foundation
   in version 1.24 of Bison.  */

#ifndef BISON_HTMLPARSE_H
# define BISON_HTMLPARSE_H

/* Tokens.  */
#ifndef YYTOKENTYPE
# if defined (__STDC__) || defined (__cplusplus)
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     T_WAIT = 258,
     T_ERROR = 259,
     T_TEXT = 260,
     T_ELEMENT_START = 261,
     T_ELEMENT_START_END = 262,
     T_ELEMENT_END = 263,
     T_SCRIPT = 264,
     T_STYLE = 265,
     T_PI = 266,
     T_COMMENT = 267,
     T_CDATA = 268,
     T_DOCTYPE = 269
   };
# endif
  /* POSIX requires `int' for tokens in interfaces.  */
# define YYTOKENTYPE int
#endif /* !YYTOKENTYPE */
#define T_WAIT 258
#define T_ERROR 259
#define T_TEXT 260
#define T_ELEMENT_START 261
#define T_ELEMENT_START_END 262
#define T_ELEMENT_END 263
#define T_SCRIPT 264
#define T_STYLE 265
#define T_PI 266
#define T_COMMENT 267
#define T_CDATA 268
#define T_DOCTYPE 269




#ifndef YYSTYPE
typedef int yystype;
# define YYSTYPE yystype
#endif




#endif /* not BISON_HTMLPARSE_H */

