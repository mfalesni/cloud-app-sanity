SHELL := /bin/bash
BUILD_DIR := build-dir
RESULTS_FILENAME := results.tar.gz
RESULTS_DIR := ./results-dir

# RHUI QE valid suite
VALID_DIR := valid
VALID_TARBALL_URL := https://github.com/mfalesni/valid/tarball/master
VALID_TARBALL := valid.tar.gz


# Documentation variables
DOCS_DIR := docs
DOCS_TITLE := CloudForms Application Sanity Test Suite
DOCS_AUTHOR := Milan Falesnik (mfalesni at redhat.com)
DOCS_VERSION := 1.00
DOCS_BRANCH_ROOT := ../cloud-app-sanity-docs/html

# Variables to control test execution
TEST_ARGS ?= -v -l
TESTNAME ?=
# If a TESTNAME was provided, update TEST_ARGS
ifneq (,$(TESTNAME))
TEST_ARGS += -k "$(TESTNAME)"
endif

# Make test file name from date and TESTNAME
# If no TESTNAME provided, use word default
ifeq (,$(TESTNAME))
TESTRESULT :=default
endif

TESTRESULT:=`(date +"%y%m%d.%H%M%S"; echo ${TESTNAME} | sed -r -e "s/[^a-z-]/_/g") | tr -d '\n'`

TEST_ARGS+=--junitxml="${RESULTS_DIR}/${TESTRESULT}.xml" --resultlog="${RESULTS_DIR}/${TESTRESULT}.log"

# For pushing to remote server
TESTNAME ?=
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

bootstrap: ${BUILD_DIR} ${VALID_DIR}

# Download "valid" suite
${VALID_DIR}:
	mkdir ${VALID_DIR}
	wget -O "${VALID_DIR}/${VALID_TARBALL}" "${VALID_TARBALL_URL}"
	cd ${VALID_DIR} && tar xfvz ${VALID_TARBALL} --strip-components=1 && rm ${VALID_TARBALL}

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

${RESULTS_FILENAME}: 
	cd ${RESULTS_DIR} && tar cfvz "../${RESULTS_FILENAME}" *.log *.xml

push: ${RESULTS_FILENAME}
	@echo "Pushing to remote server"
	[ -n "${PUSH_TARGET}" ] && scp "${RESULTS_FILENAME}" "${PUSH_TARGET}"

