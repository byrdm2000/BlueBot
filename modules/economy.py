import sqlite3
import time
# You can import anything that your module may need at the top, just like a regular Python script

# Add commands that your module can handle here, without prefix
HANDLED_COMMANDS = {"pay", "balance", "deposit", "depositall"}


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
class Economy(object):
    """
    An economy made up of users and balances stored in database econ_db
    """
    def __init__(self):
        """
        Initializes DB if needed, and loads it
        """
        self.econ_db = "economy.db"
        conn = sqlite3.connect(self.econ_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS balance (user text, balance real)''')
        conn.commit()

    def get_balance(self, user):
        """
        Retrieves balance for user
        :param user: String, user to retrieve balance for
        :return: Integer, balance for user
        """

    def transfer(self, from_user, to_user, amount):
        """
        Transfers amount from user1's balance to user2's balance
        :param from_user: String, username of person to take amount from
        :param to_user: String, username of person to give amount to
        :param amount: Integer, amount of money to transfer
        :return: True if successful, False otherwise (e.g. low balance)
        """

    def deposit(self, user, amount):
        """
        Adds amount to a user's balance
        :param user: String, username to deposit to
        :param amount: Int, amount to add
        :return: None, modifies database directly
        """

    def depositall(self, users, amount):
        """
        Adds amount to every user's balance
        :param users: Set of strings representing users to deposit to
        :param amount: Int, amount to add
        :return: None, modifies database directly
        """


# Command handler function allows commands to be handled from main python file. REQUIRED.
def command_handler(command):
    pass


# You can add additional functions your module may need here.

def get_users():
    """
    Gets set of all users from output of /NAMES command
    :return: Set of strings, representing usernames of users present in chat
    """


def parse_user_string(names_string):
    """
    Parses string from output of /NAMES command
    :param names_string: String, output of /NAMES command, includes usernames of all users currently in chat
    :return: Set of strings, representing usernames of users present in chat
    """


# Put any initialization code here
# Reward info
small_deposit_period = 5*60
big_deposit_period = 60*60
small_deposit_amount = 10
big_deposit_amount = 50

# Use loop with timers to periodically depositall
