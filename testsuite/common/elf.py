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

import re
import pytest
import common.shell

def is_elf(filename):
    """ Checks whether file is ELF executable

    :param filename: file name to check
    :type filename: ``str``

    :returns: Whether file is ELF executable
    """
    try:
        common.shell.run("readelf -h %s" % filename)
        return True
    except AssertionError:
        return False

def readelf(filename):
    """ Returns content of the ``readelf --all`` call.

    :param filename: File to check
    :type filename: ``str``

    :returns: Content of the ELF analysis
    :rtype: ``str``
    """
    return common.shell.run("readelf --all %s" % filename)

def fortify_find_dangerous(filename):
    """ Finds potentially dangerous func-calls in desired file

    :param filename: File to check
    :type filename: ``str``

    :returns: ``list`` of the potentially dangerous func-calls
    :rtype: ``str``
    """
    dangerous = ['asprintf', 'mbsnrtowcs', 'snprintf', 'vsyslog', 'confstr', 'mbsrtowcs', 'sprintf', 'vwprintf', 'dprintf', 'mbstowcs', 'stpcpy', 'wcpcpy', 'fgets', 'memcpy', 'stpncpy', 'wcpncpy', 'fgets_unlocked', 'memmove', 'strcat', 'wcrtomb', 'fgetws', 'mempcpy', 'strcpy', 'wcscat', 'fgetws_unlocked', 'memset', 'strncat', 'wcscpy', 'fprintf', 'obstack_printf', 'strncpy', 'wcsncat', 'fread', 'obstack_vprintf', 'swprintf', 'wcsncpy', 'fread_unlocked', 'pread', 'syslog', 'wcsnrtombs', 'fwprintf', 'pread64', 'ttyname_r', 'wcsrtombs', 'getcwd', 'printf', 'vasprintf', 'wcstombs', 'getdomainname', 'ptsname_r', 'vdprintf', 'wctomb', 'getgroups', 'read', 'vfprintf', 'wmemcpy', 'gethostname', 'readlink', 'vfwprintf', 'wmemmove', 'getlogin_r', 'readlinkat', 'vprintf', 'wmempcpy', 'gets', 'realpath', 'vsnprintf', 'wmemset', 'getwd', 'recv', 'vsprintf', 'wprintf', 'longjmp', 'recvfrom', 'vswprintf']
    dangerous_calls = re.findall("(?:\\b|__)(?:" + "|".join(dangerous) + ")(?:\\b|_chk|__chk_fail)", readelf(filename))
    return list(set([x.strip().split("@", 1)[0] for x in dangerous_calls]))


