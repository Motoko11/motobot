from . import Bot
from . import IRCMessage
from os import listdir
from importlib import import_module
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
        self.commands = {}
        self.patterns = []

        self.msg_hook(IRCBot.__handle_msg)

    def init(self):
        """ Overload init function to load plugin modules. """
        IRCBot.load_hooks()
        self.load_modules()

    def load_modules(self):
        """ Load the plugin modules for the bot.

        Loads the modules from the package 'modules'.
        This can easily be abstracted later to an __init__ argument.

        """
        self.commands = {}
        self.patterns = []

        modules_package = 'modules'
        for file in listdir(modules_package):
            if file.endswith('.py'):
                module = file[:-3]
                plugin = __import__(modules_package + '.' + module,
                                    globals(), locals(), -1)

    @staticmethod
    def message_hook(command):
        """ Hooks a function to handle an IRCMessage object for a given command. """
        def register_hook(func):
            IRCBot.message_hooks[command] = func
            return func
        return register_hook

    @staticmethod
    def load_hooks():
        """ Load the message hook functions for the bot.

        Loads the hooks from the package 'hooks' within motobot.

        """
        IRCBot.message_hooks = {}
        import_module('motobot.hooks')

    def __handle_msg(self, msg):
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
