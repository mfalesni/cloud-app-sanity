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

"""
    Tests using uname
"""

import re

#TODO!! Doplnit

def test_uname_o_gnu_linux():
    """
        Test that system reports it is GNU/Linux

    :raises: ``AssertionError``
    """
    uname = Test.Run.command("uname -o")
    assert uname, "uname failed!"
    assert uname.stdout.strip() == "GNU/Linux", "uname -o shoul equal to GNU/Linux"

@Test.Mark.skipif("not Test.RPM.is_package_installed('kernel')")
def test_kernel_latest_version_is_running():
    """
        This test checks whether system runs on a kernel, which is latest installed.

    :raises: ``AssertionError``
    """
    uname_r = Test.Run.command("uname -r")
    uname_r.AssertRC()
    uname_r = uname_r.stdout.strip()
    last_kernel = Test.Run.command("rpm -q --last kernel")
    last_kernel.AssertRC()
    last_kernel = last_kernel.stdout.strip().split("\n")[0]
    last_kernel = re.split(r"\s+", last_kernel, 1)[0]
    last_kernel = re.sub(r"^kernel-", "", last_kernel)
    print uname_r, last_kernel
    assert uname_r == last_kernel, "Running kernel (%s) does not match latest installed kernel (%s)!" % (uname_r, last_kernel)

@Test.Mark.skipif("not Test.RPM.is_package_installed('kernel-xen')")
def test_kernel_latest_XEN_version_is_running():
    """
        This test checks whether system runs on a kernel, which is latest installed.
        For xen kernel.

    :raises: ``AssertionError``
    """
    uname_r = Test.Run.command("uname -r")
    uname_r.AssertRC()
    uname_r = uname_r.stdout.strip()
    last_kernel = Test.Run.command("rpm -q --last kernel-xen")
    last_kernel.AssertRC()
    last_kernel = last_kernel.stdout.strip().split("\n")[0] #
    last_kernel = re.split(r"\s+", last_kernel, 1)[0]       # Drop the date field
    last_kernel = re.sub(r"^kernel-xen-", "", last_kernel)  # Strip the beginning
    assert uname_r == last_kernel, "Running kernel (%s) does not match latest installed kernel (%s)!" % (uname_r, last_kernel)