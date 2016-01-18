from motobot import IRCBot, IRCLevel
from json import load
import threading
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
    bot.load_database('desubot.json')
    bot.join('#MotoChan')
    bot.join('#animu')
    bot.join('#anime-planet.com')
    bot.join('#bakalibre')
    bot.join('#ap-marathon')
    
    thread = threading.Thread(target=thread_func(bot))
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

