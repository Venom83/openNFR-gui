installdir = $(pkglibdir)/python/Plugins/Extensions/Infopanel

SUBDIRS = meta icons locale Extra meta pics data images

install_PYTHON = *.py

dist_install_DATA = \
	sundtekinstall.sh \
	testIP

install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/sundtekinstall.sh

