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

import shlex
import subprocess
import shutil
import os

def run(cmd, errorcode=0):
    """This function runs desired command and checks whether it has failed or not

    :param cmd: Command to be run
    :type cmd: str or list (``shlex``-splitted)
    :param errorcode: Desired error code of the program. Defaults to 0 (all ok). If set to ``None``, error code won't be checked. If it is list, then it checks whether program ended with errorcode specified in list and returns the error code
    :type errorcode: int, list, None
    
    :returns: ``STDOUT`` of called process
    :rtype: ``str``, ``int``
    :raises: AssertionError
    """
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    collate_original = None
    try:
        collate_original = os.environ['LC_ALL']
    except KeyError:
        pass
    os.environ['LC_ALL'] = "C" # Because of my czech locale
    try:
        p_open = subprocess.Popen(cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
        (stdout, stderr) = p_open.communicate()
        if errorcode is not None:
            # Force errorcode to be a list
            if not isinstance(errorcode, list):
                errorcode = [errorcode]
            assert p_open.returncode in errorcode, \
                    "Command '%s' failed with unexpected error code: %d != %s\n%s" % \
                    (cmd, p_open.returncode, errorcode, stdout)
    finally:
        if collate_original:
            os.environ['LC_ALL'] = collate_original
        else:
            del os.environ['LC_ALL']
    return stdout

def command(command):
    """ Function used for calling shell commands rather than invoking programs.

    :param command: Command to be launched
    :type command: ``str``

    :returns: ``tuple`` of ``STDOUT`` and RC of the command
    :raises: AssertionError
    """
    collate_original = None
    try:
        collate_original = os.environ['LC_ALL']
    except KeyError:
        pass
    os.environ['LC_ALL'] = "C" # Because of my czech locale
    try:
        process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdout, stderr) = process.communicate()
    finally:
        if collate_original:
            os.environ['LC_ALL'] = collate_original
        else:
            del os.environ['LC_ALL']
    return (stdout, process.returncode)

def command_stderr(command):
    """ Function used for calling shell commands rather than invoking programs.
        It also returns stderr output, so it's basically the same as the preceeding function, just return tuple extended

    :param command: Command to be launched
    :type command: ``str``

    :returns: ``tuple`` of ``STDOUT`` and RC of the command
    :raises: AssertionError
    """
    collate_original = None
    try:
        collate_original = os.environ['LC_ALL']
    except KeyError:
        pass
    os.environ['LC_ALL'] = "C" # Because of my czech locale
    try:
        process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdout, stderr) = process.communicate()
    finally:
        if collate_original:
            os.environ['LC_ALL'] = collate_original
        else:
            del os.environ['LC_ALL']
    return (stdout, stderr, process.returncode)
    
def copy(source, destination):
    if not os.path.isfile(source):
        pytest.fail(msg="Couldn't find file '%s'" % source)
    shutil.copy(source, destination)

def mkdir(directory):
    os.mkdir(directory)

def exists_in_path(file, actual_directory):
    """ This function looks whether a file exists in system PATH or actual directory.

    :param file: File to look for
    :type file: ``str``
    :param actual_directory: Actual directory we are in
    :type actual_directory: ``str``
    :returns: File existence ``True`` or ``False``
    :rtype: ``bool``
    """
    extensions = os.environ.get("PATHEXT", "").split(os.pathsep)
    pathdirs = os.environ.get("PATH", "").split(os.pathsep)
    pathdirs.append(actual_directory)
    for directory in pathdirs:
        base = os.path.join(directory, file)
        options = [base] + [(base + ext) for ext in extensions]
        for filename in options:
            if os.path.exists(filename):
                return True
    return False

class Run(object):
    """
        New class for running shell commands.
        To run a command, use the Run.command(...) class method.
        Result contains stdout, stderr, rc and run command:
        self.stdout, self.stderr, self.rc, self.command.
        Result is usable in if, if the $?=0, if evaluates as True.

        Run.bash() runs bash script provides as a parameter.
    """
    def __init__(self, stdout, stderr, rc, command, shell=False):
        self.stdout = stdout
        self.stderr = stderr
        self.rc = rc
        self.command = command
        self.shell = shell

    def __repr__(self):
        return "<Run->%d stdout='%s...' stderr='%s...'>" % (self.rc, self.stdout[:16], self.stderr[:16])

    def __nonzero__(self):
        return self.rc == 0

    @classmethod
    def command(cls, command, stdin=None, shell=False):
        if not shell and isinstance(command, str):
            command = shlex.split(command)
        collate_original = None
        try:
            collate_original = os.environ['LC_ALL']
        except KeyError:
            pass
        os.environ['LC_ALL'] = "C" # Because of my czech locale
        try:
            process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=shell)
            (stdout, stderr) = process.communicate(stdin)
        finally:
            if collate_original:
                os.environ['LC_ALL'] = collate_original
            else:
                del os.environ['LC_ALL']
        return Run(stdout, stderr, process.returncode, command)

    @classmethod
    def bash(cls, script_body):
        return Run.command(["bash", "-c", script_body])