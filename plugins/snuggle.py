from motobot import command, action


@command('snuggle')
def snuggle_command(bot, nick, channel, message, args):
    response = ''
    if len(args) > 1:
        response = 'snuggles ' + ' '.join(args[1:])
    else:
        response = 'snuggles ' + nick

    return action(response)


@command('unsnuggle')
def unsnuggle_command(bot, nick, channel, message, args):
    return "Go ahead and call the cops... You can't be unsnuggled!"


@command('pat')
def pat_command(bot, nick, channel, message, args):
    response = ''
    if len(args) > 1:
        response = 'pat pats ' + ' '.join(args[1:])
    else:
        response = 'pat pats ' + nick

    return action(response)


@command('pet')
def pet_command(bot, nick, channel, message, args):
    response = ''
    if len(args) > 1:
        response = 'pets ' + ' '.join(args[1:])
    else:
        response = 'pets ' + nick

    return action(response)
