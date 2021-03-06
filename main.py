from config import Config
from secret import Secret
import modules
import modulefinder
import traceback
import socket
import time
import re


cmd_prefix = Config.COMMAND_PREFIX
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Message limits, from https://dev.twitch.tv/docs/irc/guide#command--message-limits
NON_MOD_RATE_LIMIT = 20/30
MOD_RATE_LIMIT = 100/30

finder = modulefinder.ModuleFinder(["modules"])
AVAIL_MODULES = finder.find_all_submodules(modules)

chat_mods = set()
MOD_UPDATE_TIMEOUT = 40  # time between getting mod list from server


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
    time.sleep(1)
    irc.send(join_string.encode())
    server_text = irc.recv(2040)
    if server_text.find("End of /NAMES list".encode()):
        print("Join successful")
    cap_string = "CAP REQ :twitch.tv/commands\r\n"
    irc.send(cap_string.encode())
    test_string = "PRIVMSG #" + Config.JOIN_CHANNEL + " :Bot connected!\r\n"
    irc.send(test_string.encode())
    return True


def get_mods():
    """
    Retrieves list of moderators and ops for channel using the COMMANDS capability
    :return: Set of strings, where each item is a username of a moderator or operator of the channel
    """
    send_string = "PRIVMSG #" + Config.JOIN_CHANNEL + " :/mods\r\n"
    irc.send(send_string.encode())
    mods_string = irc.recv(2040)
    mods_set = parse_mods_list(mods_string)
    mods_set.add(Config.JOIN_CHANNEL)
    return mods_set


def parse_mods_list(mods_string):
    """
    Helper function for parsing list of moderators from string returned by /mods command
    :param mods_string: Encoded string returned by /mods command
    :return: Set of strings, where each item is a username of a moderator of the channel
    """
    decoded = mods_string.decode()
    split_string = decoded.split(": ")
    if len(split_string) == 1:  # list of users not in string, so there are no mods
        return set()
    else:
        user_string = split_string[-1].rstrip()
        return {x for x in user_string.split(", ")}  # since users are separated by ", ", this makes set of them


def send(text):
    """
    Sends PRIVMSG message to server with specified text
    :param text: String, text to send
    :return: True if successful, Error if there was an error
    """
    if Config.DEBUG_MODE:
        print("[INFO]: " + text)
    send_string = "PRIVMSG #" + Config.JOIN_CHANNEL + " :" + text + "\r\n"
    irc.send(send_string.encode())
    return True


class ServerMessage(object):
    def __init__(self, response):
        """
        Initializes a ServerMessage object from bytes-like response with ping status, sender user, and content message
        If variant is a PING message, user and message are empty strings
        Response must be of the format 'PING :tmi.twitch.tv', ':<username>!<username>@<username>...:<content>', or ''
        """
        decoded_text = response.decode()
        split_response = decoded_text.split(" :")
        if split_response[0] == "PING":  # is PING variant
            self.ping = True
            self.sender = ""
            self.content = ""
        elif split_response[0].find("PRIVMSG") != -1:  # is chat message variant
            self.ping = False
            # matches characters between : and ! in string, exclusive
            match = re.search('(?<=:).*(?=!)', split_response[0])
            self.sender = match.group(0)
            self.content = split_response[1].rstrip()  # since messages include '\r\n' at end
        elif split_response[0] == '':  # is blank string
            self.ping = False
            self.sender = ""
            self.content = ""

    def is_ping(self):
        """
        Determines if server response is a ping.
        :return: True if ping message, False if server message
        """
        return self.ping

    def get_sender(self):
        """
        Determines sender of server message.
        :return: String of sender's username if MSG, empty string if PING
        """
        return self.sender

    def get_content(self):
        """
        Determines content of server message.
        :return: String of message content if MSG, empty string if PING
        """
        return self.content


class Message(object):
    def __init__(self, text, sender):
        """
        Initializes a Message object with text text written by sender sender with mod status sender_mod
        :param text: String, contents of message
        :param sender: String, username of Twitch user who sent message
        """
        self.text = text
        self.sender = sender
        self.sender_mod = False
        if self.sender in chat_mods:
            self.sender_mod = True

    def get_text(self):
        return self.text

    def get_sender(self):
        return self.sender

    def get_command(self):
        return None

    def get_args(self):
        return []

    def is_sender_mod(self):
        return self.sender_mod


class Command(Message):
    def __init__(self, command, args, sender, prefix=cmd_prefix):
        """
        Initializes a Command object, where commands and args are separated by spaces
        :param command: String, command to use
        :param args: List of strings, arguments for command
        :param sender: String, username of Twitch user who sent message
        :param prefix: String representing command prefix, usually from config
        """
        self.prefix = prefix
        self.command = command
        self.args = args
        unstrip = prefix + command + " " + " ".join(args)
        Message.__init__(self, unstrip.rstrip(), sender)

    def get_command(self):
        return self.command

    def get_args(self):
        return self.args


def message_factory(input_text, sender, prefix=cmd_prefix):
    """
    Makes a Message or Command object from input text
    :param input_text: String, input text
    :param sender: String, username of Twitch user who sent message
    :param prefix: String, prefix to look for (usually from config)
    :return: Either a Message object or Command object, depending on if input starts with the command identifier
    """
    if input_text[:len(prefix):] == prefix:
        command = input_text.split(" ")[0][len(prefix):]  # since command prefix is at start
        args = input_text.split(" ")[1:]
        return Command(command, args, sender, prefix)
    else:
        return Message(input_text, sender)


def command_handler(command):
    """
    Handles Command objects and runs corresponding commands from them
    :param command: Command object
    :return: None
    """
    if command.get_command() == "modules":
        module_string = "Loaded modules: "
        for module in AVAIL_MODULES:
            module_string += module + " "
        send(module_string.rstrip())

    for m in AVAIL_MODULES:
        # Get command_handler function from each module
        mod = __import__("modules." + m, fromlist=["command_handler, HANDLED_COMMANDS", "out"])
        command_func = getattr(mod, "command_handler")
        avail_commands = getattr(mod, "HANDLED_COMMANDS")
        out_func = getattr(mod, "out")
        if command.get_command() in avail_commands:
            try:
                command_func(command)
                send(out_func.read())
            except Exception as err:
                print("[ERROR] An error occured in module", m)
                traceback.print_tb(err.__traceback__)
                # possibly remove module after error command


if __name__ == "__main__":
    print("Welcome to BlueBot")
    print("Debug mode:", Config.DEBUG_MODE)
    print(cmd_prefix + "exit to exit")
    if connect() is True and join() is True:
        print("Ready!")

    chat_mods = get_mods()
    msg_timer = time.time_ns()
    mod_timer = time.time_ns()
    SECOND_TO_NS_CONV = 10**9
    rate_limit = (MOD_RATE_LIMIT if Secret.bot_username in chat_mods else NON_MOD_RATE_LIMIT) * SECOND_TO_NS_CONV
    mod_update_limit = MOD_UPDATE_TIMEOUT * SECOND_TO_NS_CONV

    while True:
        recv_text = irc.recv(2040)
        if Config.DEBUG_MODE:
            print(recv_text)
        server_response = ServerMessage(recv_text)

        # Check module output, and update
        for m in AVAIL_MODULES:
            mod = __import__("modules." + m, fromlist=["out", "update"])
            out_func = getattr(mod, "out")
            update_func = getattr(mod, "update")
            update_func()
            if out_func.is_updated():
                send(out_func.read())

        # Update mod list
        if time.time_ns() - mod_timer > mod_update_limit:
            chat_mods = get_mods()
            rate_limit = (
                        MOD_RATE_LIMIT if Secret.bot_username in chat_mods else NON_MOD_RATE_LIMIT) * SECOND_TO_NS_CONV
            mod_timer = time.time_ns()
            if Config.DEBUG_MODE:
                print("[DEBUG] Mods:", chat_mods)

        # To obey Twitch send rate limit, we reset timer on send
        if time.time_ns() - msg_timer > rate_limit:
            if server_response.is_ping():
                irc.send("PONG :tmi.twitch.tv\r\n".encode())
                msg_timer = time.time_ns()
            else:
                message = message_factory(server_response.get_content(), server_response.get_sender())
                if message.get_command() == "exit":
                    irc.close()
                    break
                elif message.get_command():
                    command_handler(message)
                    msg_timer = time.time_ns()
