from motobot import command, request, IRCLevel, Priority, Notice, split_response


@request('GET_PLUGINS')
def disabled_request(bot, context, channel):
    disabled = context.database.get({}).get(channel.lower(), [])
    return filter_plugins(bot.plugins, disabled)


def filter_plugins(plugins, disabled):
    return filter(
        lambda plugin: plugin.priority == Priority.max or
                       plugin.module.lower() not in disabled,
        plugins
    )


def get_modules(bot):
    return [module for module in bot.modules if not module.startswith('motobot.core_plugins')]


def user_module_command(bot, context, message, args):
    try:
        arg = args[1].lower()

        if arg == ('enable', 'disable', 'show'):
            response = "Error: You do not have the privileges to use this argument."
        elif arg == 'list':
            module = ' '.join(args[2:])
            response = list_module(get_modules(bot), module)
        elif arg == 'get':
            module = ' '.join(args[2:])
            response = get_module(get_modules(bot), module)
        else:
            response = "Error: Invalid argument."
    except IndexError:
        response = "Error: Too few arguments supplied."

    return response, Notice(context.nick)


@command('module', priority=Priority.max, level=IRCLevel.op, alt=user_module_command)
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
            response = disable_module(get_modules(bot), context.database, context.channel, module)
        elif arg == 'show':
            response = show_disabled_modules(context.database, context.channel)
        elif arg == 'list':
            module = ' '.join(args[2:])
            response = list_module(get_modules(bot), module)
        elif arg == 'get':
            module = ' '.join(args[2:])
            response = get_module(get_modules(bot), module)
        else:
            response = "Error: Invalid argument."
    except IndexError:
        response = "Error: Too few arguments supplied."

    return response, Notice(context.nick)


def enable_module(database, channel, module):
    channel = channel.lower()
    disabled_modules = database.get({})
    disabled_channel_modules = disabled_modules.get(channel, [])

    try:
        disabled_channel_modules.remove(module)
        disabled_modules[channel] = disabled_channel_modules
        database.set(disabled_modules)
        response = "{} is now enabled in {}.".format(module, channel)
    except ValueError:
        response = "{} was not disabled in {}.".format(module, channel)
    return response


def disable_module(modules, database, channel, module):
    if module in modules:
        channel = channel.lower()
        disabled_modules = database.get({})
        disabled_channel_modules = disabled_modules.get(channel, [])

        if module in disabled_channel_modules:
            response = "{} is already disabled in {}.".format(module, channel)
        else:
            disabled_channel_modules.append(module)
            disabled_modules[channel] = disabled_channel_modules
            database.set(disabled_modules)
            response = "{} successfully disabled in {}.".format(module, channel)
    else:
        response = "{} is not a valid module.".format(module)

    return response


def show_disabled_modules(database, channel):
    disabled_channel_modules = database.get({}).get(channel.lower(), [])
    if disabled_channel_modules:
        response = split_response(disabled_channel_modules,
                                  "Disabled modules in {}: {};".format(channel, '{}'))
    else:
        response = "I have no modules disabled in {}.".format(channel)
    return response


def list_module(modules, module):
    if module:
        response = None  # TODO
    else:
        response = split_response(modules, "Modules: {};")

    return response


def get_module(modules, module):
    return "Error: Not yet implemented."
