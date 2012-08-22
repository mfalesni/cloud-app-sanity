CloudForms Applications Sanity Test Suite
================

Test suite for validating deployed CloudForms applications.

Prerequisities:
===============
* <pre>make</pre>

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
make test
</pre>
But if you want to run only some particular tests, you can use this command:
<pre>
GREP="some-string" make test_grep
</pre>
Where "some-string" specifies the string, which must be contained in file name in order to run the tests. So for example <pre>GREP="99" make test_grep</pre> will run only those tests contained in file test_99unregister.py. It behaves like normal grep, just without regexps. Applies on files, not test functions itself (at least I hope so).


Documentation:
==============

You can generate documentation from sources:

1. Remove any sphinx in your computer
<pre>
yum remove python-sphinx*
</pre>
2. Install latest sphinx
<pre>
easy_install_sphinx
</pre>
3. Generate documentation
<pre>
make doc_html
</pre>