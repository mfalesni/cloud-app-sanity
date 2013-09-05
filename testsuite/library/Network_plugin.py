import re
import pytest
import base64
import common.shell
from urllib2 import urlopen, HTTPError, URLError, Request

class DownloadException(Exception):
    pass

class NetworkPlugin(object):
    @staticmethod
    def service_bound_localhost(service):
        """ This function checks whether certain service is bound only to localhost.

        :param service: Service name
        :type service: ``str``
        :returns: ``True`` when it's bound only to localhost, otherwise ``False``
        :rtype: ``bool``
        """
        netstat = Test.Run.command("netstat -t --listen")
        protocols = ["tcp", "udp"]
        local_addrs = ["127.0.0.1", "::1", "localhost"]
        for line in netstat.stdout.strip().split("\n"):
            fields = re.sub(" +", "\t", line).strip().split("\t")
            if fields[0] in protocols and fields[3].split(":")[-1] == service:
                address = fields[3].split(":")[0]
                if address not in local_addrs:
                    print line
                    pytest.fail(msg="Service '%s' listens to address %s!" % (service, address) )

    @staticmethod
    def download_file(url, target_file_name, bulletproof=False):
        """ Downloads file from desired URL. Can be specified as bulletproof,
            if downloading from Gitweb-site

        :param url: URL where to download from
        :type url: str
        :param target_file_name: Target file name
        :type target_file_name: str
        :param bulletproof: Whether it has to check if it didn't download garbage or not
        :type bulletproof: bool
        """
        trials = 10
        forbidden = "<!DOCTYPE html"
        result = None
        while result == None and trials > 0:
            try:
                handle = urlopen(url)
                content = handle.readlines()
                handle.close()
                if bulletproof:
                    for line in content:
                        if forbidden in line:
                            raise DownloadException("Wrong file format!")
                result = "\n".join(content)
            except (DownloadException, HTTPError, URLError):
                trials -= 1
                if trials == 0:
                    raise
                continue
        try:
            target_file = open(target_file_name, "w")
            target_file.write(result)
            target_file.close()
        except TypeError:
            pytest.fail(msg="Download unsuccessful")

    @staticmethod
    def make_auth_request(url, login, password):
        """ Creates request with basic HTTP authentication

        :param url: URL to use for request
        :type url: str
        :param login: Login name
        :type login: str
        :param password: Login password
        :type password: str
        :return: Basic HTTP authenticated request
        :rtype: urllib2.Request
        """
        request = Request(url)
        request.add_header("Authorization", "Basic %s" % base64.encodestring('%s:%s' % (login, password))[:-1])
        return request

export = NetworkPlugin