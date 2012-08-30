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
if you want to run only some tests matching a particular expression, you can use this command:
<pre>
TESTNAME="some-string" make test
</pre>
Where "some-string" specifies a keyword expression used by py.test to determine which tests to run.  For more information, consult the ''-k KEYWORDEXPR'' parameter to py.test.


Documentation:
==============

The latest (and greatest) version of documentation can be found here:
<pre>
http://mfalesni.github.com/cloud-app-sanity/
</pre>

It's updated usually one time a day (can be more times but I am too lazy to push it :) Maybe I will script it somehow) when documentation changes somehow.

But you can generate documentation from sources, if you want:

At first, you need to change docs/Makefile. Change line:
<pre>
BUILDDIR      = /home/mfalesni/git/cloud-app-sanity-docs
</pre>
Change it according to your needs

Fire up this command (in base directory, not in docs!):
<pre>
make doc_html
</pre>

This will put the HTML output into
<pre>
selected_directory/html
</pre>
