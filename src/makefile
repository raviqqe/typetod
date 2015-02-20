# typetod - typing game with endless mode written in python

VERSION = 0.01

PREFIX ?= /usr
MANPREFIX ?= /usr/share
BINDIR = ${DESTDIR}${PREFIX}/bin
MANDIR = ${DESTDIR}${MANPREFIX}/man/man6

RM = rm -rf

all:
	@echo 'nothing to be compiled'

install:
	install -m 755 -D typetod.py ${BINDIR}/typetod
	sed 's/VERSION/${VERSION}/' typetod.6 | gzip > typetod.6.gz
	install -m 644 -D typetod.6.gz ${MANDIR}

clean:
	${RM} typetod.6.gz

deinstall: uninstall
uninstall:
	${RM} ${BINDIR}/typetod
	${RM} ${MANDIR}/typetod.6.gz

.PHONY: all clean install deinstall uninstall
