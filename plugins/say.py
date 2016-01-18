from motobot import command, action


@command('say')
def say_command(bot, message, database):
    masters = [
        "Moto-chan",
        "Motoko11",
        "Akahige",
        "betholas",
        "Baradium",
        "Cold_slither",
        "Drahken"
    ]
    
    if message.nick.lower() not in [x.lower() for x in masters]:
        return "Check your privilege!"
    else:
        args = message.message.split(' ')[1:]

        if len(args) < 2:
            return "You must specify both a channel and a message"
        else:
            channel = args[0]
            message = ' '.join(args[1:])
            if message.startswith('/me '):
                message = action(message[4:])
            bot.send('PRIVMSG {} :{}'.format(channel, message))
