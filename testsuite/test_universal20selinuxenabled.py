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

import common
import pytest

def test_selinux_enabled(selinux_enabled):
    """ Tests whether is SElinux enabled.

    :param selinux_enabled: Whether is Selinux enabled or not
    :type selinux_enabled: ``bool``

    :raises: pytest.Failed
    """
    if not selinux_enabled:
        pytest.fail(msg="SElinux is not enabled!")

def test_selinux_enforcing(selinux_getenforce):
    """ Verifies whether SELinux is in 'Enforcing' state.

    :param selinux_getenforce: Current enforcing status
    :type selinux_getenforce: ``str``

    :raises: pytest.Failed
    """
    try:
        assert selinux_getenforce == "Enforcing"
    except AssertionError:
        pytest.fail(msg="SELinux is not in Enforcing mode!")

def test_selinux_enforcing_from_config(selinux_getenforce_conf):
    """ Verifies whether SELinux is in 'Enforcing' state.
        Checks from config file

    :param selinux_getenforce_conf: Current enforcing status
    :type selinux_getenforce_conf: ``str``

    :raises: pytest.Failed
    """
    try:
        assert selinux_getenforce_conf == "enforcing"
    except AssertionError:
        pytest.fail(msg="SELinux is not in Enforcing mode!")

def test_selinux_is_targeted(selinux_type):
    """ Verifies whether SELinux is in 'targeted' mode.

    :param selinux_type: SELinux mode (targeted)
    :type selinux_type: ``str``

    :raises: pytest.Failed
    """
    try:
        assert selinux_type == "targeted"
    except AssertionError:
        pytest.fail(msg="SELinux is not in Enforcing mode!")

def test_selinux_flip_permissive():
    """ This test sets SELinux to permissive mode

    :raises: pytest.Failed
    """
    try:
        common.selinux.setenforce("Permissive")
    except AssertionError:
        pytest.fail(msg="Setting SELinux into Permissive mode was not successful")

def test_selinux_permissive_check(selinux_getenforce):
    """ Check for success of flip_permissive test.

    :param selinux_getenforce: Current enforcing status
    :type selinux_getenforce: ``str``

    :raises: pytest.Failed
    """
    try:
        assert selinux_getenforce == "Permissive"
    except AssertionError:
        pytest.fail(msg="SELinux is not in Permissive mode")

def test_selinux_flip_enforcing():
    """ This test sets SELinux to enforcing mode

    :raises: pytest.Failed
    """
    try:
        common.selinux.setenforce("Enforcing")
    except AssertionError:
        pytest.fail(msg="Setting SELinux into Enforcing mode was not successful")

def test_selinux_enforcing_check(selinux_getenforce):
    """ Check for success of flip_enforcing test.

    :param selinux_getenforce: Current enforcing status
    :type selinux_getenforce: ``str``

    :raises: pytest.Failed
    """
    try:
        assert selinux_getenforce == "Enforcing"
    except AssertionError:
        pytest.fail(msg="SELinux is not in Enforcing mode")
