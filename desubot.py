from motobot import IRCBot, IRCLevel
from json import load


def main():
    config_filename = 'desubot_config.json'
    config = {}
    with open(config_filename, 'r') as config_file:
        config = load(config_file)
    bot = IRCBot(config)

    bot.load_plugins('plugins')
    bot.run()

if __name__ == '__main__':
    main()
