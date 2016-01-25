from motobot import IRCBot, IRCLevel
from json import load
from threading import Thread
import traceback

def thread_func(bot):
    def worker():
        bot.run()
    return worker

def main():
    config_filename = 'desubot_config.json'
    config_file = open(config_filename, 'r')
    config = load(config_file)
    bot = IRCBot(config)

    bot.load_plugins('plugins')
    
    thread = Thread(target=thread_func(bot))
    thread.start()

    running = True
    while running:
        try:
            msg = input()
            if msg.startswith(':'):
                bot.reload_plugins()
            elif msg.startswith('?'):
                bot.load_database('desubot.json')
            else:
                bot.send(msg)
        except KeyboardInterrupt:
            running = False
            bot.disconnect()
        except:
            traceback.print_exc()

if __name__ == '__main__':
    main()
