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

"""
    This file contains tests which can test various aspects around services.
"""

import re
import common.services

class TestServices(object):
    @Test.Fixture
    def chkconfig_list(self):
        """ Returns list of all services with enablement in each runlevel

        :returns: All services.
        :rtype: ``dict``
        """
        result = {}
        services = Test.Run.command("chkconfig --list")
        for line in services.stdout.strip().split("\n"):
            line = re.sub("[[:blank:]]+", "\t", line)
            fields = line.split("\t")
            servicename = fields[0].strip()
            fields = fields[1:]
            result[servicename] = {}
            for field in fields:
                (runlevel, status) = field.split(":")
                runlevel = int(runlevel)
                if status.lower() == "on":
                    status = True
                elif status.lower() == "off":
                    status = False
                else:
                    Test.Fail(msg="Bad parsing of chkconfig --list")
                result[servicename][runlevel] = status
        return result

    @Test.Fixture
    def service_check(self, chkconfig_list):
        """ Produces service-checking fixture """

        class ServiceChecker(object):
            def __init__(self, services):
                self.services = services

            def __call__(self, service, runlevel, active=True):
                """
                    Calls a checking function
                """
                return common.services.service_active_in_runlevel(self.services, service, runlevel, active)

        return ServiceChecker(chkconfig_list)

    #TODO services na novy format
    @Test.Mark.parametrize(("service", "runlevel", "state"), common.services.services_to_test())
    def test_service_enabled(self, service_check, service, runlevel, state):
        """ Tests that all services specified in parametrized/services """
        if not service_check(service, runlevel, state):
            state_message = None
            if state:
                state_message = "active"
            else:
                state_message = "inactive"
            Test.Fail(msg="Service %s is not %s in runlevel %d!" % (service, state_message, runlevel))

    def test_httpd_running(self):
        """
            Checks whether httpd service is running

        :raises: ``AssertionError``
        """
        service = Test.Run.bash("service httpd status")
        assert "is running" in service.stdout, "httpd must be running"

    def test_evm_running(self):
        """
            Checks whether EVM service is running

        :raises: ``AssertionError``
        """
        service = Test.Run.bash("service evmserverd status | grep EVM")
        assert "started" in service.stdout, "evmserverd must be running"
    
    def test_iptables_running(self):
        """
            Checks whether iptables service is running

        :raises: ``AssertionError``
        """
        service = Test.Run.bash("service iptables status")
        assert "is not running" not in service.stdout, "iptables must be running"
    