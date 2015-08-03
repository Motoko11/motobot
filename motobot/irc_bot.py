from .irc_message import IRCMessage
from .irc_level import IRCLevel, get_userlevels
from socket import create_connection
from importlib import import_module, reload
from os import listdir
from time import strftime, localtime
import re
import traceback


class IRCBot:
    def __init__(self, nick, server, port=6667, command_prefix='.'):
        self.nick = nick
        self.server = server
        self.port = port
        self.command_prefix = command_prefix

        self.socket = None
        self.running = self.connected = self.identified = False
        self.read_buffer = ''

        self.database = None
        self.channels = []
        self.ignore_list = []
        self.userlevels = {}

        self.plugins = {}
        self.commands = {}
        self.patterns = []

        self.flood_guard = {}

    def run(self):
        self.running = True
        while self.running:
            self.__connect()
            while self.connected:
                try:
                    for msg in self.__recv():
                        message = IRCMessage(msg)
                        self.__handle_message(message)
                except:
                    traceback.print_exc()

    def load_plugins(self, folder):
        self.commands = {}
        self.patterns = []

        for file in listdir(folder):
            if file.endswith('.py'):
                module_name = folder + '.' + file[:-3]
                if module_name not in self.plugins:
                    print("Loading {}".format(module_name))
                    module = import_module(module_name)
                    self.plugins[module_name] = module
                else:
                    print("Reloading {}".format(module_name))
                    reload(self.plugins[module_name])

    def reload_plugins(self):
        for module_name, module in self.plugins.items():
            print("Reloading {}".format(module_name))
            reload(module)

    def load_database(self, database_path):
        pass

    def set_val(self, name, val):
        pass

    def get_val(self, name, default=None):
        pass

    def join(self, channel):
        if self.connected:
            self.send('JOIN ' + channel)
        self.channels.append(channel)

    def ignore(self, hostmask):
        pattern = re.compile(hostmask.replace('*', '.*'), re.IGNORECASE)
        self.ignore_list.append(pattern)

    def __ignored(self, host):
        if host is None:
            return False

        for pattern in self.ignore_list:
            if pattern.match(host):
                return True
        else:
            return False

    def userlevel_wrapper(self, level, func):
        def wrapped(message):
            userlevel = max(self.userlevels.get(
                (message.nick, message.channel), IRCLevel.user))
            if userlevel >= level:
                return func(message)
        return wrapped

    def command(self, name, level=IRCLevel.user):
        def register_command(func):
            func = self.userlevel_wrapper(level, func)
            self.commands[name] = func
            return func
        return register_command

    def match(self, pattern, level=IRCLevel.user):
        def register_pattern(func):
            func = self.userlevel_wrapper(level, func)
            self.patterns.append((re.compile(pattern, re.IGNORECASE), func))
            return func
        return register_pattern

    def __connect(self):
        self.socket = create_connection((self.server, self.port))
        self.connected = True
        self.identified = False

    def disconnect(self):
        self.running = self.connected = self.identified = False

    def __recv(self):
        self.read_buffer += self.socket.recv(512).decode('UTF-8')
        msgs = self.read_buffer.split('\r\n')
        self.read_buffer = msgs.pop()
        return msgs

    def send(self, msg):
        if msg is not None:
            self.socket.send(bytes(msg + '\r\n', 'UTF-8'))
            print("Sent: {}".format(msg))

    def __handle_message(self, message):
        print(message)

        if self.__ignored(message.sender):
            print("Ignored!")
            return

        mapping = {
            'PING': IRCBot.__handle_ping,
            'PRIVMSG': IRCBot.__handle_privmsg,
            'NOTICE': IRCBot.__handle_notice,
            'INVITE': IRCBot.__handle_invite,
            '353': IRCBot.__handle_names,
            'ERROR': IRCBot.__handle_error
        }
        if message.command.upper() in mapping:
            self.send(mapping[message.command.upper()](self, message))
        else:
            print("Unknown command: {}".format(message.command))

    def __handle_ping(self, message):
        self.send('PONG :' + message.message)

    def __handle_privmsg(self, message):
        response = None

        target = message.channel \
            if is_channel(message.channel) \
            else message.nick

        if message.message.startswith(self.command_prefix):
            response = self.commands[len(self.command_prefix):](message)
            if response is not None:
                response = 'PRIVMSG {} :{}'.format(target, response)

        elif is_ctcp(message):
            response = ctcp_response(message.message[1:-1])
            if response is not None:
                response = 'NOTICE {} :\u0001{}\u0001'.format(target, response)

        else:
            for pattern, func in self.patterns:
                if pattern.search(message.message):
                    response = func(message)
                    if response is not None:
                        response = 'PRIVMSG {} :{}'.format(target, response)

        return response

    def __handle_notice(self, message):
        if not self.identified:
            self.send('USER MotoBot localhost localhost MotoBot')
            self.send('NICK ' + self.nick)
            for channel in self.channels:
                self.send('JOIN ' + channel)
            self.identified = True

    def __handle_invite(self, message):
        self.join(message.message)

    def __handle_names(self, message):
        channel = message.channel.split(' ')[-1]
        for nick in message.message.split(' '):
            self.userlevels[(nick.lstrip('+%@&~'), channel)] = \
                get_userlevels(nick)

    def __handle_error(self, message):
        self.connected = self.identified = False


def is_channel(name):
    valid = ['#', '!', '@', '&']
    return name[0] in valid and ' ' not in name and ',' not in name


def is_ctcp(message):
    return message.message.startswith('\u0001') and \
        message.message.endswith('\u0001')


def ctcp_response(message):
    mapping = {
        'VERSION': 'MotoBot Version 2.0',
        'FINGER': 'Oh you dirty man!',
        'TIME': strftime('%a %b %d %H:%M:%S', localtime()),
        'PING': message
    }
    return mapping.get(message.split(' ')[0].upper(), None)
