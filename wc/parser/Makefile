# use CVS snapshot flex for reentrant bison parser support
FLEX=/home/pool/src/flex/flex

all: htmllex.o htmlparse.o

%.o:	%.c
	gcc -g -O2 -Wall -pedantic -Wstrict-prototypes -fPIC -I. -I/usr/include/python2.1 -c $< -o $@

htmlparse.h htmlparse.c:	htmlparse.y
	bison htmlparse.y

htmllex.l:	htmlparse.h

htmllex.c:	htmllex.l
	$(FLEX) --reentrant-bison htmllex.l

test:	testsax
	cat test.html | ./testsax

clean:
	rm -f htmlparse.c htmlparse.h htmllex.c *.o *.output
