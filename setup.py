import os
import glob
import shutil
import shlex
import time
from setuptools import setup,Command
from setuptools.command.test import test as TestCommand

results_dir = 'results'
results_timestamp = time.strftime("%s", time.localtime())
default_args = '-v -l --tb=native --junitxml=%s/%s.xml --resultlog=%s/%s.log' % \
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

class CleanCommand(Command):
    description = "Custom clean command that forcefully removes dist/build directories"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        # Remove all .pyc files
        for root, dirs, files in os.walk(self.cwd, topdown=False):
            for fname in files:
                if fname.endswith('.pyc') and os.path.isfile(os.path.join(root, fname)):
                    if self.verbose: print 'removing: %s' % os.path.join(root, fname)
                    if not self.dry_run: os.remove(os.path.join(root, fname))
        # Remove egg's
        for egg_dir in glob.glob('*.egg') + \
                       glob.glob('*egg-info'):
            if self.verbose: print "Removing '%s' ..." % egg_dir
            if not self.dry_run: shutil.rmtree(egg_dir)
setup(
    name="cloud-app-sanity",
    tests_require=open('requirements.txt', 'r').readlines(),
    cmdclass = {'test': PyTest,
                'clean': CleanCommand,
                # 'build_sphinx': BuildSphinx},
               }
    )

