from motobot import IRCBot, IRCLevel

"""
@IRCBot.match(r'(?:youtube\..*?\?.*?v=|youtu\.be/)([-_a-zA-Z0-9]+)', IRCLevel.op)
def youtube_match(message):
    title = 'test'
    duration = 'test'
    uploader = 'test'
    
    return "{}'s video: {}; Duration: {}; Uploader: {};".format(
        message.nick, title, duration, uploader
    )
"""