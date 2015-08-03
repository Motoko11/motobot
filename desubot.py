from motobot.irc_bot import IRCBot, IRCLevel
import desubot
import threading

def worker():
    desubot.bot.run()

def main():
    desubot.bot.load_plugins('plugins')
    desubot.bot.ignore('*!*@will.shenan.again')
    desubot.bot.join('#Moto-chan')
    desubot.bot.join('#animu')
    desubot.bot.join('#anime-planet.com')
    
    thread = threading.Thread(target=worker)
    thread.start()

    while True:
        msg = input()
        if msg.startswith(':'):
            desubot.bot.load_plugins('plugins')
        else:
            desubot.bot.send(msg)

if __name__ == '__main__':
    main()

else:
    bot = IRCBot('desubot', 'irc.rizon.net')
