from motobot import command, Notice, format_responses, IRCBot


@command('commands')
def commands_command(bot, database, context, message, args):
    userlevel = bot.get_userlevel(context.channel, context.nick)

    valid_command = lambda plugin: plugin.type == IRCBot.command_plugin \
        and plugin.level <= userlevel and not plugin.arg.hidden
    key = lambda plugin: (plugin.arg.trigger, plugin.func)

    command_groups = {}
    for command, func in map(key, filter(valid_command, bot.plugins)):
        value = command_groups.get(func, [])
        value.append(command)
        command_groups[func] = value

    format_group = lambda group: '({})'.format(', '.join(group)) \
        if len(group) != 1 else group[0]
    commands = map(format_group, sorted(command_groups.values(), key=lambda x: x[0]))
    response = format_responses(commands, "Bot Commands: {};")

    return response, Notice(context.nick)
