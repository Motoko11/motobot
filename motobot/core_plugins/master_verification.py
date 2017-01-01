from motobot import hook, request, command, BotError, Notice, hostmask_check, Priority, IRCLevel, split_response


@request('IS_MASTER')
def is_master_request(bot, context, nick, host=None):
    recognised = context.session.get(set())
    admin_masks = context.database.get([])
    return nick.lower() in recognised or \
           any(hostmask_check(nick, host, mask) for mask in admin_masks)


@command('identify', hidden=True, priority=Priority.max)
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


@command('adminmask')
def adminmask_command(bot, context, message, args):
    try:
        arg = args[1].lower()
        if arg == 'add':
            response = add_mask(context.database, args[2])
        elif arg in ('del', 'rem'):
            response = del_mask(context.database, args[2])
        elif arg in ('show', 'list'):
            response = show_masks(context.database)
        else:
            response = 'Error: Invalid argument;'
    except IndexError:
        response = "Not enough arguments provided."
    return response, Notice(context.nick)


def add_mask(database, mask):
    masks = database.get([])
    if mask not in masks:
        masks.append(mask)
        database.set(masks)
        response = "Mask added successfully."
    else:
        response = "Error: Mask already in masks list."
    return response


def del_mask(database, mask):
    masks = database.get([])
    try:
        masks.remove(mask)
        database.set(masks)
        response = "Mask successfully deleted."
    except ValueError:
        response = "Error: Mask not in masks list."
    return response


def show_masks(database):
    masks = database.get([])

    if masks:
        response = split_response(masks, "Admin masks: {};")
    else:
        response = "I don't have any admin masks."

    return response