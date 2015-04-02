# Created by: raviqqe <raviqqe@gmail.com>
# $FreeBSD: head/games/typetod/Makefile 351411 2015-03-31 18:28:47Z zeising $

# THIS MAKEFILE IS WORK IN PROGRESS

PORTNAME=	typetod
PORTVERSION= 0.02
PORTREVISION=	1
CATEGORIES=	games
MASTER_SITES=	http://github.com/raviqqe/${PORTNAME}/raw/master/pkg/${PORTNAME}-${PORTVERSION}.tar.gz

MAINTAINER=	raviqqe@gmail.com
COMMENT= typing game with endless mode

LICENSE= UNLICENSE
LICENSE_FILE=	${WRKSRC}/UNLICENSE

#OPTIONS_DEFINE=
#OPTIONS_DEFAULT=
#USE_XORG=

PLIST_FILES=	bin/typetod
		man/man6/typetod.6.gz
PORTDOCS=	README

.include <bsd.port.options.mk>

.if ${PORT_OPTIONS:MXINERAMA}
USE_XORG+=	xinerama
.endif

.if ${PORT_OPTIONS:MXFT}
LIB_DEPENDS+=	libfreetype.so:${PORTSDIR}/print/freetype2 \
		libexpat.so:${PORTSDIR}/textproc/expat2 \
		libfontconfig.so:${PORTSDIR}/x11-fonts/fontconfig
USE_XORG+=	xft xrender
PATCHFILES+=	${PORTNAME}-${PORTVERSION}-xft.diff
.endif

pre-everything::
	@${ECHO_MSG} "You can build dwm with your own config.h using the DWM_CONF knob:"
	@${ECHO_MSG} "make DWM_CONF=/path/to/dwm/config.h install clean"
	@${ECHO_MSG} "Note: Pre-6.0 config.h-files no longer work."

post-extract:
.if defined(DWM_CONF)
	@${ECHO_MSG} "creating config.h from ${DWM_CONF}"
	@${CP} ${DWM_CONF} ${WRKSRC}/config.h
.endif

post-patch:
	@${GREP} -Rl '%%[[:alpha:]]\+%%' ${WRKSRC}|${XARGS} ${REINPLACE_CMD} \
	         -e "s,%%PREFIX%%,${PREFIX},g" \
	         -e "s,%%LOCALBASE%%,${LOCALBASE},g" \
	         -e "s,%%MANPREFIX%%,${MANPREFIX},g"
.if empty(PORT_OPTIONS:MXINERAMA)
	@${REINPLACE_CMD} -e 's,$${XINERAMALIBS},,g' \
	         -e 's,$${XINERAMAFLAGS},,g' ${WRKSRC}/config.mk
.endif
.if empty(PORT_OPTIONS:MXFT)
	@${REINPLACE_CMD} -e 's,$${XFTLIBS},,g' \
	         -e 's,$${XFTINCS},,g' ${WRKSRC}/config.mk
.endif

.include <bsd.port.mk>
