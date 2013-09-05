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
import common.elf
import re

class TestRPM(object):
    
    @staticmethod
    def packages_that_must_be_installed():
        """ Reads all rules from file parametrized/packages_installed for purposes of parametrizing of the testing

        :raises: ``IOError``
        """
        try:
            f = open("parametrized/packages_installed", "r")
        except IOError:
            f = open("../parametrized/packages_installed", "r") # For testing purposes
        lines = [re.sub(r"\s+", "\t", re.sub(r"#[^#]*$", "", x.strip())).strip() for x in f.readlines()] # Remove comments and normalize blank spaces into tabs
        f.close()
        return [line for line in lines if len(line) > 0] # remove blank lines

    @Test.Mark.skipif("os.environ.get('SKIP_SIGNATURE_CHECK', 'false').strip() == 'true'")
    @Test.Mark.parametrize("package", Test.Fixtures.rpm_package_list())
    def test_signed(self, package):
        """ This test checks a package whether it has a signature.

        :param package: package to be checked
        :type package: ``str``

        :raises: AssertionError
        """
        assert Test.RPM.package_signed(package), "Package %s is not signed!" % (package,)

    @Test.Mark.parametrize("package", Test.Fixtures.rpm_package_list())
    def test_files(self, package):
        """ This test checks a package whether all files are ok.
            It also checks the return code of rpm -Vvv.

        :param package: package to be checked
        :type package: ``str``

        :raises: AssertionError
        """
        problems = common.rpm.verify_package_files(package)
        assert len(problems) == 0, "Package %s had following problems: '%s'" % (package, ", ".join(problems))


    #TODO FINISH!!!!!!!!!!!
    @Test.Mark.parametrize("package", Test.Fixtures.rpm_package_list())
    def test_fortified(self, package):
        """ This test checks whether are all compiled files in package fortified.
            This test is still not completed as I don't have all required informations.

        :param package: Package name
        :type package: ``list``

        :raises: pytest.Failed
        """

        # FIXME - Review rpm-chksec
        # (http://people.redhat.com/sgrubb/files/rpm-chksec) coverage to determine
        # whether adjustments/enhancements are needed
        # problems = []
        # files = common.rpm.ql(package).strip().split("\n")
        # for f in files:
        #     if common.elf.is_elf(f):
        #         dangerous = common.elf.fortify_find_dangerous(f)
        #         for function in dangerous:
        #             if not function.endswith("_chk") and not function.endswith("__chk_fail"):
        #                 problems.append((f, function, "dangerous call"))
        # assert len(problems) == 0, "Problems found:\n" + "\n".join(["%s@%s | %s" % (x[1], x[0], x[2]) for x in problems])
        # Alternate
        files = common.rpm.ql(package).strip().split("\n")
        was_elf = False
        for f in files:
            if common.elf.is_elf(f):
                failed = False
                was_elf = True
                dangerous = common.elf.fortify_find_dangerous(f)
                if len(dangerous) > 0:
                    failed = True
                for function in dangerous:
                    if function.endswith("_chk") or function.endswith("__chk_fail"):
                        failed = False
                assert not failed, "File %s has problem with fortification!" % f
        if not was_elf:
            Test.Skip(msg="No binary present in this package")

    @Test.Mark.parametrize("package", TestRPM.packages_that_must_be_installed())
    def test_whether_package_installed(self, package):
        """
            This test tests whether required packages are present

        :raises: ``AssertionError``
        """
        assert Test.RPM.query(package), "Package %s has to be installed!!" % package
        