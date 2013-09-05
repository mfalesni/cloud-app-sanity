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
    def is_package_installed(cls, package):
        """
            rpm -q without assertion, instead returns bool
        """
        try:
            cls.query(package)
            return True
        except AssertionError:
            return False

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

    @classmethod
    def wrong_files_lines(cls, package_lines):
        """ Returns lines with problem files

        :param package_lines: rpm --verify output for the package
        :type package_lines: ``list[str]``

        :returns: List of lines speaking about wrong something about files
        :rtype: ``list(str)``
        """
        release = Test.Fixtures.rhel_release()
        for line in package_lines:
            line = line.strip()
            if len(line) > 0:
                # RHEL5 has 8 dots
                # RHEL6 has 9 dots
                if (not line.startswith(".........") and release.major == 6) or (not line.startswith("........") and release.major == 5):
                    yield line

    @classmethod
    def verify_package_files(cls, package):
        """ Verifies package in RPM database.

            Checks output of the rpm -Vvv and looks for files, which have some problems (see http://www.rpm.org/max-rpm/s1-rpm-verify-output.html)
            When using RHEL5, $? is ignored.

        :param package: Package to check
        :type package: ``str``
        :returns: Bool whether verification succeeded
        :rtype: ``bool``
        """
        problems = []
        vrf = cls.verify(package)
        source = vrf.stdout.strip().split("\n")
        if int(vrf.rc) != 0 and Test.Fixtures.rhel_release().major != 5: # RHEL5 will ignore returncode
            problems.append("RPM $?=%d" % int(vrf.rc))
        for line in cls.wrong_files_lines(source):
            status_type, filename = line.split("/", 1)
            filename = "/" + filename
            status_type = re.sub(r"\s+", " ", status_type).strip().split()
            status = status_type[0]
            file_type = ""
            if len(status_type) > 1:
                file_type = status_type[1].strip()
            # if file_type == "c":
            #     continue
            status_problems = []
            for key in RPM_PROBLEMS_MESSAGES:
                if key in status:
                    status_problems.append(RPM_PROBLEMS_MESSAGES[key])
            if len(status_problems) == 0:
                status_problems.append(status)
                #TODO config?

            problems.append("file %s has problems with %s" % (filename, ", ".join(status_problems) ) )
        return problems




export = RPMPlugin