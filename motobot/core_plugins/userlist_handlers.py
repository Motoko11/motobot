from motobot import hook
from ..irc_level import get_userlevels


@hook('353')
def __handle_names(bot, message):
    """ Parse the name command and record the userlevels of users. """
    channel = message.channel.split(' ')[-1]
    for nick in message.message.split(' '):
        bot.userlevels[(nick.lstrip('+%@&~'), channel)] = \
            get_userlevels(nick)


@hook('JOIN')
def __handle_join(bot, message):
    """ Handle the join of a user. """
    bot.userlevels[(message.nick, message.message)] = [0]


@hook('MODE')
def __handle_mode(bot, message):
    """ Handle the mode command and update userlevels accordingly. """
    pass


@hook('PART')
@hook('QUIT')
def __handle_leave(bot, message):
    """ Handle the part or quit of a user. """
    pass
