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
    SYSLOG tests
"""

import pytest
import common.shell
import re

def test_syslog_checksum(rhel_release):
    """
        Check that the file /etc/rsyslog.conf is unchanged.

    :raises: ``AssertionError``
    """
    md5sum = common.shell.Run.command("md5sum /etc/rsyslog.conf")
    assert md5sum, "md5sum on /etc/rsyslog.conf failed, probably does not exist"
    md5sum = md5sum.stdout.strip()[:32]
    if int(rhel_release[0]) == 5:
        assert md5sum in ["bd4e328df4b59d41979ef7202a05e074", "15936b6fe4e8fadcea87b54de495f975"]
    elif int(rhel_release[0]) == 6 and int(rhel_release[1]) in [0,1,2]:
        assert md5sum in ["dd356958ca9c4e779f7fac13dde3c1b5"]
    elif int(rhel_release[0]) == 6:
        assert md5sum in ["8b91b32300134e98ef4aee632ed61e21"]
    else:
        pytest.fail("Unknown version of RHEL (%d.%d)" % rhel_release)

