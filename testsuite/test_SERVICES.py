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

import common.services

class TestServices(object):
    @Test.Fixture
    def test_services_enabled(self, services_to_test):
        """ Tests that all services specified in parametrized/services """
        failed = []
        for service in services_to_test:
            if not self.verify_service(*service):
                state_message = None
                if service[-1]:
                    state_message = "active"
                else:
                    state_message = "inactive"
                failed.append("Service %s at runlevel %d is not %s!" % (service[0], service[1], state_message))
        if len(failed) > 0:
            Test.Fail("\n".join(failed))

    def verify_service(self, service, runlevel, state):
        return Test.System.service_active_in_runlevel(service, runlevel, state)