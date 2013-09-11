import __builtin__
import sys

folder_name = __name__

class PluginNotFound(Exception):
    pass

class ClassProperty (property):
    """Subclass property to make classmethod properties possible"""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class PluginProxy(object):
    """
        Lazy plugin loader. Let's say you have:

        ``Plugin = PluginProxy()``

        Then if you write ``Plugin.Foo`` it looks up
        in internal plugin table for Foo and when it
        does not find it, it tries to load a module
        named ``folder_name.Foo_plugin``. If everything
        succeeds, it looks for variable ``export`` inside
        the module, which specifies the class to be assigned
        as the module itself.
    """
    def __init__(self):
        self.plugins = dict()
        self.Fixtures = __import__("conftest")  # Provide fixtures from conftest.py without imports
        pytest = __import__("pytest")
        self.Mark = pytest.mark
        self.Fail = pytest.fail
        self.Skip = pytest.skip
        self.Fixture = pytest.fixture
        unittestzero = __import__("unittestzero")
        self.Assert = unittestzero.Assert

    def __getattribute__(self, attribute):
        try:
            return object.__getattribute__(self, attribute)
        except AttributeError:
            pass
        if attribute not in self.plugins:
            try:
                plugin_name = "%s.%s_plugin" % (folder_name,attribute)
                __import__(plugin_name)
                plugin = sys.modules[plugin_name]
                plugin = plugin.export
            except (ImportError, KeyError, AttributeError):
                if plugin_name in sys.modules:
                    del sys.modules[plugin_name]
                raise PluginNotFound("Plugin %s not found!" % attribute)
            self.plugins[attribute] = plugin
        return self.plugins[attribute]

# Guido will kill me
__builtin__.Test = PluginProxy()
__builtin__.ClassProperty = ClassProperty

# Python 2.4 compatibility
try:
    __builtin__.any
except AttributeError:
    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False
    __builtin__.any = any