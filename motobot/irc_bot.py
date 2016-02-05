from .irc_message import IRCMessage
from .irc_level import IRCLevel
from .database import Database
from socket import create_connection
from importlib import import_module, reload
from pkgutil import iter_modules
from time import sleep
from traceback import print_exc


class IRCBot:

    """ IRCBot class, plug in and go! """

    command_plugin = 1
    match_plugin = 2
    sink_plugin = 3
    hook = 'motobot_hook'
    plugin = 'motobot_plugin'

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

        self.ignore_list = []
        self.userlevels = {}
        self.verified_masters = []

        self.database = Database(self.database_path)
        self.load_plugins('motobot.core_plugins')

    def load_config(self, config):
        self.nick = ''
        self.server = ''
        self.port = 6667
        self.command_prefix = '.'
        self.nickserv_password = None
        self.channels = []
        self.masters = []
        self.database_path = None
        self.default_help = None
        self.error_log = None

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
                except ConnectionResetError:
                    self.connected = False
                    sleep(5)
                except UnicodeEncodeError:
                    pass
                except:
                    self.log_error()

    def load_plugins(self, package):
        """ Add a package to the package list and load the plugins. """
        error = False
        if package not in self.packages:
            self.packages.append(package)
            path = import_module(package).__path__._path
            for _, module_name, _ in iter_modules(path, package + '.'):
                error |= self.__load_module(module_name)
        self.plugins = sorted(self.plugins, reverse=True, key=lambda x: x.priority)
        return error

    def reload_plugins(self):
        """ Reload all plugins from packages. """
        error = False
        self.hooks = {}
        self.plugins = []

        for package in self.packages:
            path = import_module(package).__path__._path
            for _, module_name, _ in iter_modules(path, package + '.'):
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

    def is_master(self, nick, verified=True):
        """ Check if a user is on the master list.

        The verified parameter specifies whether you want to check verified
        masters, or non-verified ones. It's set to verified by default.
        """
        return any(
            x.lower() == nick.lower()
            for x in (self.verified_masters if verified else self.masters)
        )

    def get_userlevel(self, channel, nick):
        """ Return the userlevel of a user in a channel. """
        if self.is_master(nick):
            return IRCLevel.master
        elif channel == self.nick:
            return IRCLevel.owner
        else:
            return max(self.userlevels[(channel, nick)])

    def __connect(self):
        """ Connect the socket. """
        self.socket = create_connection((self.server, self.port))
        self.connected = True
        self.identified = False

    def log_error(self):
        if self.error_log is not None:
            with open(self.error_log, 'a') as log_file:
                print_exc(file=log)
        print_exc()

    def __recv(self):
        """ Receive messages from the socket. """
        self.read_buffer += str(self.socket.recv(512), 'UTF-8', 'ignore')
        msgs = self.read_buffer.split('\r\n')
        self.read_buffer = msgs.pop()
        return msgs

    def send(self, msg):
        """ Send a message to the socket. """
        if msg is not None:
            self.socket.send(bytes(msg + '\r\n', 'UTF-8'))
            print("Sent: {}".format(msg))

    def __handle_message(self, message):
        """ Handle an IRCMessage object with the appropriate handler."""
        print(message)

        try:
            for func in self.hooks.get(message.command, []):
                func(self, message)
        finally:
            self.database.write_database()
