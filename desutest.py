from motobot import IRCBot, IRCLevel
import desutest as this
import threading
import traceback

def worker():
    this.bot.run()

def main():
    IRCBot.load_plugins('plugins')
    this.bot.join('#Moto-chan')
    
    thread = threading.Thread(target=worker)
    thread.start()

    running = True
    while running:
        try:
            msg = input()
            if msg.startswith(':'):
                IRCBot.load_plugins('plugins')
            else:
                this.bot.send(msg)
        except KeyboardInterrupt:
            running = False
            this.bot.disconnect()
        except:
            traceback.print_exc()

if __name__ == '__main__':
    main()

else:
    bot = IRCBot('desutest', 'irc.rizon.net', command_prefix='!')
