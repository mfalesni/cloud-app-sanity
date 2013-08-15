CloudForms Applications Sanity Test Suite
================

Test suite for validating deployed CloudForms applications.

Prerequisities:
===============
* <code>python</code>
* <code>python-setuptools</code>
* <code>make</code> - For creating documentation

Usage:
======

1. Checkout the git repository
<pre>
git clone git://github.com/mfalesni/cloud-app-sanity.git
</pre>
If you don't have git installed, use this command, which will download repository as tarball and extract it
<pre>
curl https://raw.github.com/mfalesni/cloud-app-sanity/master/tools/download_suite.sh | bash
</pre>
2. Change into the repository directory
<pre>
cd cloud-app-sanity
</pre>
3. Prepare the environment and run the test suite. You can run all tests with this command:
<pre>
python setup.py test
</pre>
if you want to run only some tests matching a particular expression, you can use this command:
<pre>
PY_KEYWORDEXPR="some-string" python setup.py test
</pre>
Where "some-string" specifies a keyword expression used by py.test to determine which tests to run.  For more information, consult the ''-k KEYWORDEXPR'' parameter to py.test.


Documentation:
==============

The latest (and greatest) version of documentation can be found here:
<pre>
http://mfalesni.github.com/cloud-app-sanity/
</pre>

It's updated usually after bigger changes in codebase.