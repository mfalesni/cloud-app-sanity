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

""" Tests around grub

"""

def test_menu_lst_exists():
    """
        Test which checks whether ``menu.lst`` exists.

    :raises: ``AssertionError``
    """
    assert Test.Run.command("test -h /boot/grub/menu.lst"), "/boot/grub/menu.lst does not exist"

def test_symlink_menu_lst():
    """
        Test which checks whether ``menu.lst`` is a symlink to ``/boot/grub/grub.conf``.

    :raises: ``AssertionError``
    """
    symlink = Test.Run.command("readlink -e /boot/grub/menu.lst")
    assert symlink
    assert symlink.stdout.strip() == "/boot/grub/grub.conf", "/boot/grub/menu.lst is not a symlink to /boot/grub/grub.conf"