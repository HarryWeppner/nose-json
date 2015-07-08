# Version
VERSION=0.2.5

# Install location
TOOLS?= /mnt/lab/bin/tools

# Package location
VPATH=./dist

# Always re-generate archive
.PHONY: nose-json-$(VERSION).tar.gz

# Copy archive to nfs share
dist: nose-json-$(VERSION).tar.gz
	cp $(VPATH)/$< $(TOOLS)/

# Generate package archive
nose-json-$(VERSION).tar.gz :
	python setup.py sdist
