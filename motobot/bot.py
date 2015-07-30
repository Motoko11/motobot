import traceback
from socket import create_connection


class Bot:
    
    """ Class used to manage socket connection and event loop for bot. """
    
    def __init__(self, server, port, message_ending=None, buffer_size=1024):
        """ Create a new bot instance. """
        self.server = server
        self.port = port
        self.socket = None
        self.message_ending = message_ending
        self.buffer_size = buffer_size

        self.msg_hooks = []

        self.running = False
        self.connected = False
        self.read_buffer = ''

    def run(self):
        """ Run the bot.

        Will print traceback for any exceptions which occur,
        or exit on keyboard interrupt.

        """
        self.running = True
        self.init()

        while self.running:
            self.connect()

            while self.connected:
                try:
                    msgs = self.recv()
                    for msg in msgs:
                        self.handle_msg(msg)

                except KeyboardInterrupt:
                    self.disconnect()
                except:
                    traceback.print_exc()
        self.destroy()

    def __connect(self):
        """ Connect the socket. """
        self.socket = create_connection((self.server, self.port))
        self.connected = True

    def __disconnect(self):
        """ Disconnect and stop running the bot. """
        self.connected = self.running = False

    def send(self, msg):
        """ Send a message to the socket, appending an ending if necessary. """
        if msg is not None:
            self.socket.send(bytes(msg + self.message_ending, 'UTF-8'))
            print("Sent: {}".format(msg))

    def __recv(self):
        """ Receive messages from socket, splitting by message ending. """
        self.read_buffer += self.socket.recv(self.buffer_size).decode('UTF-8')

        if self.message_ending is not None:
            msgs = self.read_buffer.split(self.message_ending)
            self.read_buffer = msgs.pop()
        else:
            msgs = [read_buffer]
            self.read_buffer = msgs.pop()

        return msgs

    def __handle_msg(self, msg):
        """ Handle a message by forwarding it to hooked functions. """
        for hook in self.msg_hooks:
            response = hook(self, msg)
            self.send(response)

    def msg_hook(self, f):
        """ Hook a function to be used by handle_msg. """
        self.msg_hooks.append(f)

    def init(self):
        """ Function to be called when bot starts running. """
        pass

    def destroy(self):
        """ Function to be called when bot stops running. """
        pass
