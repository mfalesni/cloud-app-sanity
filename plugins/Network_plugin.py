import re
import pytest
import base64
import socket
import common.shell
from urllib2 import urlopen, HTTPError, URLError, Request

class DownloadException(Exception):
    pass

class NetworkPlugin(object):

    default_wait_port = 35579

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

    @classmethod
    def wait_for_request(cls, request_path="/continue", port=None):
        host = '0.0.0.0'
        if not port:
            port = cls.default_wait_port
        backlog = 5
        size = 1024
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host,port))
        s.listen(backlog)
        result = None
        try:
            while True:
                client, address = s.accept()
                data = client.recv(size)
                if not data:
                    client.close()
                    continue
                data = data.strip().split("\n", 1)[0].strip()
                if not data.startswith("GET"):
                    client.send("HTTP/1.1 405 Method Not Allowed\nContent-type: text/plain\n\n405 %s\n" % request_path)
                else:
                    method, rest = data.split(" ", 1)
                    path, protocol = rest.rsplit(" ", 1)
                    if path.strip().startswith(request_path):
                        client.send("HTTP/1.1 200 OK\nContent-type: text/plain\n\n200 %s\n" % request_path)
                        result = path.strip()[len(request_path):]
                        result = re.sub(r"^/", "", result)
                        break
                    else:
                        client.send("HTTP/1.1 404 Not Found\nContent-type: text/plain\n\n404 %s\n" % request_path)
                client.close()
        finally:
            s.close()
        return result

    @classmethod
    def domain_ip(cls, domain):
        result = Test.Run.command("host -t a %s" % domain)
        assert result
        assert "has address" in result.stdout
        ip_addr = result.stdout.strip().rsplit("has address", 1)[-1].strip()
        return ip_addr

export = NetworkPlugin