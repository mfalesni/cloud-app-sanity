SHELL := /bin/bash
BUILD_DIR := build-dir
RESULTS_FILENAME := results.tgz
RESULTS_DIR := results

# Documentation variables
DOCS_DIR := docs
DOCS_TITLE := CloudForms Application Sanity Test Suite
DOCS_AUTHOR := Milan Falesnik (mfalesni at redhat.com)
DOCS_VERSION := 1.00
DOCS_BRANCH_ROOT := ../cloud-app-sanity-docs/html

# Variables to control test execution parameters
TEST_ARGS ?= -v -l --tb=short
TESTNAME ?=
# If a TESTNAME was provided, update TEST_ARGS
ifneq (,$(TESTNAME))
TEST_ARGS += -k "$(TESTNAME)"
endif

# MAIL_TO variable is used to provide a valid email address to send test
# results
MAIL_TO?=
ifneq (,$(findstring @,$(AUDREY_VAR_KATELLO_REGISTER_NOTIFY_EMAIL)))
MAIL_TO:=$(AUDREY_VAR_KATELLO_REGISTER_NOTIFY_EMAIL)
endif

# For pushing to remote server
PUSH_TARGET?=
ifneq (,$(AUDREY_VAR_KATELLO_REGISTER_AEOLUS_SERVER_RESULTS_LOCATION))
PUSH_TARGET:=$(AUDREY_VAR_KATELLO_REGISTER_AEOLUS_SERVER_RESULTS_LOCATION)
endif

ifeq (,$(PUSH_TARGET))
ifneq (,$(TARGET))
PUSH_TARGET:=$(TARGET)
endif
endif

.PHONY: bootstrap pack clean doc doc_src doc_html doc_git push

bootstrap: ${BUILD_DIR}

# Setup virtualenv
${BUILD_DIR}:
	[ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR)
	cp virtualenv.py $(BUILD_DIR)/virtualenv.py
	python $(BUILD_DIR)/virtualenv.py --system-site-packages $(BUILD_DIR)
	source $(BUILD_DIR)/bin/activate && easy_install pytest sphinx sphinxtogithub

clean:
	rm -f *.pyc testsuite/*.pyc
	rm -rf ${BUILD_DIR} $(DOCS_DIR)/*.rst $(DOCS_DIR)/_* $(DOCS_DIR)/make.bat testsuite/__pycache__

clean_all: clean
	rm -rf "${RESULTS_DIR}/*"

test:
	[ -d $(RESULTS_DIR) ] || mkdir -p $(RESULTS_DIR)
	PY_KEYWORDEXPR="${TESTNAME}" PY_ARGS="${TEST_ARGS}" python setup.py test

doc_src: bootstrap
	[ -d $(DOCS_DIR) ] || mkdir -p $(DOCS_DIR)
	cd "$(DOCS_DIR)" && rm -rf index.rst
	source "$(BUILD_DIR)/bin/activate" && cd $(DOCS_DIR) && sphinx-apidoc -F -H "${DOCS_TITLE}" -A "${DOCS_AUTHOR}" -V "${DOCS_VERSION}" -o ./ ../testsuite/

doc_html: doc_src
	source "$(BUILD_DIR)/bin/activate" && cd $(DOCS_DIR) && make html

doc: doc_html

doc_git: doc_html
	cd $(DOCS_BRANCH_ROOT) && git add * && (git diff --quiet || (git commit -a -m "Doc update" && git pull origin gh-pages && git push origin gh-pages))

${RESULTS_FILENAME}:
	cd ${RESULTS_DIR} && tar cfvz "../${RESULTS_FILENAME}" *.log *.xml

mail: ${RESULTS_FILENAME}
	@[ -n "${MAIL_TO}" ] && (echo "Mailing results: ${MAIL_TO} ..." ; for LOG in ${RESULTS_DIR}/*.log ; do echo "[$${LOG}]" ; cat "$${LOG}" ; done | mail -s "Task finished on ${HOSTNAME}" -a ${RESULTS_FILENAME} "${MAIL_TO}") || echo "No email provided (set MAIL_TO)"


push: ${RESULTS_FILENAME}
	@echo "Pushing to remote server"
	[ -n "${PUSH_TARGET}" ] && scp "${RESULTS_FILENAME}" "${PUSH_TARGET}"

