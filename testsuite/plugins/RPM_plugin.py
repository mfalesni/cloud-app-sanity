import re

class RPMPackageFailure(Exception):
    pass

class RPMScriptletFailure(Exception):
    pass

RPM_PROBLEMS_MESSAGES = {   "S": "size",
                            "M": "mode",
                            "5": "MD5 checksum",
                            "D": "major and minor numbers",
                            "L": "symbolic link contents",
                            "U": "owner",
                            "G": "group",
                            "T": "modification time"}
""" Contains messages reported by RPM tests for each problem """

class RPMPlugin(object):
    @classmethod
    def query(cls, package=None, format=None):
        """
            rpm -q command

        :param package: Which package to query. If None, the all packages are queried
        :param format: --qf formatting string. If None, no specific format
        """
        command = "rpm"
        if package is not None:
            command += " -q %s" % package
        else:
            command += " -qa"
        if format is not None:
            command += " --qf '%s\\n'" % format
        rpm = Test.Run.command(command)
        assert rpm, "'%s' failed, does the package exist?" % command
        return rpm.stdout.strip().split("\n")

    @classmethod
    def verify(cls, package):
        """
            Does rpm -Vvv command, returns the output.

        """
        rpm = Test.Run.command("rpm -Vvv %s" % package)
        assert rpm, "'rpm -Vvv %s' failed, does the package exist?" % package
        return rpm

    @classmethod
    def who_owns(cls, file):
        """
            rpm -qf file
        """
        rpm = Test.Run.command("rpm -qf %s" % file)
        if rpm.rc != 0:
            return None
        else:
            return rpm.stdout.strip()

    @classmethod
    def list_files(cls, package):
        """
            List all files owned by a specified package.
        """
        rpm = Test.Run.command("rpm -ql %s" % package)
        assert rpm, "'rpm -ql %s' failed, does the package exist?" % package
        return rpm.stdout.strip().split("\n")

    @classmethod
    def signature_lines(cls, package_lines):
        """ Returns lines with signature informations of package

        :param package_lines: rpm --verify output for the package
        :type package_lines: ``list[str]``

        :returns: List of lines speaking about signatures
        :rtype: ``list(str)``
        """
        sig = re.compile("[Ss]ignature")
        for line in package_lines:
            if sig.search(line):
                yield line.split("#", 1)[-1].lstrip()

    @classmethod
    def package_signed(cls, package):
        """ Verifies package in RPM database.

            Checks for signature.

        :param package: Package to check
        :type package: ``str``
        :returns: Bool whether verification of signature succeeded
        :rtype: ``bool``
        """
        rpm = Test.Run.command("rpm -qvv %s" % package)
        assert rpm, "'rpm -qvv %s' failed, does the package exist?" % package
        stderr = rpm.stderr.strip().split("\n")
        for line in cls.signature_lines(stderr):
            fields = [x.strip() for x in line.rsplit(", key ID", 1)]
            key_status = None
            if re.match("^[0-9a-z]+$", fields[1]):
                # RHEL 5
                key_status = fields[0]
            else:
                # RHEL 6
                key_status = fields[1]
            key_status = key_status.rsplit(":", 1)[1].strip()   # The key info is on the right side of the colon
            if not key_status.upper() == "OK":
                return False
        return True

    @classmethod
    def check_for_errors(cls, text):
        """ This function checks for errors in text and returns text unchanged

        :param text: text to be checked
        :type text: ``str``

        :returns: text
        :rtype: ``str``
        """
        errors = {'failure in rpm package': RPMPackageFailure, 'scriptlet failed, exit status 1': RPMScriptletFailure}
        for error in errors.keys():
            if error in text:
                raise errors.keys()[error](text)
        return text




export = RPMPlugin