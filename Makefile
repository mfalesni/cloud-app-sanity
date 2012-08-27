SHELL := /bin/bash
BUILD_DIR := build-dir
RESULTS_FILENAME := results

# Documentation variables
DOCS_DIR := docs
DOCS_TITLE := CloudForms Application Sanity Test Suite
DOCS_AUTHOR := Milan Falesnik (mfalesni at redhat.com)
DOCS_VERSION := 1.00

# Variables to control test execution
TEST_ARGS ?= -v -l --junitxml="${RESULTS_FILENAME}.xml" --resultlog="${RESULTS_FILENAME}.log"
TESTNAME ?=
# If a TESTNAME was provided, update TEST_ARGS
ifneq (,$(TESTNAME))
TEST_ARGS += -k "$(TESTNAME)"
endif

.PHONY: bootstrap pack clean doc

bootstrap: ${BUILD_DIR}

# Setup virtualenv
${BUILD_DIR}:
	[ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR)
	wget -P $(BUILD_DIR) https://raw.github.com/pypa/virtualenv/master/virtualenv.py
	python $(BUILD_DIR)/virtualenv.py --system-site-packages $(BUILD_DIR)
	source $(BUILD_DIR)/bin/activate && easy_install pytest sphinx

clean:
	rm -f virtualenv.py *.pyc testsuite/*.pyc
	rm -rf ${BUILD_DIR} $(DOCS_DIR) testsuite/__pycache__

test: bootstrap
	[ -d $(RESULTS_DIR) ] || mkdir -p $(RESULTS_DIR)
	source "$(BUILD_DIR)/bin/activate" && python "$(BUILD_DIR)/bin/py.test" testsuite $(TEST_ARGS)
	for SUFFIX in log xml ; do ln -f -s ${RESULTS_FILENAME}.$$SUFFIX ${RESULTS_DIR}/results.$$SUFFIX ; done

doc_src: bootstrap
	[ -d $(DOCS_DIR) ] || mkdir -p $(DOCS_DIR)
	source "$(BUILD_DIR)/bin/activate" && cd $(DOCS_DIR) && sphinx-apidoc -F -H "${DOCS_TITLE}" -A "${DOCS_AUTHOR}" -V "${DOCS_VERSION}" -f -o ./ ../testsuite/
	source "$(BUILD_DIR)/bin/activate" && cd $(DOCS_DIR) && mv conf.py conf.py.old && echo -ne "import sys\nimport os\nsys.path.insert(0, os.path.abspath('../testsuite'))\n" > conf.py && cat conf.py.old | sed -r -e "s/^import sys, os$///" >> conf.py && rm -f conf.py.old

doc_html: doc_src
	source "$(BUILD_DIR)/bin/activate" && cd $(DOCS_DIR) && make html

doc: doc_html
