from motobot import hook, request, command, BotError, Notice, hostmask_check


@request('IS_MASTER')
def is_master_request(bot, context, nick, host=None):
    recognised = context.session.get(set())
    admin_masks = context.database.get([])
    return nick.lower() in recognised or \
           any(hostmask_check(nick, host, mask) for mask in admin_masks)


@command('identify', hidden=True)
def identify_command(bot, context, message, args):
    try:
        password = bot.admin_pass
    except AttributeError:
        raise BotError("Error: I've not been configured with a password.", Notice(context.nick))

    input_pass = ' '.join(args[1:])
    if input_pass == password:
        recognise(context.session, context.nick)
        response = 'You are now recognised as a bot admin.'
    else:
        response = 'Error: Password incorrect.'
    return response, Notice(context.nick)


def recognise(session, nick):
    admins = session.get(set())
    admins.add(nick.lower())
    session.set(admins)
