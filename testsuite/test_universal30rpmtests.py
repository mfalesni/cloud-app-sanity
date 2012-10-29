#!/usr/bin/env python2
#   Author(s): Milan Falesnik <mfalesni@redhat.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2012 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys
import pytest
import common.elf
import common.rpm
import common.shell
import common.yum

def test_packages_installed_against_list(rpm_package_list_names, rhel_release):
    """ Tests whether there are only exact packages installed in the system.

    :param rpm_package_list_names: Package list with names only
    :param rpm_package_list_names: ``list``

    :raises: pytest.Failed
    """
    major, minor = rhel_release
    rhel6pkgfilelist = {"0": "packages_6","1": "packages_61","2": "packages_62","3": "packages_63"}
    packagelist = None
    try:
        if major == "5":
            # RHEL5 packages
            packagelist = common.shell.run("cat data/packages_5")
        elif major == "6":
            # RHEL6 packages
            try:
                packagelist = common.shell.run("cat data/%s" % rhel6pkgfilelist[minor])
            except KeyError:
                pytest.fail("Unknown version of RHEL! (major: %s, minor: %s)" % rhel_release)
    except AssertionError:
        pytest.fail(msg="Unable to find file according to your RHEL version (major: %s minor: %s)" % rhel_release)
    packagelist = packagelist.strip().split("\n")
    not_installed_packages = []
    while len(packagelist) > 0:
        # Pop out checked packages
        pkg = packagelist.pop()
        if pkg not in rpm_package_list_names:
            not_installed_packages.append(pkg)
        else:
            del rpm_package_list_names[rpm_package_list_names.index(pkg)]
    if len(not_installed_packages) > 0:
        pytest.fail(msg="Some packages, which should have been installed weren't installed: %s" % str(not_installed_packages))

    if len(rpm_package_list_names) > 0:
        pytest.fail(msg="There are packages in this system, which aren't supposed to be installed: %s" % str(rpm_package_list_names))

def test_gpg_check(gpgcheck_enabled):
    """ Tests whether is GPG check enabled in YUM

    :param gpgcheck_enabled: Whether is GPG check active
    :type gpgcheck_enabled: ``bool``

    :raises: pytest.Failed
    """
    try:
        assert gpgcheck_enabled == True
    except AssertionError:
        pytest.fail(msg="GPG check is not enabled")

@pytest.mark.parametrize("package", common.rpm.qa().strip().split("\n"))
def test_check_all_packages(package):
    """ This test checks all packages in system.

    :param package: package to be checked
    :type package: ``str``

    :raises: pytest.Failed
    """
    if not common.rpm.verify_package(package):
        pytest.fail(msg="Package had problem: '%s'" % common.rpm.package_problems(package))

@pytest.mark.parametrize("package", common.rpm.qa().strip().split("\n"))
def test_check_all_packages_files_fortified(package):
    """ This test checks whether are all compiled files in package fortified

    :param package: Package name
    :type package: ``list``

    :raises: pytest.Failed
    """
    files = common.rpm.ql(package).strip().split("\n")
    for f in files:
        if common.elf.is_elf(f):
            dangerous = common.elf.fortify_find_dangerous(f)
            for function in dangerous:
                if not function.endswith("_chk") and not function.endswith("__chk_fail"):
                    pytest.fail(msg="File %s: Symbol '%s' found! All relevant symbols in file: %s" % (f, function, dangerous))

def test_yum_full_test(rhel_release):
    """ This test tests yum thoroughly

    :param rhel_release: Version release of RHEL
    :type rhel_release: ``tuple``

    :raises: pytest.Failed
    """
    # Package to check
    pkg = "redhat-release-server"
    if int(rhel_release[0]) == 5:
        pkg = "redhat-release"
    if common.yum.check_update(pkg):
        print "Update for %s is available" % pkg
    else:
        print "No update available for %s" % pkg
    print common.yum.repolist()
    print common.yum.search("zsh")
    print common.yum.install("zsh")
    assert common.rpm.package_installed("zsh")
    print common.yum.grouplist()
    print common.yum.groupinstall("Development tools")
    print common.yum.update()
    print common.rpm.e("zsh")
    assert not common.rpm.package_installed("zsh")




    
