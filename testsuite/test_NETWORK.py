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
    This module contains tests targeted on system hardware and so.
"""

import pytest
import common.shell
import re

#TODO parametrize externally
@pytest.mark.parametrize(("rule"),[
    ("ACCEPT", "tcp", "--", "anywhere", "anywhere", "state NEW tcp dpt:ssh"),
    ("ACCEPT", "tcp", "--", "anywhere", "anywhere", "state NEW tcp dpt:http"),
    ("ACCEPT", "tcp", "--", "anywhere", "anywhere", "state NEW tcp dpt:https"),
    ])
def test_iptables_rules(rule):
    ''' Verifies key iptable rules are in place '''
    iptables = common.shell.Run.command('iptables -L')
    assert iptables
    iptables = [re.sub(r"\s\s+", "\t", x) for x in iptables.stdout.strip().split("\n")]
    iptables = [re.sub(r"([^\s]+)\s(--)", "\\1\t\\2", x) for x in iptables]   # for icmp -- (only one space)
    found = False
    for line in iptables:
        line = tuple(x.strip() for x in line.strip().split("\t"))
        if line != rule:
            continue
        else:
            found = True
            break
        

    assert found