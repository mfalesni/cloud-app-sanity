CloudForms Applications Sanity Test Suite
================
Maintainer: Milan Falešník <mfalesni@redhat.com>

Documentation: http://mfalesni.github.io/cloud-app-sanity/


Introduction:
=============
Test suite for validating deployed CloudForms applications. It can be also used for validating basically any kind of RHEL system. What can be validated? Current suite validates:
* filesystem (world-writable files, symlinks, ...)
* <code>/etc/passwd</code> (whether it contains only correct records for impotant accounts)
* <code>/etc/inittab</code> validity
* whether specified services are enabled in specified runlevels
* SSL key is enough long and does not use weak hashes
* sshd installed, activ and running
* <code>/bin/bash</code> and <code>/bin/nologin</code> in <code>/etc/shells</code>
* RPM packages signed, all files in packages are correct (hashes, symlinks, ...) and all binaries fortified
* System runs the latest kernel which is installed
* SElinux enabled and Enforcing
* and other (<code>.bash_history</code>, GRUB's <code>menu.lst</code>, ...)

Suite is compatible with these systems:
* RHEL6
* partially RHEL5 (it's not the main focus to support it, but anything I add into the suite runs also on RHEL5)

If you need some case-specific tuning, folder parametrized is used to store parametrization details which can be loaded using py.test switch <code>--parametrize-file=somefile</code>, which will load <code>paraemtrized/somefile.yaml</code>. If no parameter specified, file <code>default.yaml</code> is loaded.

Contribute!
===========
This suite is not finished yet. If you have any idea which could extend the suite, feel free to fork, extend and make a pull request. Before making any changes, look into the test_* files to catch the basic principles and look also in the folder <code>testsuite/plugins</code> which is used to store system-manipulating functions to raise the level of abstraction.

And I really don't like the ninja comments, so please avoid them. If you see any ninja comment in my code, be sure it will disappear soon.

To-Do:
=======
* extend, extend, ...

Prerequisities:
===============
* <code>python (v2.4+)</code>
* <code>python-setuptools</code>
* <code>make</code> - For creating documentation

First two prerequisities are handled with the <code>./starter.sh</code> script as they are necessary

Usage:
======

1. Checkout the git repository
<pre>
git clone git://github.com/mfalesni/cloud-app-sanity.git
</pre>
If you don't have git installed, use this command, which will download repository as a tarball and extract it
<pre>
curl https://raw.github.com/mfalesni/cloud-app-sanity/master/tools/download_suite.sh | bash
</pre>
2. Change into the repository directory
<pre>
cd cloud-app-sanity
</pre>
3. To run the suite using virtualenv and stuff, wrapper <code>starter.sh</code> is used. It wraps <code>py.test</code> call and passes all parameters to it.

With current tests scheme, for example, one can run rpm tests by specifying keywordexpr (<code>-k KEYWORD</code>) as "RPM". Look into <code>tests</code> folder.