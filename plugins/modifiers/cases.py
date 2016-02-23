from motobot import command


@command('shout')
@command('upper')
def shout_command(bot, context, message, args):
    """ Shout something! """
    return ' '.join(args[1:]).upper()


@command('lower')
def lower_command(bot, context, message, args):
    return ' '.join(args[1:]).lower()


@command('swapcase')
def swapcase_command(bot, context, message, args):
    return ' '.join(args[1:]).swapcase()


@command('coolcase')
@command('alernatingcase')
def alternatingcase_command(bot, context, message, args):
    return alternatingcase(' '.join(args[1:]))


def alternatingcase(string):
    output = ''
    step = True
    for c in string:
        if c.isalpha():
            c = c.upper() if step else c.lower()
            step = not step
        output += c
    return output
