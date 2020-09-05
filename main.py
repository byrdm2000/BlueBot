from config import Config
import minisongrequest

cmd_prefix = Config.COMMAND_PREFIX


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
    # if command.get_command() in minisongrequest.HANDLED_COMMANDS:
    #     minisongrequest.command_handler(command)

    if command.get_command() == "ping":
        print("Pong!")


if __name__ == "__main__":
    print("Welcome to BlueBot debug prompt")
    print(cmd_prefix + "exit to exit")
    while True:
        message = message_factory(input("> "))
        if message.get_command() == "exit":
            break
        elif message.get_command():
            command_handler(message)
