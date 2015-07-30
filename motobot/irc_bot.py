from . import Bot
from . import IRCMessage
from os import listdir
from time import sleep
import re


class IRCBot(Bot):

    """ Class to inherit from Bot and abstract the IRC protocol. """

    def __init__(self, nick, server, port=6667, command_prefix='.'):
        """ Create a new IRCBot instance. """
        Bot.__init__(self, server, port, message_ending='\r\n')
        self.nick = nick
        self.command_prefix = command_prefix
        self.userlist = {}
        self.hook(message_handler)

    def init(self):
        """ Overload init function to load plugin modules. """
        self.load_modules()

    def load_modules(self):
        """ Load the plugin modules for the bot.

        Loads the modules from the package 'modules'.
        This can easily be abstracted later to an __init__ argument.

        """
        self.commands = {}
        self.patterns = []

        modules_folder = 'modules'
        for file in listdir(modules_folder):
            if file.endswith('.py'):
                module = file[:-3]
                plugin = __import__(modules_folder + '.' + module,
                                    globals(), locals(), -1)

    def command(self, name):
        """ Decorator to register a command to the bot.

        Commands are triggered the the string name and
        are prefixed with command_prefix.

        """
        def register_command(func):
            self.commands[name] = func
            return func
        return register_command

    def match(self, pattern):
        """ Decorator to register a regex pattern to the bot.

        Commands are triggered when a message sent to the bot or
        a channel the bot occupies matches for the given pattern.

        """
        def register_pattern(func):
            self.patterns.append((re.compile(pattern), func))
            return func
        return register_pattern

    def get_userlevel(self, nick, channel):
        """ Return the userlevel of a user in a given channel. """
        # TODO: As per raylu's suggestion, integrate this into the decorator
        return self.userlist[(channel, nick)]


# TODO:
# Clean all this shit up.
# I want to restructure it to a more readable/followable form
# snd to make it more clearly extensible as it really is.
message_handlers = {}


def hook(name):
    def register_hook(func):
        message_handlers[name] = func
        return func
    return register_hook


def message_handler(bot, msg):
    message = IRCMessage(msg)
    response = None

    if message.command in message_handlers:
        response = message_handlers[message.command](bot, message)

    return response


@hook('439')
def identify_hook(bot, message):
    bot.send('USER MotoBot localhost localhost MotoBot')
    sleep(1)
    bot.send('NICK ' + bot.nick)
    bot.send('JOIN #Moto-chan')
    bot.send('JOIN #animu')
    bot.send('JOIN #anime-planet.com')


@hook('PING')
def ping_hook(bot, message):
    return 'PONG :' + message.message


@hook('ERROR')
def error_hook(bot, message):
    bot.connected = False


@hook('INVITE')
def invite_hook(bot, message):
    return 'JOIN ' + message.message


@hook('353')
def names_hook(bot, message):
    channel = message.channel.split(' ')[2]

    for name in message.message.split(' '):
        level = get_level(name[0])
        nick = name if level == 0 else name[1:]
        bot.userlist[(channel, nick)] = level


def get_level(symbol):
    mapping = {
        '~': 5,
        '&': 4,
        '@': 3,
        '%': 2,
        '+': 1
    }
    return mapping[symbol] if symbol in mapping else 0


@hook('PRIVMSG')
def msg_hook(bot, message):
    response = None
    if message.message.startswith(bot.command_prefix):
        command = message.message.split(' ')[0][1:]
        if command in bot.commands:
            response = bot.commands[command](message)

    else:
        for pattern, func in bot.patterns:
            if pattern.search(message.message):
                response = func(message)

    if response is not None:
        target = message.channel \
            if is_channel(message.channel) else message.nick
        return 'PRIVMSG ' + target + ' :' + response


def is_channel(channel_name):
    """ Ugliest function ever """
    return (channel_name[0] == '#' or
            channel_name[0] == '@' or
            channel_name[0] == '+' or
            channel_name[0] == '!') and \
            ' ' not in channel_name and \
            ',' not in channel_name
