from motobot import command


@command('give')
def give_command(bot, context, message, args):
    target = args[1]
    message = ' '.join(args[2:])
    return "{}: {}".format(target, message)
