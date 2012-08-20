CloudForms Applications Sanity Test Suite
================

Test suite for validating deployed CloudForms applications.


Usage:
======

1. git clone git://github.com/mfalesni/cloud-app-sanity.git
2. cd into git repo
3. make bootstrap # Will prepare own python environment
4. tests are launched with ./runtests.sh . It's wrapper around py.test command to provide right environment, so feel free to provide it command-line options like it was py.test

Look into settings.cfg. There you can tune some properties of this process (log directory etc.)

If you don't have git, you can use this set of commands instead of step 1:

wget -O master.zip https://github.com/mfalesni/cloud-app-sanity/zipball/master && unzip master.zip && mv mfalesni-cloud-app-sanity-* cloud-app-sanity && rm master.zip

But do it only in clean directory, otherwise FFUUUU (mv) :)