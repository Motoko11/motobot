from motobot.irc_bot import IRCBot, IRCLevel
import desubot
import threading
import traceback

def worker():
    desubot.bot.run()

def main():
    desubot.bot.load_plugins('plugins')
    desubot.bot.join('#Moto-chan')
    desubot.bot.join('#animu')
    desubot.bot.join('#anime-planet.com')
    
    thread = threading.Thread(target=worker)
    thread.start()

    while True:
        try:
            msg = input()
            if msg.startswith(':'):
                desubot.bot.load_plugins('plugins')
            else:
                desubot.bot.send(msg)
        except:
            traceback.print_exc()

if __name__ == '__main__':
    main()

else:
    bot = IRCBot('desubot', 'irc.rizon.net', command_prefix='!')
