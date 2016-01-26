from motobot import command
from requests import get


def format_temp(temp):
    temp -= 273.15
    return '{:.0f}C ({:.1f}F)'.format(temp, temp * 1.8 + 32)


def format_windspeed(speed):
    speed *= 3.6
    return '{:.2f}kmph ({:.2f}mph)'.format(speed, speed * 0.621371)


def silly_response(arg):
    mapping = {
        'betholas': "betholas is HAWT HAWT HAWT!",
        'beth': "beth is HAWT HAWT HAWT!",
        'ss23': "ss23 is snuggly as always ;)",
        'anime-planet': "It's always a beautiful day in the world of anime!",
        'anime-planet.com': "It's always a beautiful day in the world of anime!",
        'aereon': "aereon being cold and callus as always! >:D",
        'aere0n': "aere0n being cold and callus as always! >:D",
        'chintzygore65': "ChintzyGore65 being cold and callus as always! >:D",
        'awkwardapples': "AwkwardApples is #anime-planet.com's prettiful pet! <3",
        'hell': "Hell is freezing over!",
        'animu': "The weather doesn't matter... We do not go outside.",
        'nubmer6': "It's always sunny in the Village.",
        'number6': "It's always sunny in the Village."
    }

    arg = arg.lstrip('#@!&').lower()
    if arg in mapping:
        return mapping[arg]


@command('w')
@command('weather')
def weather_command(bot, database, nick, channel, message, args):
    """ Get the weather for a given area. """
    response = silly_response(args[1])
    if response is not None:
        return nick + ': ' + response
    try:
        arguments = '%20'.join(args[1:])
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(
            arguments, '3706fd03388bce9f7340aa1999c3eb1e'
        )
        weather = get(url).json()

        response = "{}: Weather in {}, {}: {}; Temperature: {}; Pressure: {}mb; Humidity: {}%; Wind: {};".format(
            nick, weather['name'], weather['sys']['country'],
            weather['weather'][0]['description'],
            format_temp(weather['main']['temp']), weather['main']['pressure'],
            weather['main']['humidity'], format_windspeed(weather['wind']['speed'])
        )
    except KeyError:
        response = "Error: Unable to find specified location."
    except:
        response = "Fuck knows what went wrong. Probably connection issues."

    return response
