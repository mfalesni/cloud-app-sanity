SHELL := /bin/bash
BUILD_DIR := build-dir
RESULTS_FILENAME := results
RESULTS_DIR := results-dir

# Documentation variables
DOCS_DIR := docs
DOCS_TITLE := CloudForms Application Sanity Test Suite
DOCS_AUTHOR := Milan Falesnik (mfalesni at redhat.com)
DOCS_VERSION := 1.00
DOCS_BRANCH_ROOT := ../cloud-app-sanity-docs/html

# Variables to control test execution
TEST_ARGS ?= -v -l --junitxml="${RESULTS_FILENAME}.xml" --resultlog="${RESULTS_FILENAME}.log"
TESTNAME ?=
# If a TESTNAME was provided, update TEST_ARGS
ifneq (,$(TESTNAME))
TEST_ARGS += -k "$(TESTNAME)"
endif

.PHONY: bootstrap pack clean doc doc_src doc_html doc_git

bootstrap: ${BUILD_DIR}

# Setup virtualenv
${BUILD_DIR}:
	[ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR)
	cp virtualenv.py $(BUILD_DIR)/virtualenv.py
	python $(BUILD_DIR)/virtualenv.py --system-site-packages $(BUILD_DIR)
	source $(BUILD_DIR)/bin/activate && easy_install pytest sphinx sphinxtogithub

clean:
	rm -f virtualenv.py *.pyc testsuite/*.pyc
	rm -rf ${BUILD_DIR} $(DOCS_DIR)/*.rst $(DOCS_DIR)/_* $(DOCS_DIR)/make.bat testsuite/__pycache__

test: bootstrap
	[ -d $(RESULTS_DIR) ] || mkdir -p $(RESULTS_DIR)
	source "$(BUILD_DIR)/bin/activate" && python "$(BUILD_DIR)/bin/py.test" testsuite $(TEST_ARGS)
	#for SUFFIX in log xml ; do ln -f -s ${RESULTS_FILENAME}.$$SUFFIX ${RESULTS_DIR}/results.$$SUFFIX ; done

doc_src: bootstrap
	[ -d $(DOCS_DIR) ] || mkdir -p $(DOCS_DIR)
	cd "$(DOCS_DIR)" && rm -rf index.rst
	source "$(BUILD_DIR)/bin/activate" && cd $(DOCS_DIR) && sphinx-apidoc -F -H "${DOCS_TITLE}" -A "${DOCS_AUTHOR}" -V "${DOCS_VERSION}" -o ./ ../testsuite/

doc_html: doc_src
	source "$(BUILD_DIR)/bin/activate" && cd $(DOCS_DIR) && make html

doc: doc_html

doc_git: doc_html
	cd $(DOCS_BRANCH_ROOT) && git add * && (git diff --quiet || (git commit -a -m "Doc update" && git pull origin gh-pages && git push origin gh-pages))