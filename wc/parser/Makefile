# use CVS snapshot flex for reentrant bison parser support
FLEX=/home/pool/src/flex/flex

all: testsax

testsax: htmllex.o htmlparse.o
	gcc -lpython2.1 $^ -o testsax

%.o:	%.c
	gcc -g -Wall -pedantic -Wstrict-prototypes -fPIC -I. -I/usr/include/python2.1 -c $< -o $@

htmlparse.h htmlparse.c:	htmlparse.y
	bison htmlparse.y

htmllex.l:	htmlparse.h

htmllex.c:	htmllex.l
	$(FLEX) htmllex.l

test:	testsax
	cat test.html | ./testsax

clean:
	rm -f htmlparse.c htmlparse.h htmllex.c *.o *.output testsax
