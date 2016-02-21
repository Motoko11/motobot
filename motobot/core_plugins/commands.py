from motobot import command, Notice, split_response, IRCBot
from collections import defaultdict


def filter_plugins(plugins, userlevel):
    return map(
        lambda plugin: (plugin.arg.trigger, plugin.func), filter(
            lambda plugin: plugin.type == IRCBot.command_plugin and
                           plugin.level <= userlevel and not plugin.arg.hidden,
            plugins
        )
    )


def format_group(group):
    return '({})'.format(', '.join(group)) if len(group) != 1 else group[0]


@command('commands')
def commands_command(bot, context, message, args):
    userlevel = bot.get_userlevel(context.channel, context.nick)
    groups = defaultdict(lambda: [])

    for command, func in filter_plugins(bot.plugins, userlevel):
        groups[func].append(command)

    commands = map(format_group, sorted(groups.values(), key=lambda x: x[0]))
    response = split_response(commands, "Bot Commands: {};")

    return response, Notice(context.nick)
