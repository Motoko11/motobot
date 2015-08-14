from motobot import IRCBot, IRCLevel
import desubot
import threading
import traceback

def worker():
    desubot.bot.run()

def main():
    desubot.bot.load_plugins('plugins')
    desubot.bot.join('#Moto-chan')
    
    thread = threading.Thread(target=worker)
    thread.start()

    running = True
    while running:
        try:
            msg = input()
            if msg.startswith(':'):
                desubot.bot.load_plugins('plugins')
            else:
                desubot.bot.send(msg)
        except KeyboardInterrupt:
            running = False
            desubot.bot.disconnect()
        except:
            traceback.print_exc()

if __name__ == '__main__':
    main()

else:
    bot = IRCBot('desutest', 'irc.rizon.net', command_prefix='!')
