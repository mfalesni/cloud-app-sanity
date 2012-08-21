SHELL := /bin/bash
BUILD_DIR := build-dir
JUNITXML := results.xml

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
	source "${BUILD_DIR}/bin/activate" && python "${BUILD_DIR}/bin/py.test" -v --junitxml="${JUNITXML}"

doc:
	epydoc -v --config epydoc.cfg