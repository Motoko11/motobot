from .irc_message import IRCMessage
from .irc_level import IRCLevel
from .priority import Priority
from .database import Database
from socket import create_connection
from importlib import import_module, reload
from pkgutil import iter_modules
from time import sleep
import re
import traceback


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

        self.database = Database()
        self.load_plugins('motobot.core_plugins')

    def load_config(self, config):
        self.nick = ''
        self.server = ''
        self.port = 6667
        self.command_prefix = '.'
        self.nickserv_password = None
        self.channels = []
        self.masters = []

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
                except:
                    traceback.print_exc()

    def load_plugins(self, package):
        """ Add a package to the package list and load the plugins. """
        if package not in self.packages:
            self.packages.append(package)
            path = import_module(package).__path__._path
            for _, module_name, _ in iter_modules(path, package + '.'):
                self.__load_module(module_name)
        self.plugins = sorted(self.plugins, reverse=True, key=lambda x: x[2])

    def reload_plugins(self):
        """ Reload all plugins from packages. """
        self.hooks = {}
        self.plugins = []

        for package in self.packages:
            path = import_module(package).__path__._path
            for _, module_name, _ in iter_modules(path, package + '.'):
                self.__load_module(module_name)
        self.plugins = sorted(self.plugins, reverse=True, key=lambda x: x[2])

    def __load_module(self, module_name):
        """ Load or reload a module. """
        if module_name in self.modules:
            reload(self.modules[module_name])
            print("Module: {} reloaded".format(module_name))
        else:
            self.modules[module_name] = import_module(module_name)
            print("Module: {} loaded".format(module_name))

        module = self.modules[module_name]
        for func in [getattr(module, attrib) for attrib in dir(module)]:
            self.__add_hook(func)
            self.__add_plugin(func)

    def __add_hook(self, func):
        """ Add a hook to the bot. """
        for hook in getattr(func, IRCBot.hook, []):
            funcs = self.hooks.get(hook, [])
            funcs.append(func)
            self.hooks[hook] = funcs

    def __add_plugin(self, func):
        """ Add a plugin to the bot. """
        for plugin_data in getattr(func, IRCBot.plugin, []):
            self.plugins.append((func,) + plugin_data)

    def load_database(self, path):
        self.database = Database(path)

    def ignore(self, hostmask):
        """ Ignore a user with the given hostmask. """
        pattern = re.compile(hostmask.replace('*', '.*'), re.IGNORECASE)
        self.ignore_list.append(pattern)

    def unignore(self, host):
        """ Unignore all masks which match given nick. """
        removed = False
        for pattern in self.ignore_list:
            if pattern.match(host):
                self.ignore_list.remove(pattern)
                removed = True
        return removed

    def __ignored(self, host):
        """ Test if a given user is ignored or not. """
        if host is None:
            return False

        for pattern in self.ignore_list:
            if pattern.match(host):
                return True
        else:
            return False

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

    def disconnect(self):
        """ Disconnect the bot. """
        self.send('QUIT :BAI!')
        self.running = self.connected = self.identified = False

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
        """ Handle an IRCMessage object with the appropriate handler.

        Will ignore a user if their mask is on the ignore list.

        """
        print(message)

        if not self.__ignored(message.sender):
            if message.command in self.hooks:
                for func in self.hooks[message.command]:
                    func(self, message)
            else:
                print("Unknown command: {}".format(message.command))


def hook(command):
    """ Decorator to add a hook to the bot. """
    def register_hook(func):
        attr = getattr(func, IRCBot.hook, [])
        attr.append(command)
        setattr(func, IRCBot.hook, attr)
        return func
    return register_hook


def command(name, level=IRCLevel.user, priority=Priority.medium):
    """ Decorator to add a command to the bot. """
    def register_command(func):
        attr = getattr(func, IRCBot.plugin, [])
        attr.append((IRCBot.command_plugin, priority, level, name))
        setattr(func, IRCBot.plugin, attr)
        return func
    return register_command


def match(pattern, level=IRCLevel.user, priority=Priority.medium):
    """ Decorator to add a regex pattern to the bot. """
    def register_pattern(func):
        attr = getattr(func, IRCBot.plugin, [])
        compiled = re.compile(pattern, re.IGNORECASE)
        attr.append((IRCBot.match_plugin, priority, level, compiled))
        setattr(func, IRCBot.plugin, attr)
        return func
    return register_pattern


def sink(level=IRCLevel.user, priority=Priority.medium):
    """ Decorator to add sink to the bot. """
    def register_sink(func):
        attr = getattr(func, IRCBot.plugin, [])
        attr.append((IRCBot.sink_plugin, priority, level))
        setattr(func, IRCBot.plugin, attr)
        return func
    return register_sink
