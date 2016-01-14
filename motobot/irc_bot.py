from .irc_message import IRCMessage
from .irc_level import IRCLevel, get_userlevels
from .database import Database
from socket import create_connection
from importlib import import_module, reload
from os import listdir
from time import strftime, localtime, sleep, time
import re
import traceback


class IRCBot:

    """ IRCBot Class, plug in and go! """

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
        self.flood_protection = {}

        self.plugins = {}
        self.commands = {}
        self.patterns = []
        self.sinks = []

        self.channels = []
        self.ignore_list = []
        self.userlevels = {}

        self.database = Database()

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

    def load_plugins(self, folder):
        """ Load or reload plugins from folder. """
        self.commands = {}
        self.patterns = []
        self.sinks = []

        for file in listdir(folder):
            if file.endswith('.py'):
                module_name = folder + '.' + file[:-3]
                self.__load_module(module_name)

    def reload_plugins(self):
        """ Reload all loaded plugins. """
        self.commands = {}
        self.patterns = []
        self.sinks = []

        for module_name in self.plugins.keys():
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
            self.__add_command(func)
            self.__add_pattern(func)
            self.__add_sink(func)

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

    def __flood_protect(self, message):
        default = (0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        message_times = self.flood_protection.get(message.sender, default)
        current_time = time()

        if message_times[0] >= current_time or \
           all(x <= current_time + 60 for x in message_times[1]):
            self.flood_protection[message.sender] = (current_time + 5 * 60, message_times[1])
            return False
        else:
            message_times[1].pop(0)
            message_times[1].append(current_time)
            self.flood_protection[message.sender] = message_times
            return True

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

        if self.__flood_protect(message):
            print("Flood protected")
            return None

        target = message.channel \
            if is_channel(message.channel) \
            else message.nick

        if message.message.startswith(self.command_prefix):
            command = message.message.split(' ')[0][len(self.command_prefix):]
            response = self.commands[command](self, message, self.database)
            if response is not None:
                response = 'PRIVMSG {} :{}'.format(target, response)

        elif is_ctcp(message):
            response = ctcp_response(message.message[1:-1])
            if response is not None:
                response = 'NOTICE {} :\u0001{}\u0001'.format(target, response)

        else:
            for pattern, func in self.patterns:
                if pattern.search(message.message):
                    response = func(self, message, self.database)
                    if response is not None:
                        response = 'PRIVMSG {} :{}'.format(target, response)

            if response is None:
                for sink in self.sinks:
                    response = sink(self, message, self.database)
                    if response is not None:
                        response = 'PRIVMSG {} :{}'.format(target, response)
                        break

        return response

    def __handle_notice(self, message):
        """ Use the notice message to identify and register to the server. """
        if not self.identified:
            self.send('USER MotoBot localhost localhost MotoBot')
            self.send('NICK ' + self.nick)
            sleep(2)

            if self.nickserv_password is not None:
                self.send('PRIVMSG nickserv :identify ' + self.nickserv_password)
                sleep(2)
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
    def wrapped(bot, message, *args, **kwargs):
        if max(bot.userlevels.get((message.nick, message.channel), [IRCLevel.user])) >= level:
            return func(bot, message, *args, **kwargs)
    return wrapped


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


def action(message):
    """ Make the message an action. """
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
    """ Strip the control codes from the input. """
    pattern = re.compile(r'\x03[0-9]{0,2},?[0-9]{0,2}|\x02|\x1D|\x1F|\x16|\x0F')
    output = pattern.sub('', input)
    return output
