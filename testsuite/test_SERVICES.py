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
import re
import common.services
import common.shell

class TestServices(object):
    @pytest.fixture
    def chkconfig_list(self):
        """ Returns list of all services with enablement in each runlevel

        :returns: All services.
        :rtype: ``dict``
        """
        result = {}
        services = common.shell.Run.command("chkconfig --list")
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
                    pytest.fail(msg="Bad parsing of chkconfig --list")
                result[servicename][runlevel] = status
        return result

    @pytest.fixture
    def service_check(self, chkconfig_list):
        """ Produces service-checking fixture """

        class ServiceChecker(object):
            def __init__(self, services):
                self.services = services

            def __call__(self, service, runlevel, active=True):
                return common.services.service_active_in_runlevel(self.services, service, runlevel, active)

        return ServiceChecker(chkconfig_list)

    @pytest.mark.parametrize(("service", "runlevel", "state"), common.services.services_to_test())
    def test_service_enabled(self, service_check, service, runlevel, state):
        """ Tests all services specified in parametrized/services """
        if not service_check(service, runlevel, state):
            pytest.fail(msg="Service %s is not %s in runlevel %d!" % (service, ["active", "inactive"][0 if state else 1], runlevel))