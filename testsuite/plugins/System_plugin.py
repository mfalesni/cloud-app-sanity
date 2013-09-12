import re

class SystemPlugin(object):
    @classmethod
    def chkconfig_list(cls):
        """ Returns list of all services with enablement in each runlevel

        :returns: All services.
        :rtype: ``dict``
        """
        result = {}
        services = Test.Run.command("chkconfig --list")
        for line in services.stdout.strip().split("\n"):
            line = re.sub("[[:blank:]]+", "\t", line)
            fields = line.split("\t")
            servicename = fields[0].strip()
            fields = fields[1:]
            result[servicename] = {}
            for field in fields:
                (runlevel, status) = field.split(":")
                runlevel = int(runlevel)
                if status.lower() == "on":
                    status = True
                elif status.lower() == "off":
                    status = False
                else:
                    Test.Fail(msg="Bad parsing of chkconfig --list")
                result[servicename][runlevel] = status
        return result

    @classmethod
    def service_active_in_runlevel(cls, service, runlevel, active=True):
        """ Does the check of service presence in desired runlevels

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
        chkconfig_list = cls.chkconfig_list()
        try:
            if chkconfig_list[service][runlevel] != active:
                return False
        except KeyError:
            Test.Fail("Service %s probably even does not exist in the system!" % service)

        return True

export = SystemPlugin