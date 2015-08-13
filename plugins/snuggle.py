from desubot import bot


def action(message):
    return '\u0001ACTION {}\u0001'.format(message)


@bot.command('snuggle')
def snuggle_command(message):
    response = ''
    args = message.message.split(' ')
    if len(args) > 1:
        response = 'snuggles ' + args[1]
    else:
        response = 'snuggles ' + message.nick
    
    return action(response)


@bot.command('unsnuggle')
def unsnuggle_command(message):
    return "Go ahead and call the cops... You can't be unsnuggled!"


@bot.command('pat')
def pat_command(message):
    response = ''
    args = message.message.split(' ')
    if len(args) > 1:
        response = 'pat pats ' + args[1]
    else:
        response = 'pat pats ' + message.nick
    
    return action(response)