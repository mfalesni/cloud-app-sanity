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

""" This file contains methods used for testing services (init.d/) """

import re

def services_to_test():
    """ Reads all rules from file parametrized/services for purposes of parametrizing of the testing

    :raises: ``IOError``
    """
    try:
        f = open("parametrized/services", "r")
    except IOError:
        f = open("../parametrized/services", "r") # For testing purposes
    lines = [re.sub(r"\s+", "\t", re.sub(r"#[^#]*$", "", x.strip())).strip() for x in f.readlines()] # Remove comments and normalize blank spaces into tabs
    f.close()
    lines = [line for line in lines if len(line) > 0] # remove blank lines
    resulting_rules = {}
    for rule in lines:
        srv_name, params = rule.split("\t", 1)
        params = params.split("\t")
        # No multiple entries
        if srv_name in resulting_rules:
            raise Exception("Service %s already exists in the list (line '%s')" % (srv_name, rule))
        resulting_rules[srv_name] = {}
        # Parameters are always pair runlevel -> state
        if len(params) % 2 != 0:
            raise Exception("Count of parameters for service must be even (line '%s')" % rule)
        # Ugly lambda, however does iterate over the array taking the right pairs
        for runlevel, status in (lambda iterable : [(iterable[i], iterable[i+1]) for i in range(0, len(iterable)-1, 2)])(params):   # [a,b,c,d] -> [a,b], [c,d]
            if status.lower() in ["yes", "y"]:
                status = True
            elif status.lower() in ["no", "n"]:
                status = False
            else:
                raise Exception("Unknown value '%s' at line '%s'" % (status, rule))
            try:
                runlevel = int(runlevel)
            except ValueError:
                raise Exception("Runlevel '%s' at line '%s' is not a number!" % (runlevel, rule))
            resulting_rules[srv_name][runlevel] = status
    tupled_rules = []
    # Make tuples from dict
    for service in resulting_rules:
        for runlevel, state in resulting_rules[service].iteritems():
            tupled_rules.append((service, runlevel, state))
    return tupled_rules




def service_active_in_runlevel(chkconfig_list, service, runlevel, active=True):
    """ Does the check of service presence in desired runlevels

    :param chkconfig_list: ``dict`` from ``pytest_funcarg__chkconfig_list`` - list of all chkconfig services details injected by py.test
    :type chkconfig_list: ``dict``

    :param service: Service name
    :type service: ``str``

    :param runlevel: Integers of desired runlevel
    :type runlevel: Iterable (``tuple``, ``list``)

    :param active: Report active OR inactive in particular runlevel
    :type runlevel: ``bool``

    :returns: Whether the service is active in specified runlevel
    :rtype: ``bool``

    :raises: ``KeyError``
    """
    if chkconfig_list[service][runlevel] != active:
        return False

    return True