from motobot import hook, sink, Priority


def check(bot, nick):
    """ Check a user by sending a WHOIS query. """
    if bot.is_master(nick, False):
        bot.send('WHOIS ' + nick)


def verify(bot, nick):
    """ Mark a master as verified in the bot. """
    if bot.is_master(nick, False):
        index = [master.lower() for master in bot.masters].index(nick.lower())
        bot.verified_masters.append(bot.masters.pop(index))


def unverify(bot, nick):
    """ Unmark a user as verified in the bot. """
    if bot.is_master(nick):
        index = [master.lower() for master in bot.verified_masters].index(nick.lower())
        bot.masters.append(bot.verified_masters.pop(index))


@hook('307')
def registered_nick_confirm(bot, message):
    """ Hooks the user is registered reply from a WHOIS query and verifies user. """
    verify(bot, message.params[1])


@sink(priority=Priority.max)
def master_verification_sink(bot, database, context, message):
    """ Checks a user that speaks in the channel. """
    check(bot, context.nick)


@hook('353')
def handle_names(bot, message):
    """ Check users whom are present in the channel upon joining. """
    channel = message.params[2]
    names = message.params[-1].split(' ')
    for name in names:
        check(bot, name.lstrip('+%@&~'))


@hook('JOIN')
def handle_join(bot, message):
    """ Check a user that joins a channel. """
    check(bot, message.nick)


@hook('NICK')
def handle_nick(bot, message):
    """ Unmark a user as verified in the bot and check new nick. """
    unverify(bot, message.nick)
    check(bot, message.params[0])


@hook('QUIT')
def handle_quit(bot, message):
    """ Unmark a user as verified in the bot upon quit. """
    unverify(bot, message.nick)
