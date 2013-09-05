import __builtin__
import sys

folder_name = "plugins"

class PluginNotFound(Exception):
    pass

class ClassProperty (property):
    """Subclass property to make classmethod properties possible"""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class PluginProxy(object):
    def __init__(self):
        self.plugins = dict()

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