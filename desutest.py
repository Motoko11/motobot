from motobot import IRCBot, IRCLevel
import threading
import traceback

def thread_func(bot):
    def worker():
        bot.run()
    return worker

def main():
    config = {
        'nick': 'desutest',
        'server': 'irc.rizon.net',
        'port': 6667,
        'command_prefix': '!',
        'masters': [
            "Moto-chan",
            "Motoko11",
            "MotoNyan",
            "Akahige",
            "betholas",
            "Baradium",
            "Cold_slither",
            "Drahken"
        ]
    }
    bot = IRCBot(config)

    bot.load_plugins('plugins')
    bot.load_database('desutest.json')
    bot.join('#MotoChan')

    thread = threading.Thread(target=thread_func(bot))
    thread.start()

    running = True
    while running:
        try:
            msg = input()
            if msg.startswith(':'):
                bot.reload_plugins()
            else:
                bot.send(msg)
        except KeyboardInterrupt:
            running = False
            bot.disconnect()
        except:
            traceback.print_exc()

if __name__ == '__main__':
    main()
