CC ?= gcc

.PRONY: daemon.c verify.c

all: daemon.c verify.c
	eval $(CC) `python-config --cflags --ldflags` daemon.c verify.c -o daemon

daemon.c:
	cython -3 --embed daemon.py

verify.c:
	cython -3 verify.py

clean:
	rm -f daemon.c verify.c daemon

