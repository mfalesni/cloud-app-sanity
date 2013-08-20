#!/usr/bin/env python2
#   Author(s): Milan Falesnik <mfalesni@redhat.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2013 Red Hat, Inc. All rights reserved.
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

"""
    This file contains class which tests each RPM package in the system.
"""

import pytest
import common.rpm
import conftest as fixtures

@pytest.mark.parametrize("package", fixtures.rpm_package_list())
class TestRPM(object):
    def test_signed(self, package):
        """ This test checks a package whether it has signature.

        :param package: package to be checked
        :type package: ``str``

        :raises: AssertionError
        """
        problems = common.rpm.verify_package_signed(package)
        assert len(problems) == 0, "Package %s had following problems: '%s'" % (package, ", ".join(problems))

    def test_files(self, package):
        """ This test checks a package whether all files are ok.
            It also checks the return code of rpm -Vvv.

        :param package: package to be checked
        :type package: ``str``

        :raises: AssertionError
        """
        problems = common.rpm.verify_package_files(package)
        assert len(problems) == 0, "Package %s had following problems: '%s'" % (package, ", ".join(problems))

    def test_fortified(self, package):
        """ This test checks whether are all compiled files in package fortified.

        :param package: Package name
        :type package: ``list``

        :raises: pytest.Failed
        """

        # FIXME - Review rpm-chksec
        # (http://people.redhat.com/sgrubb/files/rpm-chksec) coverage to determine
        # whether adjustments/enhancements are needed

        files = common.rpm.ql(package).strip().split("\n")
        for f in files:
            if common.elf.is_elf(f):
                dangerous = common.elf.fortify_find_dangerous(f)
                for function in dangerous:
                    if not function.endswith("_chk") and not function.endswith("__chk_fail"):
                        pytest.fail(msg="File %s: Symbol '%s' found! All relevant symbols in file: %s" % (f, function, dangerous))