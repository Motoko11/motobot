from motobot import command, Action, match
from random import choice


@command('snuggle')
def snuggle_command(bot, context, message, args):
    """ Snuggle your favourite person. """
    response = ''
    if len(args) > 1:
        response = 'snuggles ' + ' '.join(args[1:])
    else:
        response = 'snuggles ' + context.nick

    return response, Action


@command('unsnuggle')
def unsnuggle_command(bot, context, message, args):
    """ Tell someone the cold hard truth. """
    return "Go ahead and call the cops... You can't be unsnuggled!"


@command('pat')
def pat_command(bot, context, message, args):
    """ Pat someone who deserves it. """
    response = ''
    if len(args) > 1:
        response = 'pat pats ' + ' '.join(args[1:])
    else:
        response = 'pat pats ' + context.nick

    return response, Action


@command('pet')
def pet_command(bot, context, message, args):
    """ Pet someone who really deserves it. """
    response = ''
    if len(args) > 1:
        response = 'pets ' + ' '.join(args[1:])
    else:
        response = 'pets ' + context.nick

    return response, Action


@command('michaeljackson')
def micky_command(bot, context, message, args):
    target = ''
    if len(args) > 1:
        target = ' '.join(args[1:])
    else:
        target = context.nick

    return "moonwalks over {}'s face".format(target), Action


@match(r'\*(.+? )(pets|hugs|cuddles|snuggles) desubot')
def purr_match(bot, context, message, match):
    responses = [
        'purrs', 'snuggles up against ' + context.nick,
        'cuddles ' + context.nick, 'rubs up against ' + context.nick
    ]
    return choice(responses), Action


@match(r'\*(?:.+? )(kicks|pokes|hits|bites|pats) desubot')
def bite_match(bot, context, message, match):
    return 'bites ' + context.nick + (' back' if match.group(1) == 'bites' else ''), Action
