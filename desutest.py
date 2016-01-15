from motobot import IRCBot, IRCLevel
import desutest as this
import threading
import traceback

def worker():
    this.bot.run()

def main():
    this.bot.load_plugins('plugins')
    this.bot.load_database('desutest.json')
    this.bot.join('#MotoChan')
    
    thread = threading.Thread(target=worker)
    thread.start()

    running = True
    while running:
        try:
            msg = input()
            if msg.startswith(':'):
                this.bot.reload_plugins()
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
