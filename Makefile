SHELL := /bin/bash
BUILD_DIR := build-dir
JUNITXML := results.xml
DOCS_TITLE := CloudForms Integration Sanity Test Suite
DOCS_AUTHOR := Milan Falesnik (mfalesni at redhat.com)
DOCS_VERSION := 1.00

.PHONY: bootstrap pack clean doc

bootstrap: bootstrap.py ${BUILD_DIR}

bootstrap.py: virtualenv.py
	./genbootstrap.py

virtualenv.py:
	wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py

${BUILD_DIR}:
	./boot.sh -d ${BUILD_DIR} pytest

clean:
	rm -f bootstrap.py virtualenv.py *.pyc testsuite/*.pyc
	rm -rf ${BUILD_DIR} testsuite/__pycache__

test: bootstrap
	source "${BUILD_DIR}/bin/activate" && python "${BUILD_DIR}/bin/py.test" testsuite -v -l --junitxml="${JUNITXML}"

test_grep: bootstrap
	@echo "Testing files with '${GREP}' in their names" 
	source "${BUILD_DIR}/bin/activate" && python "${BUILD_DIR}/bin/py.test" testsuite -v -l --junitxml="${JUNITXML}" -k "${GREP}"

doc_src:
	mkdir -p docs
	cd docs && sphinx-apidoc -F -H "${DOCS_TITLE}" -A "${DOCS_AUTHOR}" -V "${DOCS_VERSION}" -f -o ./ ../testsuite/
	cd docs && mv conf.py conf.py.old && echo -ne "import sys\nimport os\nsys.path.insert(0, os.path.abspath('../testsuite'))\n" > conf.py && cat conf.py.old | sed -r -e "s/^import sys, os$///" >> conf.py && rm -f conf.py.old

doc_html: doc_src
	cd docs && make html
