from motobot import IRCBot, hook, Priority, Context, strip_control_codes
from motobot.modifiers import Modifier, CommandModifier, ParamsModifier, TrailingModifier, EatType


@hook('PRIVMSG')
def handle_privmsg(bot, context, message):
    """ Handle the privmsg commands.

    Will send messages to each plugin accounting for priority and level.

    """
    nick = message.nick
    channel = message.params[0]
    target = channel if channel != bot.nick else nick
    message = strip_control_codes(transform_action(nick, message.params[-1]))
    messages = list(split_messages(message, bot.command_prefix))

    break_priority = Priority.min
    for plugin in bot.plugins:
        if break_priority > plugin.priority:
            break
        else:
            try:
                responses = handle_plugin(bot, plugin, nick, channel, messages)
                if handle_responses(bot, responses, [target]):
                    break_priority = plugin.priority
            except:
                bot.log_error()


def transform_action(nick, msg):
    """ Transform an action CTCP into a message. """
    if msg.startswith('\x01ACTION ') and msg.endswith('\x01'):
        return '*' + nick + msg[7:-1]
    else:
        return msg


def split_messages(message, command_prefix):
    messages = iter(message.split('|'))
    current_message = next(messages)

    for message in messages:
        test_message = message.lstrip(' ')
        if test_message.startswith(command_prefix):
            yield current_message
            current_message = test_message
        else:
            current_message += '|' + message
    yield current_message


def handle_plugin(bot, plugin, nick, channel, messages):
    responses = None

    for message in messages:
        if responses is None:
            responses = call_plugins([plugin], bot, nick, channel, message)
        else:
            responses = handle_pipe(bot, nick, channel, message, responses)

    return responses


def call_plugins(plugins, bot, nick, channel, message):
    for plugin in plugins:
        response = None
        module = plugin.func.__module__
        context = Context(nick, channel, bot.database.get_entry(module),
                          bot.sessions.get_entry(module))
        if plugin.type == IRCBot.command_plugin:
            response = handle_command(plugin, bot, context, message)
        elif plugin.type == IRCBot.match_plugin:
            response = handle_match(plugin, bot, context, message)
        elif plugin.type == IRCBot.sink_plugin:
            response = handle_sink(plugin, bot, context, message)
        if response is not None:
            yield response


def handle_pipe(bot, nick, channel, message, responses):
    plugins = list(filter(lambda x: x.type == IRCBot.command_plugin, bot.plugins))
    for x in responses:
        if isinstance(x, str):
            yield call_plugins(plugins, bot, nick, channel, message.rstrip(' ') + ' ' + x)
        elif isinstance(x, Modifier):
            yield x
        else:
            yield handle_pipe(bot, nick, channel, message, x)


def handle_command(plugin, bot, context, message):
    trigger = bot.command_prefix + plugin.arg.trigger
    test = message.split(' ', 1)[0]

    if trigger == test:
        alt = bot.request('USERLEVEL', context.channel, context.nick) < plugin.level
        func = plugin.func if not alt else plugin.alt
        if func is not None:
            args = message[len(bot.command_prefix):].split(' ')
            return func(bot, context, message, args)


def handle_match(plugin, bot, context, message):
    match = plugin.arg.search(message)
    if match is not None:
        alt = bot.request('USERLEVEL', context.channel, context.nick) < plugin.level
        func = plugin.func if not alt else plugin.alt
        if func is not None:
            return func(bot, context, message, match)


def handle_sink(plugin, bot, context, message):
    alt = bot.request('USERLEVEL', context.channel, context.nick) < plugin.level
    func = plugin.func if not alt else plugin.alt
    if func is not None:
        return func(bot, context, message)


def handle_responses(bot, responses, params, command='PRIVMSG', trailing_mods=None, require_trailing=True):
    eat = False
    trailings = []
    command_mods = []
    param_mods = []
    trailing_mods = [] if trailing_mods is None else trailing_mods
    iters = []
    eat |= extract_responses(responses, trailings, command_mods,
                             param_mods, trailing_mods, iters)

    for modifier in command_mods:
        require_trailing &= modifier.require_trailing
        command = modifier.modify_command(command)
    for modifier in param_mods:
        require_trailing &= modifier.require_trailing
        params = modifier.modify_params(params)

    if not require_trailing and not trailings:
        trailings = ['']

    for trailing in trailings:
        for modifier in trailing_mods:
            trailing = modifier.modify_trailing(trailing)
        message = form_message(command, params, trailing)
        bot.send(message)

    for iter in iters:
            eat |= handle_responses(bot, iter, params, command, trailing_mods, require_trailing)
    return eat


def extract_responses(responses, trailings, command_mods,
                      param_mods, trailing_mods, iters):
    will_eat = False

    for x in responses:
        if isinstance(x, EatType):
            will_eat = True
        elif isinstance(x, str):
            trailings.append(x)
        elif isinstance(x, Modifier):
            if isinstance(x, CommandModifier):
                command_mods.append(x)
            if isinstance(x, ParamsModifier):
                param_mods.append(x)
            if isinstance(x, TrailingModifier):
                trailing_mods.append(x)
        else:
            iters.append(x)

    return will_eat


def form_message(command, params, trailing):
    message = command
    message += ' ' + ' '.join(params) if params else ''
    message += ' :' + trailing if trailing else ''
    return message
