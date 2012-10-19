import os
import shlex
from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True
        self.test_args = shlex.split(os.environ.get('PY_ARGS', '-v -l --tb=short'))
        if os.environ.has_key('PY_KEYWORDEXPR'):
            self.test_args.extend(shlex.split('-k "%s"' % os.environ.get('PY_KEYWORDEXPR')))
        self.test_args.extend(shlex.split(os.environ.get('PY_TESTS', 'testsuite')))

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded elsewhere
        import pytest
        print "Running: pytest %s" % " ".join(self.test_args)
        pytest.main(self.test_args)

setup(
    #...,
    name="cloud-app-sanity",
    tests_require=['pytest', 'sphinx', 'sphinxtogithub'],
    cmdclass = {'test': PyTest,}
                # 'build_sphinx': BuildSphinx},
    )

