# Install location
TOOLS?= /testlab/results/bin/tools

# Package location
VPATH=./dist

# Always re-generate archive
.PHONY: nose-json-0.2.4.tar.gz

# Copy archive to nfs share
dist: nose-json-0.2.4.tar.gz
	cp $(VPATH)/$< $(TOOLS)/

# Generate package archive
nose-json-0.2.4.tar.gz :
	python setup.py sdist
