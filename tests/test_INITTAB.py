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
    tests around ``/etc/inittab``.
"""

@Test.Mark.skipif("not Test.Fixtures.is_systemd()")
def test_runlevel_systemd():
    """
        Check for correct runlevel when using systemd

    :raises: ``AssertionError``
    """
    symlink = Test.Run.command("readlink -f /etc/systemd/system/default.target")
    assert symlink
    assert symlink.stdout.strip() == "/lib/systemd/system/multi-user.target"

@Test.Mark.skipif("Test.Fixtures.is_systemd()")
def test_runlevel_systemV():
    """
        Check for correct runlevel when using SysV

    :raises: ``AssertionError``
    """
    inittab = Test.Run.command("grep '^id:' /etc/inittab")
    assert inittab
    assert inittab.stdout.strip() == "id:3:initdefault"