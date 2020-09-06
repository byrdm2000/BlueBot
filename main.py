from config import Config
from secret import Secret
import minisongrequest
import socket
import time

cmd_prefix = Config.COMMAND_PREFIX
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# TODO: make better helper functions
def connect():
    """
    Establishes connection with Twitch's IRC server
    :return: True if successful, False if there was an error
    """
    irc.connect((Config.SERVER_ADDRESS, Config.SERVER_PORT))
    password_string = "PASS " + Secret.bot_oauth + "\n"
    irc.send(password_string.encode())
    nick_string = "NICK " + Secret.bot_username + "\n"
    irc.send(nick_string.encode())
    time.sleep(1)
    server_text = irc.recv(2040)
    if server_text.find("Welcome, GLHF!".encode()):
        return True
    return False


def join():
    """
    Joins room specified in config
    :return: True if successful, Error if there was an error
    """
    join_string = "JOIN #" + Config.JOIN_CHANNEL + "\n"
    irc.send(join_string.encode())
    server_text = irc.recv(2040)
    if server_text.find("End of /NAMES list".encode()):
        print("Join successful")
    test_string = "PRIVMSG #" + Config.JOIN_CHANNEL + " :Bot connected! \n"
    irc.send(test_string.encode())
    return True


class Message(object):
    def __init__(self, text):
        """
        Initializes a Message object with text text
        :param text: String, contents of message
        """
        self.text = text

    def get_text(self):
        return self.text

    def get_command(self):
        return None

    def get_args(self):
        return []


class Command(Message):
    def __init__(self, command, args, prefix=cmd_prefix):
        """
        Initializes a Command object, where commands and args are separated by spaces
        :param command: String, command to use
        :param args: List of strings, arguments for command
        :param prefix: String representing command prefix, usually from config
        """
        self.prefix = prefix
        self.command = command
        self.args = args
        unstrip = prefix + command + " " + " ".join(args)
        Message.__init__(self, unstrip.rstrip())

    def get_command(self):
        return self.command

    def get_args(self):
        return self.args


def message_factory(input_text, prefix=cmd_prefix):
    """
    Makes a Message or Command object from input text
    :param input_text: String, input text
    :param prefix: String, prefix to look for (usually from config)
    :return: Either a Message object or Command object, depending on if input starts with the command identifier
    """
    if input_text[:len(prefix):] == prefix:
        command = input_text.split(" ")[0][len(prefix):]  # since command prefix is at start
        args = input_text.split(" ")[1:]
        return Command(command, args, prefix)
    else:
        return Message(input_text)


def command_handler(command):
    """
    Handles Command objects and runs corresponding commands from them
    :param command: Command object
    :return: None
    """
    if command.get_command() in minisongrequest.HANDLED_COMMANDS:
        minisongrequest.command_handler(command)

    if command.get_command() == "ping":
        print("Pong!")


if __name__ == "__main__":
    print("Welcome to BlueBot debug prompt")
    print(cmd_prefix + "exit to exit")
    if connect() is True:
        print("Connected to server!")
    if join() is True:
        print("Ready!")
    recv_timer = time.time()
    server_text = "".encode()
    print("Debug mode:", Config.DEBUG_MODE)
    while True:
        # Non-blocking way to receive messages from server
        if time.time() - recv_timer > 1.5:
            recv_text = irc.recv(2040)
            if recv_text != b'':
                server_text = recv_text

        if server_text.find("PING :tmi.twitch.tv".encode()):
            irc.send("PONG :tmi.twitch.tv".encode())

        #TODO: make adt that handles server messages

        server_message = server_text.decode().rstrip()
        print(server_message)
        print(server_message.split(" :"))
        message = server_message.split(" :")[-1]
        print(message)
        message = message_factory(message)
        # message = message_factory(input("> "))
        if message.get_command() == "exit":
            irc.close()
            break
        elif message.get_command():
            command_handler(message)
