CC ?= gcc

all:
	cython -3 --embed daemon.py
	eval $(CC) `python-config --cflags --ldflags` daemon.c -o daemon

clean:
	rm -f daemon.c daemon

