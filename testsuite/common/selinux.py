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

import pytest
import common.shell

def setenforce(mode):
    """ Sets enforcing mode of SElinux

    :param mode: Enforcing mode from [Permissive, Enforcing]
    :param type: ``str``
    :raises: AssertionError
    """
    mode = mode.strip().title()
    assert mode in ["Permissive", "Enforcing"]
    result = common.shell.Run.command("/usr/sbin/setenforce %s" % mode)
    assert result

def getenforce():
    """ Returns enforcing mode of SElinux

    :returns: Enforcing mode of SELinux
    :rtype: ``str``
    """
    return common.shell.Run.command("/usr/sbin/getenforce")
