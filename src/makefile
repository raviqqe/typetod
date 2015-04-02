# typetod - type everything forever

.include "config.mk"

VERSION = 0.02

RM = rm -rf

all:
	@echo 'nothing to be compiled'

debug:
	@echo BINDIR = ${BINDIR}
	@echo MANDIR = ${MANDIR}

man: typetod.6
	sed 's/VERSION/${VERSION}/' typetod.6 | gzip > typetod.6.gz

install: man
	install -m 755 typetod.py ${BINDIR}/typetod
	install -m 644 typetod.6.gz ${MANDIR}/typetod.6.gz

clean:
	${RM} typetod.6.gz

deinstall: uninstall
uninstall:
	${RM} ${BINDIR}/typetod
	${RM} ${MANDIR}/typetod.6.gz

.PHONY: all clean install deinstall uninstall
