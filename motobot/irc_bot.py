from . import Bot
from . import IRCMessage
from os import listdir
from time import sleep
import re


class IRCBot(Bot):

    """ Class to inherit from Bot and abstract the IRC protocol. """

    message_hooks = {}

    def __init__(self, nick, server, port=6667, command_prefix='.'):
        """ Create a new IRCBot instance. """
        Bot.__init__(self, server, port, message_ending='\r\n')
        self.nick = nick
        self.command_prefix = command_prefix
        self.userlist = {}
        self.msg_hook(IRCBot.handle_msg)

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

    @staticmethod
    def message_hook(command):
        """ Hooks a function to handle an IRCMessage object for a given command. """
        def register_hook(func):
            IRCBot.message_hooks[command] = func
            return func
        return register_hook

    def handle_msg(self, msg):
        """ Constructs an IRCMessage from msg and passes it to the appropriate message_hook. """
        message = IRCMessage(msg)
        print(message)

        response = None
        if message.command in IRCBot.message_hooks:
            response = IRCBot.message_hooks[message.command](self, message)
        return response

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
            self.patterns.append((re.compile(pattern, re.IGNORECASE), func))
            return func
        return register_pattern

    def get_userlevel(self, nick, channel):
        """ Return the userlevel of a user in a given channel. """
        # TODO: As per raylu's suggestion, integrate this into the decorator
        return self.userlist[(channel, nick)]


# TODO:
# Clean all this shit up.
# I want to restructure it to a more readable/followable form
# and to make it more clearly extensible as it really is.


@IRCBot.message_hook('439')
def identify_hook(bot, message):
    bot.send('USER MotoBot localhost localhost MotoBot')
    sleep(1)
    bot.send('NICK ' + bot.nick)
    # TODO: Actually make a way (Other than inviting) to have the bot join
    bot.send('JOIN #Moto-chan')
    bot.send('JOIN #animu')
    # bot.send('JOIN #anime-planet.com')


@IRCBot.message_hook('PING')
def ping_hook(bot, message):
    return 'PONG :' + message.message


@IRCBot.message_hook('ERROR')
def error_hook(bot, message):
    bot.connected = False


@IRCBot.message_hook('INVITE')
def invite_hook(bot, message):
    return 'JOIN ' + message.message


@IRCBot.message_hook('353')
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


@IRCBot.message_hook('PRIVMSG')
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
