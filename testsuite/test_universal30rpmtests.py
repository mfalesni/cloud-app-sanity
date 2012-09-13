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

import common
import pytest
import sys

def test_packages_installed_against_list(rpm_package_list_name, rhel_release):
    """ Tests whether there are only exact packages installed in the system.

    :param rpm_package_list_name: Package list with names only
    :param rpm_package_list_name: ``list``

    :raises: pytest.Failed
    """
    major, minor = rhel_release
    rhel6pkgfilelist = {"0": "packages_6","1": "packages_61","2": "packages_62","3": "packages_63"}
    packagelist = None
    try:
        if major == "5":
            # RHEL5 packages
            packagelist = common.run("cat data/packages_5")
        elif major == "6":
            # RHEL6 packages
            try:
                packagelist = common.run("cat data/%s" % rhel6pkgfilelist[minor])
            except KeyError:
                pytest.fail("Unknown version of RHEL! (major: %s, minor: %s)" % rhel_release)
    except AssertionError:
        pytest.fail(msg="Unable to find file according to your RHEL version (major: %s minor: %s)" % rhel_release)
    packagelist = packagelist.strip().split("\n")
    not_installed_packages = []
    while len(packagelist) > 0:
        # Pop out checked packages
        pkg = packagelist.pop()
        if pkg not in rpm_package_list_name:
            not_installed_packages.append(pkg)
        else:
            del rpm_package_list_name[rpm_package_list_name.index(pkg)]
    if len(not_installed_packages) > 0:
        pytest.fail(msg="Some packages, which should have been installed weren't installed: %s" % str(not_installed_packages))

    if len(rpm_package_list_name) > 0:
        pytest.fail(msg="There are packages in this system, which aren't supposed to be installed: %s" % str(rpm_package_list_name))
    



def test_check_all_packages(rpm_package_list):
    """ This test checks all packages in system.

    :param rpm_package_list: List of all packages installed in system
    :type rpm_package_list: ``list``

    :raises: pytest.Failed
    """
    failed = False
    for package in rpm_package_list:
        if not common.rpm_verify_package(package):
            sys.stderr.write("Package %s:\n%s" % (package, common.rpm_package_problems(package)))
            failed = True
    if failed:
        pytest.fail(msg="Some packages had problem!")
