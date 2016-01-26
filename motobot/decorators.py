from .irc_bot import IRCBot
from .irc_level import IRCLevel
from .priority import Priority
from collections import namedtuple
from re import compile, IGNORECASE


Plugin = namedtuple('Plugin', 'func alt type priority level arg')


def hook(command):
    """ Decorator to add a hook to the bot. """
    def register_hook(func):
        attr = getattr(func, IRCBot.hook, [])
        attr.append(command)
        setattr(func, IRCBot.hook, attr)
        return func
    return register_hook


def command(name, *, level=IRCLevel.user, priority=Priority.medium, alt=None):
    """ Decorator to add a command to the bot. """
    def register_command(func):
        attr = getattr(func, IRCBot.plugin, [])
        plugin = Plugin(func, alt, IRCBot.command_plugin, priority, level, name)
        attr.append(plugin)
        setattr(func, IRCBot.plugin, attr)
        return func
    return register_command


def match(pattern, *, level=IRCLevel.user, priority=Priority.medium, alt=None):
    """ Decorator to add a regex pattern to the bot. """
    def register_pattern(func):
        attr = getattr(func, IRCBot.plugin, [])
        compiled = compile(pattern, IGNORECASE)
        plugin = Plugin(func, alt, IRCBot.match_plugin, priority, level, compiled)
        attr.append(plugin)
        setattr(func, IRCBot.plugin, attr)
        return func
    return register_pattern


def sink(*, level=IRCLevel.user, priority=Priority.medium, alt=None):
    """ Decorator to add sink to the bot. """
    def register_sink(func):
        attr = getattr(func, IRCBot.plugin, [])
        plugin = Plugin(func, alt, IRCBot.sink_plugin, priority, level, None)
        attr.append(plugin)
        setattr(func, IRCBot.plugin, attr)
        return func
    return register_sink
