from motobot import command
from requests import get
from bs4 import BeautifulSoup


fml_cache = []


def load_fml():
    url = 'http://www.fmylife.com/random'
    bs = BeautifulSoup(get(url).text)

    for div in bs.find_all('div', {'class', 'article'}, recursive=True):
        fml_cache.append(div.find('p').text)


def get_fml():
    if len(fml_cache) == 0:
        load_fml()
    return fml_cache.pop(0)


@command('fml')
def fml_command(bot, database, context, message, args):
    """ You mean I have to return FMLs when asked? FML. """
    return get_fml()
