#!/usr/bin/env python2
#   Author(s): Milan Falesnik <mfalesni@redhat.com>
#              James Laska <jlaska@redhat.com>
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

""" This module contains tests, which are used to unregister and cleanup tasks.

"""

import common.shell
import common.tools
import pytest

@pytest.mark.skipif("True")
def test_audreyvars(audreyvars):
    """ This test checks for presence of audrey environment variables.
        It's checked here again because of possibility to invoke tests separately.

    :param audreyvars: Dict of audrey environment variables
    :type audreyvars: dict

    :raises: AssertionError
    """
    assert len(audreyvars) > 0


@pytest.mark.skipif("True")
def test_unregister():
    """This test unregisters system from Katello.

    :raises: AssertionError
    """
    common.shell.run("subscription-manager unregister")

@pytest.mark.skipif("True")
def test_verify_unregistered():
    """This test verifies that the system was unregistered from Katello.

    :raises: AssertionError
    """
    common.shell.run("subscription-manager unregister", 1)    # SM unreg. returns 1 when not registered

@pytest.mark.skipif("True")
def test_uninstall_cert(audreyvars):
    """This test uninstalls Candlepin customer certificate.

    :param audreyvars: Dict of audrey environment variables
    :type audreyvars: dict

    :raises: AssertionError
    """
    cert_rpm = common.tools.s_format("candlepin-cert-consumer-{KATELLO_HOST}", audreyvars)
    cmd = "rpm -e %s" % cert_rpm
    common.shell.run(cmd)
