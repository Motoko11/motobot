from motobot import command, action


@command('snuggle')
def snuggle_command(message, database):
    response = ''
    args = message.message.split(' ')
    if len(args) > 1:
        response = 'snuggles ' + args[1]
    else:
        response = 'snuggles ' + message.nick
    
    return action(response)


@command('unsnuggle')
def unsnuggle_command(message, database):
    return "Go ahead and call the cops... You can't be unsnuggled!"


@command('pat')
def pat_command(message, database):
    response = ''
    args = message.message.split(' ')
    if len(args) > 1:
        response = 'pat pats ' + args[1]
    else:
        response = 'pat pats ' + message.nick
    
    return action(response)


@command('pet')
def pet_command(message, database):
    response = ''
    args = message.message.split(' ')
    if len(args) > 1:
        response = 'pets ' + args[1]
    else:
        response = 'pets ' + message.nick
    
    return action(response)
