from motobot import command, request, IRCLevel, Priority, Notice, split_response


@request('GET_PLUGINS')
def disabled_request(bot, context, channel):
    disabled = context.database.get({}).get(channel.lower(), set())
    return filter_plugins(bot.plugins, disabled)


def filter_plugins(plugins, disabled):
    return filter(
        lambda plugin: plugin.priority == Priority.max or
                       plugin.module.lower() not in disabled,
        plugins
    )


@command('module', priority=Priority.max, level=IRCLevel.op)
def module_command(bot, context, message, args):
    """ Command to enable or disable modules in the bot.

    The 'enable' and 'disable' argument both require a module argument.
    The 'show' argument will show the currently disabled modules in the channel.
    The 'list' argument will return a list of modules in the bot.
    If 'list' is called with an argument, it'll return a list of plugins in that module.
    The 'get' argument will return the module a particular command is located in.
    """
    try:
        arg = args[1].lower()

        if arg == 'enable':
            module = ' '.join(args[2:])
            response = enable_module(context.database, context.channel, module)
        elif arg == 'disable':
            module = ' '.join(args[2:])
            response = disable_module(bot, context.database, context.channel, module)
        elif arg == 'show':
            response = show_disabled_modules(context.database, context.channel)
        elif arg == 'list':
            module = ' '.join(args[2:])
            response = list_module(bot, module)
        elif arg == 'get':
            module = ' '.join(args[2:])
            response = get_module(bot, module)
        else:
            response = "Error: Invalid argument."
    except IndexError:
        response = "Error: Too few arguments supplied."

    return response, Notice(context.nick)


def enable_module(database, channel, module):
    return "Error: Not yet implemented."


def disable_module(bot, database, channel, module):
    return "Error: Not yet implemented."


def show_disabled_modules(database, channel):
    return "Error: Not yet implemented."


def list_module(bot, module):
    if module:
        pass
    else:
        response = split_response(bot.modules, "Modules: {};")

    return response


def get_module(bot, module):
    return "Error: Not yet implemented."
