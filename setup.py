import os
import shlex
import time
from setuptools import setup
from setuptools.command.test import test as TestCommand

results_dir = 'results'
results_timestamp = time.strftime("%s", time.localtime())
default_args = '-v -l --tb=short --junitxml=%s/%s.xml --resultlog=%s/%s.log' % \
    (results_dir, results_timestamp, results_dir, results_timestamp)

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True
        self.test_args = shlex.split(os.environ.get('PY_ARGS', default_args))

        if not os.path.isdir(results_dir):
            os.mkdir(results_dir)

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

