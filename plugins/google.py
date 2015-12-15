from motobot import command
from requests import get

#api_key = 'AIzaSyCPGvdjsEjdo0uGBzdeukiChqDVx7SY_og'

def google_search(term):
    url = 'https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=' + term
    params = {
        'Referer': 'https://github.com/Motoko11/desubot',
        'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
    }
    results = get(url, params=params).json()
    result = results['responseData']['results'][0]
    url = result['url']
    title = result['titleNoFormatting']
    return title, url


#@command('g')
#@command('google')
def google_command(message, database):
    args = message.message.split(' ')

    if len(args) <= 1:
        return "No search term specified."
    else:
        title, url = google_search(' '.join(args[1:]))
        return "Search result: {} ({})".format(title, url)


@command('calc')
def calc_command(message, database):
    return "Does not compute!"
