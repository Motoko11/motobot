from motobot.irc_bot import IRCBot, IRCLevel
import desubot
import threading

def worker():
    desubot.bot.run()

def main():
    desubot.bot.load_plugins('plugins')
    desubot.bot.join('#Moto-chan')
    
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
    bot = IRCBot('desutest', 'irc.rizon.net', command_prefix='!')
