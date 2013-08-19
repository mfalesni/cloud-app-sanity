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
import common.services

@pytest.mark.parametrize(("service", "runlevel", "state"), common.services.services_to_test())
def test_service_enabled(service_check, service, runlevel, state):
    """ Tests all services specified in parametrized/services """
    if not service_check(service, runlevel, state):
        pytest.fail(msg="Service %s is not %s in runlevel %d!" % (service, ["active", "inactive"][0 if state else 1], runlevel))