from setuptools import setup
from motobot import __VERSION__


setup(
    name='motobot',
    version=__VERSION__,
    description='A plugin-able IRC Bot core.',
    long_description='',
    url='https://github.com/Motoko11/desubot',
    author='Motoko11',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    packages=['motobot', 'motobot.core_plugins'],
    keywords='irc bot ircbot plugin'
)
