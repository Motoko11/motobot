from motobot import command
from requests import get


def get_weather(query):
    response = None

    api_key = 'd6581ca607738206'
    weather_url = 'https://api.wunderground.com/api/{}/conditions/bestfct:1/pws:0/q/{}.json'.format(
        api_key, query)
    weather = get(weather_url).json()

    if 'current_observation' in weather:
        weather = weather['current_observation']
        location = weather['display_location']['full']
        type = weather['weather']
        temp_c = weather['temp_c']
        temp_f = weather['temp_f']
        pressure = weather['pressure_mb']
        humidity = weather['relative_humidity']
        wind_kph = weather['wind_kph']
        wind_mph = weather['wind_mph']
        
        response = "Weather in {}: {}; Temperature: {}C ({}F); Pressure: {}mb; Humidity: {}; Wind: {}kph ({}mph);".format(
            location, type, temp_c, temp_f, pressure, humidity, wind_kph, wind_mph)

    elif 'results' in weather['response']:
        q = weather['response']['results'][0]['l'][3:]
        response = get_weather(q)

    else:
        response = "Error: Unable to find specified location."

    return response


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
        'bakalibre': "The weather doesn't matter... We do not go outside.",
        'nubmer6': "It's always sunny in the Village.",
        'number6': "It's always sunny in the Village.",
        'chalamius': "As cold as ChalamiuS' heart!",
        'manga_or_manha': "manga_or_manha is innocent as always!"
    }

    if arg in mapping:
        return mapping[arg.lower()]


@command('w')
@command('weather')
def weather_command(bot, context, message, args):
    """ Get the weather for a given area. """
    try:
        response = silly_response(args[1])
        if response is None:
            response = get_weather('%20'.join(args[1:]))
        response = "{}: {}".format(context.nick, response)
    except IndexError:
        response = "Error: You must supply a search term."
    return response
