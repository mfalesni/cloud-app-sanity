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

import re


def test_memory():
    """
        This test tests whether the box has at least 6G of memory

    :raises: ``AssertionError``
    """
    mem = Test.Run.bash("free -g | grep Mem:")
    assert mem
    mem = re.sub(r"\s+", "\t", mem.stdout.strip()).split("\t")  # ['Mem:', '1', '1', ...]
    mem = int(mem[1]) # second column
    assert mem >= 6, "Machine must have at least 6G of mem."

def test_cpu():
    """
        This test verifies that the machine has at least 4 cpus

    :raises: ``AssertionError``
    """
    cpus = Test.Run.bash("lscpu | grep ^CPU\(s\):")
    assert cpus
    cpus = re.sub(r"\s+", "\t", cpus.stdout.strip())
    cpus = int(cpus.split("\t", 1)[-1]) # Second column
    assert cpus >= 4, "Machine must have at least 4 CPUs"