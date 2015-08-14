from .irc_message import IRCMessage
from .irc_level import IRCLevel, get_userlevels
from socket import create_connection
from importlib import import_module, reload
from os import listdir
from time import strftime, localtime
import re
import traceback


class IRCBot:
    plugins = {}
    commands = {}
    patterns = []

    def __init__(self, nick, server, port=6667, command_prefix='.'):
        """ Create a new instance of IRCBot. """
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
                except:
                    traceback.print_exc()

    @staticmethod
    def load_plugins(folder):
        """ Load or reload plugins from folder. """
        IRCBot.commands = {}
        IRCBot.patterns = []

        for file in listdir(folder):
            if file.endswith('.py'):
                module_name = folder + '.' + file[:-3]
                if module_name not in IRCBot.plugins:
                    print("Loading {}".format(module_name))
                    module = import_module(module_name)
                    IRCBot.plugins[module_name] = module
                else:
                    print("Reloading {}".format(module_name))
                    reload(IRCBot.plugins[module_name])

    @staticmethod
    def reload_plugins():
        """ Reloads all loaded plugins. """
        for module_name, module in IRCBot.plugins.items():
            print("Reloading {}".format(module_name))
            reload(module)

    def load_database(self, database_path):
        """ Load the database. """
        pass

    def set_val(self, name, val):
        """ Set a value in the database. """
        pass

    def get_val(self, name, default=None):
        """ Get a value from the database, return default if non-existent. """
        pass

    def join(self, channel):
        """ Join a channel. """
        if self.connected:
            self.send('JOIN ' + channel)
        self.channels.append(channel)

    def ignore(self, hostmask):
        """ Ignore a user with the given hostmask. """
        pattern = re.compile(hostmask.replace('*', '.*'), re.IGNORECASE)
        self.ignore_list.append(pattern)

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
            mapping = {
                'PING': IRCBot.__handle_ping,
                'PRIVMSG': IRCBot.__handle_privmsg,
                'NOTICE': IRCBot.__handle_notice,
                'INVITE': IRCBot.__handle_invite,
                'JOIN': IRCBot.__handle_join,
                'PART': IRCBot.__handle_leave,
                'QUIT': IRCBot.__handle_leave,
                '353': IRCBot.__handle_names,
                'MODE': IRCBot.__handle_mode,
                'ERROR': IRCBot.__handle_error
            }
            if message.command.upper() in mapping:
                self.send(mapping[message.command.upper()](self, message))
            else:
                print("Unknown command: {}".format(message.command))

    def __handle_ping(self, message):
        """ Handle the server's pings. """
        self.send('PONG :' + message.message)

    def __handle_privmsg(self, message):
        """ Handle the privmsg commands.

        Will send the reply back to the channel the command was sent from, 
        or back to the user whom sent it in the case of a private message.
        Commands (prefixed with command_prefix) are executed, CTCP is handled,
        and the matches are checked.

        """
        response = None

        target = message.channel \
            if is_channel(message.channel) \
            else message.nick

        if message.message.startswith(self.command_prefix):
            command = message.message.split(' ')[0][len(self.command_prefix):]
            response = IRCBot.commands[command](self, message)
            if response is not None:
                response = 'PRIVMSG {} :{}'.format(target, response)

        elif is_ctcp(message):
            response = ctcp_response(message.message[1:-1])
            if response is not None:
                response = 'NOTICE {} :\u0001{}\u0001'.format(target, response)

        else:
            for pattern, func in IRCBot.patterns:
                if pattern.search(message.message):
                    response = func(self, message)
                    if response is not None:
                        response = 'PRIVMSG {} :{}'.format(target, response)

        return response

    def __handle_notice(self, message):
        """ Use the notice message to identify and register to the server. """
        if not self.identified:
            self.send('USER MotoBot localhost localhost MotoBot')
            self.send('NICK ' + self.nick)
            for channel in self.channels:
                self.send('JOIN ' + channel)
            self.identified = True

    def __handle_invite(self, message):
        """ Join a channel when invited. """
        self.join(message.message)

    def __handle_names(self, message):
        """ Parse the name command and record the userlevels of users. """
        channel = message.channel.split(' ')[-1]
        for nick in message.message.split(' '):
            self.userlevels[(nick.lstrip('+%@&~'), channel)] = \
                get_userlevels(nick)

    def __handle_join(self, message):
        """ Handle the join of a user. """
        self.userlevels[(message.nick, message.message)] = [0]

    def __handle_leave(self, message):
        """ Handle the part or quit of a user. """
        pass

    def __handle_mode(self, message):
        """ Handle the mode command and update userlevels accordingly. """
        pass

    def __handle_error(self, message):
        """ Handle an error message from the server. """
        self.connected = self.identified = False


def userlevel_wrapper(func, level):
    """ Modify a plugin to only take users above a certain userlevel. """
    def wrapped(bot, message):
        if max(bot.userlevels[(message.nick, message.channel)]) >= level:
            return func(message)
    return wrapped


def command(name, level=IRCLevel.user):
    """ Decorator to add a command to the bot. """
    def register_command(func):
        func = userlevel_wrapper(func, level)
        IRCBot.commands[name] = func
        return func
    return register_command


def match(pattern, level=IRCLevel.user):
    """ Decorator to add a regex pattern to the bot. """
    def register_pattern(func):
        func = userlevel_wrapper(func, level)
        IRCBot.patterns.append((re.compile(pattern, re.IGNORECASE), func))
        return func
    return register_pattern


def action(message):
    return '\u0001ACTION {}\u0001'.format(message)


def is_channel(name):
    """ Check if a name is a valid channel name or not. """
    valid = ['&', '#', '+', '!']
    invalid = [' ', ',', '\u0007']
    return (name[0] in valid) and all(c not in invalid for c in name)


def is_ctcp(message):
    """ Check if a message object is a ctcp message or not. """
    return message.message.startswith('\u0001') and \
        message.message.endswith('\u0001')


def ctcp_response(message):
    """ Return the appropriate response to a CTCP request. """
    mapping = {
        'VERSION': 'MotoBot Version 2.0',
        'FINGER': 'Oh you dirty man!',
        'TIME': strftime('%a %b %d %H:%M:%S', localtime()),
        'PING': message
    }
    return mapping.get(message.split(' ')[0].upper(), None)


def strip_control_codes(input):
    pattern = re.compile(r'\x03[0-9]{0,2},?[0-9]{0,2}|\x02|\x1D|\x1F|\x16|\x0F')
    output = pattern.sub('', input)
    return output
