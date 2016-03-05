from motobot import IRCBot, command, Notice


@command('help')
def help_command(bot, context, message, args):
    """ Print help messages for the user.

    Takes a single argument for a command name.
    No arguments gives a generic help message.
    """

    try:
        response = get_command_help(bot, args[1])
    except IndexError:
        default_help = "For a list of commands use '{0}commands'. For help on a specific command use '{0}help command'.".format(bot.command_prefix)
        response = getattr(bot, 'default_help', default_help)

    return response, Notice(context.nick)


def get_command_help(bot, command):
    has_help = False
    for docstring in filter_plugins(bot.plugins, command):
        if docstring is not None:
            has_help = True
            yield ' '.join(docstring.split())
    if not has_help:
        yield "There is no help entry for the command: {}.".format(command)


def filter_plugins(plugins, command):
    return map(
        lambda plugin: plugin.func.__doc__,
        filter(
            lambda plugin: plugin.type == IRCBot.command_plugin and
                           plugin.arg.trigger.lower() == command.lower(),
            plugins
        )
    )
