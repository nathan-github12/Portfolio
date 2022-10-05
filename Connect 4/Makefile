CFLAGS = -Wall -Wextra -pedantic -std=c11
DEPS = add.h subtract.h

all: main

main: libmaths.so maths_prog.o
	gcc $(CFLAGS) maths_prog.o -L. -lmaths -o maths_prog

%.o: %.c $(DEPS)
	gcc $(CFLAGS) -c $< -o $@


libmaths.so: add.o subtract.o
	gcc $(CFLAGS) -shared $^ -o $@
 
clean:
	rm -rf *.o libmaths.so maths_prog


