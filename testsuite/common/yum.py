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

import os
import sys
import pytest
import common.shell
import common.rpm
from ConfigParser import ConfigParser

def set_yum_variable(key, value):
    if not os.path.isdir('/etc/yum/vars'):
        os.mkdir('/etc/yum/vars')
    fp = open("/etc/yum/vars/%s" % key, "w+")
    fp.write(value)
    fp.close()

def get_yum_variable(key):
    # FIXME ... should we also look in /etc/yum/vars/releasever ?

    # Bypass namespace collision on the 'yum' module
    #import yum
    # yb = yum.YumBase()
    yb = __import__('yum').YumBase()

    yb.conf
    return yb.yumvar.get(key)

def install(package_name):
    """ Does the 'yum install <package>' command.

    :param package_name: Name of the package to install (eg. katello-all)
    :type package_name: str

    :raises: AssertionError
    """
    # Install it
    text = common.shell.run("yum -y install %s" % (package_name))
    # Verify it
    common.shell.run("rpm -q %s" % (package_name))
    return common.rpm.check_for_errors(text)

def groupinstall(group):
    """ Does the 'yum groupinstall <package>' command.

    :param package_name: Name of the group to install (eg. katello-all)
    :type package_name: str

    :raises: AssertionError
    """
    # Install it
    text = common.shell.run("yum -y groupinstall %s" % (group))
    return common.rpm.check_for_errors(text)

def remove(package_name):
    """ Does the 'yum remove <package>' command.

    :param package_name: Name of the package to be removed (eg. katello-all)
    :type package_name: str

    :raises: AssertionError
    """
    # Remove it
    text = common.shell.run("yum -y remove %s" % (package_name))
    # Verify it
    common.shell.run("rpm -q %s" % (package_name), errorcode=1)

    return text

def check_update(package_name):
    """ Does the 'yum check-update <package>' command.

    :param package_name: Name of the package to be checked for update (eg. katello-all)
    :type package_name: str

    :raises: AssertionError
    """
    # Check for update
    result_good = [0, 100]
    result_map = {0: False, 100: True}
    result = common.shell.run("yum check-update %s" % (package_name), result_good)
    return result_map[result]

def repolist():
    """ Does the 'yum repolist' command.

    :raises: AssertionError
    """
    # Check for update
    return common.shell.run("yum repolist")

def grouplist():
    """ Does the 'yum grouplist' command.

    :raises: AssertionError
    """
    # Check for update
    return common.shell.run("yum grouplist")

def update():
    """ Does the 'yum update' command.

    :raises: AssertionError
    """
    # Update
    return common.rpm.check_for_errors(shell.run("yum -y update"))

def search(package_name):
    """ Does the 'yum search <package>' command.

    :param package_name: Name of the package to install (eg. katello-all)
    :type package_name: str

    :raises: AssertionError
    """
    # Install it
    return common.shell.run("yum search %s" % (package_name))

def update_config(repo_file, enabled=True):
    """Enables or disables all sections in Yum config files

    :param repo_file: Config file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool

    """
    if os.path.isfile(repo_file):
        cfg = ConfigParser()
        cfg.read([repo_file])
        save_changes = False
        for section in cfg.sections():
            if cfg.has_option(section, 'enabled'):
                save_changes = True
                if enabled:
                    cfg.set(section, 'enabled', 1)
                else:
                    cfg.set(section, 'enabled', 0)
        if save_changes:
            fd = open(repo_file, 'rwa+')
            cfg.write(fd)
            fd.close()
    else:
        pytest.fail(msg="%s was not found!" % repo_file)

def update_repo(repo_file, enabled=True):
    """Enables or disables all sections in Yum repository files

    :param repo_file: Repo file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool
    """
    if not repo_file.startswith('/'):
        repo_file = '/etc/yum.repos.d/%s' % repo_file
    if not repo_file.endswith('.repo'):
        repo_file = '%s.repo' % repo_file
    update_config(repo_file, enabled)

def update_plugin(plugin_conf, enabled=True):
    """Enables or disables all sections in Yum plugin config files

    :param repo_file: Config file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool
    """
    if not plugin_conf.startswith('/'):
        plugin_conf = '/etc/yum/pluginconf.d/%s' % plugin_conf
    if not plugin_conf.endswith('.conf'):
        plugin_conf = '%s.conf' % plugin_conf
    update_config(plugin_conf, enabled)
