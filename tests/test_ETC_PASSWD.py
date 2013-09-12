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
    File containing tests around /etc/passwd and /etc/group
"""

@Test.Mark.parametrize("line", [
    "root:x:0:0:root:/root:/bin/bash",
    "nobody:x:99:99:Nobody:/:/sbin/nologin",
    "sshd:x:74:74:Privilege-separated SSH:/var/empty/sshd:/sbin/nologin"]
    )
def test_lines_in_passwd(line):
    """
        This test checks whether important accounts are correctly specified

    :raises: ``AssertionError``
    """
    assert Test.Run.command(r"grep '^%s' /etc/passwd" % line)

@Test.Mark.parametrize("group", [
    "root:x:0:",
    "daemon:x:2:bin,daemon",
    "bin:x:1:bin,daemon"]
    )
@Test.Mark.skipif("int(rhel_release()[0]) != 6")
def test_groups_RHEL6(group):
    """
        This test checks whether important groups are correctly specified.
        RHEL6 variant.

    :raises: ``AssertionError``
    """
    assert Test.Run.command(r"grep '^%s' /etc/group" % group)

@Test.Mark.parametrize("group", [
    "root:x:0:root",
    "daemon:x:2:bin,daemon",
    "bin:x:1:bin,daemon"]
    )
@Test.Mark.skipif("int(Test.Fixtures.rhel_release()[0]) != 5")
def test_groups_RHEL5(group):
    """
        This test checks whether important groups are correctly specified.
        RHEL5 variant.

    :raises: ``AssertionError``
    """
    assert Test.Run.command(r"grep '^%s' /etc/group" % group)