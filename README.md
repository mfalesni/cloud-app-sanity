CloudForms Applications Sanity Test Suite
================

Test suite for validating deployed CloudForms applications.


Usage:
======

1. git clone git://github.com/mfalesni/cloud-app-sanity.git
2. cd into git repo
3. make bootstrap # Will prepare own python environment
4. tests are launched with ./test.sh . It's wrapper around py.test command to provide right environment, so feel free to provide it command-line options like it was py.test

Look into settings.cfg. There you can tune some properties of this process (log directory etc.)
