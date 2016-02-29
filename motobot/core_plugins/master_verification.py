from motobot import hook, sink, request, Priority


def get_master_lists(bot, session):
    confirmed, unconfirmed = session.get((set(), None))

    if unconfirmed is None:
        unconfirmed = set(map(str.lower, bot.masters))
        session.set((confirmed, unconfirmed))

    return confirmed, unconfirmed


@request('IS_MASTER')
def is_master_request(bot, context, nick):
    confirmed = get_master_lists(bot, context.session)[0]
    return nick.lower() in confirmed


def check(bot, session, nick):
    """ Check a user by sending a WHOIS query. """
    confirmed, unconfirmed = get_master_lists(bot, session)

    if nick.lower() in unconfirmed:
        bot.send('WHOIS ' + nick)


def verify(bot, session, nick):
    """ Mark a master as verified in the bot. """
    nick = nick.lower()
    confirmed, unconfirmed = get_master_lists(bot, session)

    try:
        unconfirmed.remove(nick)
        confirmed.add(nick)
    except KeyError:
        pass


def unverify(bot, session, nick):
    """ Unmark a user as verified in the bot. """
    nick = nick.lower()
    confirmed, unconfirmed = get_master_lists(bot, session)

    try:
        confirmed.remove(nick)
        unconfirmed.add(nick)
    except KeyError:
        pass


@hook('307')
def registered_nick_confirm(bot, context, message):
    """ Hooks the user is registered reply from a WHOIS query and verifies user. """
    verify(bot, context.session, message.params[1])


@sink(priority=Priority.max)
def master_verification_sink(bot, context, message):
    """ Checks a user that speaks in the channel. """
    check(bot, context.session, context.nick)


@hook('353')
def handle_names(bot, context, message):
    """ Check users whom are present in the channel upon joining. """
    channel = message.params[2]
    names = message.params[-1].split(' ')
    for name in names:
        check(bot, context.session, name.lstrip('+%@&~'))


@hook('JOIN')
def handle_join(bot, context, message):
    """ Check a user that joins a channel. """
    check(bot, context.session, message.nick)


@hook('NICK')
def handle_nick(bot, context, message):
    """ Unmark a user as verified in the bot and check new nick. """
    unverify(bot, context.session, message.nick)
    check(bot, context.session, message.params[0])


@hook('QUIT')
def handle_quit(bot, context, message):
    """ Unmark a user as verified in the bot upon quit. """
    unverify(bot, context.session, message.nick)
