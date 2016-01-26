from motobot import IRCBot, command, Notice


def get_command_help(bot, command, modifier):
    responses = []

    func = lambda x: x.type == IRCBot.command_plugin and x.arg.lower() == command.lower()
    for plugin in filter(func, bot.plugins):
        func = plugin.func

        if func.__doc__ is not None:
            responses.append((' '.join(func.__doc__.split()), modifier))
    return responses


@command('help')
def help_command(bot, database, nick, channel, message, args):
    """ Print help messages for the user.

    Takes a single argument for a command name.
    No arguments gives a generic help message.
    """
    response = None
    modifier = Notice(nick)

    if len(args) <= 1:
        default_help = "For help on a specific command use '!help command'."
        response = bot.default_help \
            if bot.default_help is not None else default_help
        response = (response, modifier)
    else:
        response = get_command_help(bot, args[1], modifier)

        if response == []:
            response = ("There is no help entry for the command: {}.".format(args[1]), modifier)

    return response
