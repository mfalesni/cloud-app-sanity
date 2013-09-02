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

import common.shell
import pytest
from conftest import rhel_release

 # self.get_return_value(connection, 'grep \'^root:x:0:0:root:/root:/bin/bash\' /etc/passwd')
        # self.get_return_value(connection, 'grep \'^nobody:x:99:99:Nobody:/:/sbin/nologin\' /etc/passwd')
        # self.get_return_value(connection, 'grep \'^sshd:x:74:74:Privilege-separated SSH:/var/empty/sshd:/sbin/nologin\' /etc/passwd')
        # if params['version'].startswith('5.') or params['version'].startswith('6.0') or params['version'].startswith('6.1') or params['version'].startswith('6.2'):
        #     self.get_return_value(connection, 'grep \'^root:x:0:root\' /etc/group')
        #     self.get_return_value(connection, 'grep \'^daemon:x:2:root,bin,daemon\' /etc/group')
        #     self.get_return_value(connection, 'grep \'^bin:x:1:root,bin,daemon\' /etc/group')
        # elif params['version'].startswith('6.'):
        #     self.get_return_value(connection, 'grep \'^root:x:0:\' /etc/group')
        #     self.get_return_value(connection, 'grep \'^daemon:x:2:bin,daemon\' /etc/group')
        #     self.get_return_value(connection, 'grep \'^bin:x:1:bin,daemon\' /etc/group')
        # return self.log

@pytest.mark.parametrize("line", [
    "root:x:0:0:root:/root:/bin/bash",
    "nobody:x:99:99:Nobody:/:/sbin/nologin",
    "sshd:x:74:74:Privilege-separated SSH:/var/empty/sshd:/sbin/nologin"]
    )
def test_lines_in_passwd(rhel_release, line):
    assert common.shell.Run.command(r"grep '^%s' /etc/passwd" % line)

@pytest.mark.parametrize("group", [
    "root:x:0:",
    "daemon:x:2:bin,daemon",
    "bin:x:1:bin,daemon"]
    )
@pytest.mark.skipif("int(rhel_release()[0]) != 6")
def test_groups_RHEL6(group):
    assert common.shell.Run.command(r"grep '^%s' /etc/group" % group)

@pytest.mark.parametrize("group", [
    "root:x:0:root",
    "daemon:x:2:bin,daemon",
    "bin:x:1:bin,daemon"]
    )
@pytest.mark.skipif("int(rhel_release()[0]) != 5")
def test_groups_RHEL5(group):
    assert common.shell.Run.command(r"grep '^%s' /etc/group" % group)