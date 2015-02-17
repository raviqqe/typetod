# typetod - typing game with endless mode written in python

PREFIX ?= /usr

BINDIR = ${DESTDIR}${PREFIX}/bin
RM = rm -f

all:
	@echo 'nothing to be compiled'

install:
	install -m 755 typetod.py ${BINDIR}/typetod

clean:
	@echo 'nothing to be cleaned'

uninstall:
	${RM} ${BINDIR}/typetod

.PHONY: all clean install uninstall
