from motobot import command, action


@command('snuggle')
def snuggle_command(bot, message, database):
    response = ''
    args = message.message.split(' ')
    if len(args) > 1:
        response = 'snuggles ' + ' '.join(args[1:])
    else:
        response = 'snuggles ' + message.nick
    
    return action(response)


@command('unsnuggle')
def unsnuggle_command(bot, message, database):
    return "Go ahead and call the cops... You can't be unsnuggled!"


@command('pat')
def pat_command(bot, message, database):
    response = ''
    args = message.message.split(' ')
    if len(args) > 1:
        response = 'pat pats ' + ' '.join(args[1:])
    else:
        response = 'pat pats ' + message.nick
    
    return action(response)


@command('pet')
def pet_command(bot, message, database):
    response = ''
    args = message.message.split(' ')
    if len(args) > 1:
        response = 'pets ' + ' '.join(args[1:])
    else:
        response = 'pets ' + message.nick
    
    return action(response)
