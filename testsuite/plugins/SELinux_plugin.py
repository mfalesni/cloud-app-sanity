
class SELinuxPlugin(object):
    @staticmethod
    def setenforce(mode):
        """ Sets enforcing mode of SElinux

        :param mode: Enforcing mode from [Permissive, Enforcing]
        :param type: ``str``
        :raises: AssertionError
        """
        mode = mode.strip().title()
        assert mode in ["Permissive", "Enforcing"]
        assert Test.Run.command("/usr/sbin/setenforce %s" % mode)

    @ClassProperty
    @classmethod
    def getenforce(cls):
        """ Returns enforcing mode of SElinux

        :returns: Enforcing mode of SELinux
        :rtype: ``str``
        """
        getenforce = Test.Run.command("/usr/sbin/getenforce")
        assert getenforce
        return getenforce.stdout.strip()

    @ClassProperty
    @classmethod
    def enabled(cls):
        try:
            assert Test.Run.command("selinuxenabled")
        except AssertionError:
            return False
        return True

export = SELinuxPlugin