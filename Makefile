# Makefile for development.
# See INSTALL and docs/dev.txt for details.
SHELL = /bin/bash
ROOT_DIR = $(shell pwd)
BIN_DIR = $(ROOT_DIR)/bin
CFG_DIR = $(ROOT_DIR)/etc
DATA_DIR = $(ROOT_DIR)/var
VIRTUALENV_DIR = $(ROOT_DIR)/lib/virtualenv
PIP = $(VIRTUALENV_DIR)/bin/pip
PROJECT = insight_reloaded
NOSE = $(BIN_DIR)/nosetests

develop: virtualenv bin_dir directories
	$(PIP) install -e $(ROOT_DIR)


virtualenv:
	if [ ! -x $(PIP) ]; then virtualenv --no-site-packages --setuptools $(VIRTUALENV_DIR); fi


bin_dir:
	if [ ! -h $(BIN_DIR) ]; then \
		ln -s $(VIRTUALENV_DIR)/bin $(BIN_DIR); \
	fi;


directories:
	mkdir -p $(DATA_DIR)/test


clean:
	find $(ROOT_DIR)/ -name "*.pyc" -delete
	find $(ROOT_DIR)/ -name ".noseids" -delete
	find $(ROOT_DIR)/ -name ".coverage" -delete


distclean: clean
	rm -rf $(ROOT_DIR)/*.egg-info


maintainer-clean: distclean
	rm -f $(BIN_DIR)
	rm -fr $(ROOT_DIR)/lib/


test:
	$(VIRTUALENV_DIR)/bin/python setup.py test


doc:
	cd docs; make html
