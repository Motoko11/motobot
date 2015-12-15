from motobot import match
from requests import get
from re import compile


pattern_string = r'((youtube\.com\/watch\?\S*v=)|(youtu\.be/))([a-zA-Z0-9-_]+)'
pattern = compile(pattern_string)


def format_duration(duration):
    x = i = h = m = s = 0

    for c in duration:
        if c.isdigit():
            x = x * 10 + int(c)
            i += 1
        elif c == 'H':
            h = x
            i = x = 0
        elif c == 'M':
            m = x
            i = x = 0
        elif c == 'S':
            s = x
            i = x = 0

    time = '' if h == 0 else '{}:'.format(h)
    return time + "{:02d}:{:02d}".format(m, s)


@match(pattern_string)
def youtube_match(message, database):
    invalid_channels = ['#animu', '#bakalibre']
    if message.channel in invalid_channels:
        return None
    match = pattern.search(message.message)
    vid = match.group(4)
    params = {
        'id': vid,
        'part': 'contentDetails,snippet',
        'key': 'AIzaSyAehOw6OjS2ofPSSo9AerCGuBzStsX5tks'
    }
    response = get('https://www.googleapis.com/youtube/v3/videos', params=params)
    if response.status_code == 400:
        return "{}: invalid id".format(message.nick)
    video = response.json()['items'][0]
    title = video['snippet']['title']
    duration = format_duration(video['contentDetails']['duration'])
    channel = video['snippet']['channelTitle']
    return "{}'s video: {} - {}".format(
        message.nick, title, duration
    )
