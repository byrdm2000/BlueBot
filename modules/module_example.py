

# You can import anything that your module may need at the top, just like a regular Python script

HANDLED_COMMANDS = {"ping", "pong"}  # Add commands that your module can handle here, without prefix


class Output(object):
    # Output class is used for communicating between the module and the main process. REQUIRED.
    def __init__(self):
        """
        Initializes a Output object for passing module output to main process
        """
        self.out = ''
        self.updated = False

    def read(self):
        """
        Reads from output
        :return: String, representing output from module
        """
        self.updated = False
        return self.out

    def write(self, o):
        """
        Writes to Output object
        :param o: Object, as long as it has a string representation
        :return: None
        """
        self.updated = True
        self.out = str(o)

    def is_updated(self):
        """
        Checks if new text has been written to output
        :return: True if output has updated since last read, False if not
        """
        return self.updated


out = Output()  # Make Output object for communicating with main. REQUIRED. Use out.write(o) as if sending a msg to chat

# You can add additional classes your module may need here


# Command handler function allows commands to be handled from main python file. REQUIRED.
def command_handler(command):
    if command.get_command() == "ping":
        out.write("Pong!")
    if command.get_command() == "pong":
        out.write("Ping!")


# You can add additional functions your module may need here.

# Put any initialization code here
pass
