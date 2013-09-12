
import os
import sys
import pytest
from ConfigParser import ConfigParser

class YumPlugin(object):
    @classmethod
    def set_yum_variable(cls, key, value):
        """ ???

        """
        if not os.path.isdir('/etc/yum/vars'):
            os.mkdir('/etc/yum/vars')
        fp = open("/etc/yum/vars/%s" % key, "w+")
        fp.write(value)
        fp.close()

    @classmethod
    def get_yum_variable(cls, key):
        """ ???

        """
        # FIXME ... should we also look in /etc/yum/vars/releasever ?

        # Bypass namespace collision on the 'yum' module
        #import yum
        # yb = yum.YumBase()
        yb = __import__('yum').YumBase()

        yb.conf
        return yb.yumvar.get(key)

    @classmethod
    def install(cls, package_name):
        """ Does the 'yum install <package>' command.

        :param package_name: Name of the package to install (eg. katello-all)
        :type package_name: str

        :raises: AssertionError
        """
        # Install it
        result = Test.Run.command("yum -y install %s" % (package_name))
        # Verify it
        assert result, "Installation of package %s failed" % package_name
        Test.RPM.check_for_errors(result.stdout)
        return True

    @classmethod
    def groupinstall(cls, group):
        """ Does the 'yum groupinstall <package>' command.

        :param package_name: Name of the group to install (eg. katello-all)
        :type package_name: str

        :raises: AssertionError
        """
        # Install it
        result = Test.Run.command("yum -y groupinstall %s" % (group))
        assert result, "Installation of group %s failed" % group
        Test.RPM.check_for_errors(result.stdout)
        return True

    @classmethod
    def remove(cls, package_name):
        """ Does the 'yum remove <package>' command.

        :param package_name: Name of the package to be removed (eg. katello-all)
        :type package_name: str

        :raises: AssertionError
        """
        # Remove it
        result = Test.Run.command("yum -y remove %s" % (package_name))
        assert result, "Removal of package %s failed" % package_name
        # Verify it
        try:
            Test.RPM.query(package_name)
            return False
        except AssertionError:
            return True

    @classmethod
    def check_update(cls, package_name):
        """ Using the 'yum check-update <package>' command, determines whether an
        update is available for the provided package.

        :param package_name: Name of the package to be checked for update (eg. katello-all)
        :type package_name: str

        :raises: AssertionError
        """
        # Check for update - error code 100 means an update is available, anything
        # else is considered a failure
        result = Test.Run.command("yum check-update %s" % (package_name))
        if result.rc == 100:
            return True
        else:
            return False

    @classmethod
    def repolist(cls):
        """ Does the 'yum repolist' command.

        :raises: AssertionError
        """
        # Check for update
        result = Test.Run.command("yum repolist")
        assert result
        return result.stdout.strip()

    @classmethod
    def grouplist(cls):
        """ Does the 'yum grouplist' command.

        :raises: AssertionError
        """
        # Check for update
        result = Test.Run.command("yum grouplist")
        assert result
        return result.stdout.strip()

    @classmethod
    def update(cls, package=None):
        """ Does the 'yum update' command.

        :param package: If None, all packages are updated, otherwise selected one will be updated.
        :raises: AssertionError
        """
        # Update
        result = None
        if package is None:
            result = Test.Run.command("yum -y update")
        else:
            result = Test.Run.command("yum -y update %s" % package)
        assert result
        Test.RPM.check_for_errors(result.stdout)
        return result.stdout.strip()

    @classmethod
    def search(cls, package_name):
        """ Does the 'yum search <package>' command.

        :param package_name: Name of the package to install (eg. katello-all)
        :type package_name: str

        :raises: AssertionError
        """
        # Search it
        result = Test.Run.command("yum search %s" % package_name)
        assert result
        return result.stdout.strip()

    @classmethod
    def update_config(cls, repo_file, enabled=True):
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

    @classmethod
    def update_repo(cls, repo_file, enabled=True):
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
        cls.update_config(repo_file, enabled)

    @classmethod
    def update_plugin(cls, plugin_conf, enabled=True):
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
        cls.update_config(plugin_conf, enabled)

export = YumPlugin