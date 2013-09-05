
import os
import pytest
import shutil

class ShellPlugin(object):
    @staticmethod
    def copy(source, destination):
        if not os.path.isfile(source):
            pytest.fail(msg="Couldn't find file '%s'" % source)
        shutil.copy(source, destination)

    @staticmethod
    def mkdir(directory):
        os.mkdir(directory)

    @staticmethod
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

    @staticmethod
    def append_file(target, fromf, strip_sep=False):
        """ This function appends one file to another.
            It's possible to strip the content from blank characters at beginning and end + separate the contents by \n

        :param target: Target file
        :type target: str
        :param target: Source file
        :type target: str
        :param strip_sep: Whether to strip the contents and separate new file by \n
        :type strip_sep: ``bool``

        :returns: None
        :rtype: None
        """    
        destination = open(target, "a")
        source = open(fromf, "r")
        data = source.read()
        if strip_sep:
            data = "%s\n" % data.strip()
        destination.write(data)
        source.close()
        destination.close()

export = ShellPlugin