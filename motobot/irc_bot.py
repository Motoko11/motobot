from .irc_message import IRCMessage
from .irc_level import IRCLevel
from .database import Database
from socket import create_connection
from importlib import import_module, reload
from pkgutil import iter_modules
from time import sleep
import re
import traceback


class IRCBot:

    """ IRCBot class, plug in and go! """

    def __init__(self, nick, server, port=6667, command_prefix='.', nickserv_password=None):
        """ Create a new instance of IRCBot. """
        self.nick = nick
        self.server = server
        self.port = port
        self.command_prefix = command_prefix
        self.nickserv_password = nickserv_password

        self.socket = None
        self.running = self.connected = self.identified = False
        self.read_buffer = ''

        self.packages = []
        self.plugins = {}
        self.hooks = {}
        self.commands = {}
        self.patterns = []
        self.sinks = []

        self.channels = []
        self.ignore_list = []
        self.userlevels = {}

        self.database = Database()
        self.load_plugins('motobot.hooks')

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

    def reload_plugins(self):
        """ Reload all plugins from packages. """
        self.hooks = {}
        self.commands = {}
        self.patterns = []
        self.sinks = []

        for package in self.packages:
            path = import_module(package).__path__._path
            for _, module_name, _ in iter_modules(path, package + '.'):
                self.__load_module(module_name)

    def __load_module(self, module_name):
        """ Load or reload a module. """
        if module_name in self.plugins:
            reload(self.plugins[module_name])
            print("Module: {} reloaded".format(module_name))
        else:
            self.plugins[module_name] = import_module(module_name)
            print("Module: {} loaded".format(module_name))

        module = self.plugins[module_name]
        for func in [getattr(module, attrib) for attrib in dir(module)]:
            self.__add_hook(func)
            self.__add_command(func)
            self.__add_pattern(func)
            self.__add_sink(func)

    def __add_hook(self, func):
        if hasattr(func, 'motobot_hook'):
            for hook in func.motobot_hook:
                self.hooks[hook] = func

    def __add_command(self, func):
        if hasattr(func, 'motobot_command'):
            for command, level in func.motobot_command:
                self.commands[command] = userlevel_wrapper(func, level)

    def __add_pattern(self, func):
        if hasattr(func, 'motobot_pattern'):
            for pattern, level in func.motobot_pattern:
                regex = re.compile(pattern, re.IGNORECASE)
                self.patterns.append((regex, userlevel_wrapper(func, level)))

    def __add_sink(self, func):
        if hasattr(func, 'motobot_sink'):
            self.sinks.append(func)

    def load_database(self, path):
        self.database = Database(path)

    def join(self, channel):
        """ Join a channel. """
        if self.connected:
            self.send('JOIN ' + channel)
        self.channels.append(channel)

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
        self.read_buffer += str(self.socket.recv(512), 'ASCII', 'ignore')
        self.read_buffer = strip_control_codes(self.read_buffer)
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
                self.send(self.hooks[message.command](self, message))
            else:
                print("Unknown command: {}".format(message.command))


def userlevel_wrapper(func, level):
    """ Modify a plugin to only take users above a certain userlevel. """
    def wrapped(bot, message, *args, **kwargs):
        if max(bot.userlevels.get((message.nick, message.channel), [IRCLevel.user])) >= level:
            return func(bot, message, *args, **kwargs)
    return wrapped


def hook(command):
    """ Decorator to add a hook to the bot. """
    def register_hook(func):
        if not hasattr(func, 'motobot_hook'):
            func.motobot_hook = []
        func.motobot_hook.append(command)
        return func
    return register_hook


def command(name, level=IRCLevel.user):
    """ Decorator to add a command to the bot. """
    def register_command(func):
        if not hasattr(func, 'motobot_command'):
            func.motobot_command = []
        func.motobot_command.append((name, level))
        return func
    return register_command


def match(pattern, level=IRCLevel.user):
    """ Decorator to add a regex pattern to the bot. """
    def register_pattern(func):
        if not hasattr(func, 'motobot_pattern'):
            func.motobot_pattern = []
        func.motobot_pattern.append((pattern, level))
        return func
    return register_pattern


def sink(func):
    """ Decorator to add sink to the bot. """
    func.motobot_sink = True
    return func


def strip_control_codes(input):
    """ Strip the control codes from the input. """
    pattern = re.compile(r'\x03[0-9]{0,2},?[0-9]{0,2}|\x02|\x1D|\x1F|\x16|\x0F')
    output = pattern.sub('', input)
    return output
