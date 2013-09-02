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
from conftest import is_systemd

# if (params['product'].upper() == 'RHEL' or params['product'].upper() == 'BETA') and params['version'].startswith('5.'):
# self.ping_pong(connection, 'grep \'^si:\' /etc/inittab', 'si::sysinit:/etc/rc.d/rc.sysinit')

@pytest.mark.skipif("not is_systemd()")
def test_runlevel_systemd():
    symlink = common.shell.Run.command("readlink -f /etc/systemd/system/default.target")
    assert symlink
    assert symlink.stdout.strip() == "/lib/systemd/system/multi-user.target"

@pytest.mark.skipif("is_systemd()")
def test_runlevel_systemV():
    inittab = common.shell.Run.command("grep '^id:' /etc/inittab")
    assert inittab
    assert inittab.stdout.strip() == "id:3:initdefault"