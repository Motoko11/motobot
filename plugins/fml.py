from motobot import command
from requests import get


@command('fml')
def fml_command(message, database):
    return 'Provisional command for fml'
