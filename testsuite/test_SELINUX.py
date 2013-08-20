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

import pytest
import common.selinux

class TestSelinux(object):
    @classmethod
    def setup_class(cls):
        cls.original_enforce = common.selinux.getenforce()

    @classmethod
    def teardown_class(cls):
        common.selinux.setenforce(cls.original_enforce)

    @pytest.fixture
    def enforcing(self):
        common.selinux.setenforce("Enforcing")

    @pytest.fixture
    def permissive(self):
        common.selinux.setenforce("Permissive")

    @pytest.fixture
    def enabled(self):
        """ Detects whether is SElinux enabled or not

        :returns: SElinux status
        :rtype: ``bool``
        """
        try:
            common.shell.run("selinuxenabled")
            return True
        except AssertionError:
            return False

    @pytest.fixture
    def getenforce(self):
        """ Returns current enforcing mode of SELinux

        :returns: SElinux enforcing status
        :rtype: ``str``
        """
        return common.shell.run("/usr/sbin/getenforce").strip()

    @pytest.fixture
    def getenforce_conf(self):
        """ Returns current enforcing mode of SELinux from config file

        :returns: SElinux enforcing status
        :rtype: ``str``
        """
        f = open("/etc/sysconfig/selinux", "r")
        lines = []
        for line in f.readlines():
            if line.startswith("SELINUX="):
                lines.append(line)
        f.close()
        # Check whether is only one
        assert len(lines) == 1
        return lines[0].split("=")[1].strip()

    @pytest.fixture
    def mode(self):
        """ Returns current SELINUX type/mode from config file

        :returns: SElinux type
        :rtype: ``str``
        """
        f = open("/etc/sysconfig/selinux", "r")
        lines = []
        for line in f.readlines():
            if line.startswith("SELINUXTYPE="):
                lines.append(line)
        f.close()
        # Check whether is only one
        assert len(lines) == 1
        return lines[0].split("=")[1].strip()

    def test_enabled(self, enabled):
        """ Tests whether is SElinux enabled.

        :param enabled: Whether is Selinux enabled or not
        :type enabled: ``bool``

        :raises: pytest.Failed
        """
        if not enabled:
            pytest.fail(msg="SElinux is not enabled!", pytrace=False)

    def test_enforcing(self, getenforce):
        """ Verifies whether SELinux is in 'Enforcing' state.

        :param getenforce: Current enforcing status
        :type getenforce: ``str``

        :raises: pytest.Failed
        """
        try:
            assert getenforce == "Enforcing"
        except AssertionError:
            pytest.fail(msg="SELinux is not in Enforcing mode!", pytrace=False)

    def test_enforcing_from_config(self, getenforce_conf):
        """ Verifies whether SELinux is in 'Enforcing' state.
            Checks from config file

        :param getenforce_conf: Current enforcing status
        :type getenforce_conf: ``str``

        :raises: pytest.Failed
        """
        try:
            assert getenforce_conf == "enforcing"
        except AssertionError:
            pytest.fail(msg="SELinux is not in Enforcing mode!", pytrace=False)

    def test_is_targeted(self, mode):
        """ Verifies whether SELinux is in 'targeted' mode.

        :param selinux_type: SELinux mode (targeted)
        :type selinux_type: ``str``

        :raises: pytest.Failed
        """
        try:
            assert mode == "targeted"
        except AssertionError:
            pytest.fail(msg="SELinux is not in Enforcing mode!", pytrace=False)

    def test_permissive_check(self, permissive, getenforce):
        """ Check for success of flip_permissive test.

        :param selinux_getenforce: Current enforcing status
        :type selinux_getenforce: ``str``

        :raises: pytest.Failed
        """
        try:
            assert getenforce == "Permissive"
        except AssertionError:
            pytest.fail(msg="SELinux is not in Permissive mode", pytrace=False)

    def test_enforcing_check(self, enforcing, getenforce):
        """ Check for success of flip_enforcing test.

        :param selinux_getenforce: Current enforcing status
        :type selinux_getenforce: ``str``

        :raises: pytest.Failed
        """
        try:
            assert getenforce == "Enforcing"
        except AssertionError:
            pytest.fail(msg="SELinux is not in Enforcing mode", pytrace=False)