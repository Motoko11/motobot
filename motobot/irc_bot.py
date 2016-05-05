from .irc_message import IRCMessage
from .database import Database
from .utilities import Context
from socket import create_connection, timeout
from ssl import wrap_socket
from importlib import import_module, reload
from pkgutil import walk_packages
from time import sleep
from traceback import print_exc


class IRCBot:

    """ IRCBot class, plug in and go! """

    command_plugin = 1
    match_plugin = 2
    sink_plugin = 3
    hook = 'motobot_hook'
    plugin = 'motobot_plugin'
    req = 'motobot_request'

    def __init__(self, config):
        """ Create a new instance of IRCBot. """
        self.load_config(config)

        self.socket = None
        self.running = self.connected = self.identified = False
        self.read_buffer = ''

        self.packages = []
        self.modules = {}
        self.hooks = {}
        self.plugins = []
        self.requests = {}

        self.database = Database(self.database_path, self.backup_folder)
        self.sessions = Database()
        self.load_plugins('motobot.core_plugins')

    def load_config(self, config):
        self.nick = ''
        self.server = ''
        self.port = 6667
        self.ssl = False
        self.command_prefix = '.'
        self.nickserv_password = None
        self.channels = []
        self.masters = []
        self.database_path = None
        self.error_log = None
        self.backup_folder = None

        for key, val in config.items():
            setattr(self, key, val)

    def run(self):
        """ Run the bot.

        If an exception is raised during message handing
        or recv, it is eaten, and the traceback is printed.

        """
        self.running = True
        while self.running:
            self.__connect()
            while self.connected:
                try:
                    for msg in self.__recv():
                        message = IRCMessage(msg)
                        self.__handle_message(message)
                except (ConnectionResetError, ConnectionAbortedError, timeout):
                    self.connected = False
                    sleep(5)
                except:
                    self.log_error()

    def load_plugins(self, package):
        """ Add a package to the package list and load the plugins. """
        error = False
        if package not in self.packages:
            self.packages.append(package)
            module = import_module(package)
            paths = module.__path__
            for _, module_name, is_package in walk_packages(paths, package + '.'):
                if not is_package:
                    error |= self.__load_module(module_name)
        self.plugins = sorted(self.plugins, reverse=True, key=lambda x: x.priority)
        return error

    def reload_plugins(self):
        """ Reload all plugins from packages. """
        error = False
        self.hooks = {}
        self.plugins = []

        for package in self.packages:
            module = import_module(package)
            paths = module.__path__
            for _, module_name, is_package in walk_packages(paths, package + '.'):
                if not is_package:
                    error |= self.__load_module(module_name)
        self.plugins = sorted(self.plugins, reverse=True, key=lambda x: x.priority)
        return error

    def __load_module(self, module_name):
        """ Load or reload a module. """
        error = False
        if module_name in self.modules:
            try:
                reload(self.modules[module_name])
                print("Module: {} reloaded".format(module_name))
            except:
                error = True
                self.log_error()
                print("Error: while trying to reload module: {}".format(module_name))
        else:
            try:
                self.modules[module_name] = import_module(module_name)
                print("Module: {} loaded".format(module_name))
            except:
                error = True
                self.log_error()
                print("Error: while trying to load module: {}".format(module_name))

        if not error:
            module = self.modules[module_name]
            for func in [getattr(module, attrib) for attrib in dir(module)]:
                self.__add_hook(func)
                self.__add_plugin(func)
                self.__add_request(func)
        return error

    def __add_hook(self, func):
        """ Add a hook to the bot. """
        for hook in getattr(func, IRCBot.hook, []):
            funcs = self.hooks.get(hook, [])
            funcs.append(func)
            self.hooks[hook] = funcs

    def __add_plugin(self, func):
        """ Add a plugin to the bot. """
        for plugin in getattr(func, IRCBot.plugin, []):
            self.plugins.append(plugin)

    def __add_request(self, func):
        """ Add a request to the bot. """
        for request in getattr(func, IRCBot.req, []):
            self.requests[request] = func

    def request(self, name, *args, **kwargs):
        """ Request something from the bot's request plugins. """
        func = self.requests.get(name, lambda *x, **xs: None)
        module = func.__module__
        context = Context(None, None, None, self.database.get_entry(module),
                          self.sessions.get_entry(module))
        return func(self, context, *args, **kwargs)

    def __connect(self):
        """ Connect the socket. """
        while True:
            try:
                self.socket = create_connection((self.server, self.port))
                if self.ssl:
                    self.socket = wrap_socket(self.socket)
                self.socket.settimeout(5 * 60)
                self.connected = True
                self.identified = False
                break
            except:
                sleep(5)

    def log_error(self):
        if self.error_log is not None:
            with open(self.error_log, 'a') as log_file:
                print_exc(file=log_file)
        print_exc()

    def __recv(self):
        """ Receive messages from the socket. """
        self.read_buffer += str(self.socket.recv(512), 'UTF-8', 'ignore')
        msgs = self.read_buffer.split('\r\n')
        self.read_buffer = msgs.pop()
        return msgs

    def send(self, msg):
        """ Send a message to the socket. """
        max_len = 510
        byte_string = bytes(msg, 'UTF-8')
        message = byte_string.replace(b'\r', b'').replace(b'\n', b'')[:max_len] + b'\r\n'
        self.socket.send(message)
        try:
            print("Sent: {}".format(msg))
        except UnicodeEncodeError:
            pass

    def __handle_message(self, message):
        """ Handle an IRCMessage object with the appropriate handler."""
        try:
            print(message)
        except UnicodeEncodeError:
            pass

        try:
            for func in self.hooks.get(message.command, []):
                module = func.__module__
                context = Context(None, None, None, self.database.get_entry(module),
                                  self.sessions.get_entry(module))
                func(self, context, message)
        finally:
            self.database.write_database()
