from motobot import hook, sink, Priority


def check(bot, nick):
    if bot.is_master(nick, False):
        bot.send('WHOIS ' + nick)


def verify(bot, nick):
    index = [master.lower() for master in bot.masters].index(nick.lower())
    bot.verified_masters.append(bot.masters.pop(index))


def unverify(bot, nick):
    index = [master.lower() for master in bot.verified_masters].index(nick.lower())
    bot.masters.append(bot.verified_masters.pop(index))


@hook('307')
def registered_nick_confirm(bot, message):
    verify(bot, message.params[1])


@sink(priority=Priority.max)
def master_verification_sink(bot, nick, channel, message):
    check(bot, nick)


@hook('353')
def handle_names(bot, message):
    channel = message.params[2]
    names = message.params[-1].split(' ')
    for name in names:
        check(bot, name.lstrip('+%@&~'))


@hook('JOIN')
def handle_join(bot, message):
    check(bot, message.nick)


@hook('NICK')
def handle_nick(bot, message):
    unverify(message.nick)
    check(bot, message.params[0])


@hook('QUIT')
def handle_quit(bot, message):
    unverify(bot, message.nick)
