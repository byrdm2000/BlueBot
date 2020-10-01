from config import Config
import requests
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
        conn.close()

    def get_balance(self, user):
        """
        Retrieves balance for user. Returns 0 if user not in database.
        :param user: String, user to retrieve balance for
        :return: Integer, balance for user
        """
        conn = sqlite3.connect(self.econ_db)
        c = conn.cursor()
        c.execute('''SELECT balance FROM balance WHERE user = ?''', (user,))
        result = c.fetchone()
        if result is not None:
            balance = result[0]
        else:
            balance = 0
        conn.commit()
        conn.close()
        return balance

    def transfer(self, from_user, to_user, amount):
        """
        Transfers amount from user1's balance to user2's balance
        :param from_user: String, username of person to take amount from
        :param to_user: String, username of person to give amount to
        :param amount: Integer, amount of money to transfer (must be positive)
        :return: True if successful, False otherwise (e.g. low balance)
        :raise: ValueError if amount is not positive
        """
        if amount < 1:
            raise ValueError
        conn = sqlite3.connect(self.econ_db)
        c = conn.cursor()

        # Get and update from_user balance
        c.execute('''SELECT balance FROM balance WHERE user = ?;''', (from_user,))
        result = c.fetchone()
        if result is not None:  # user in db
            new_balance = result[0] - amount
            c.execute('''UPDATE balance SET balance = ? WHERE user = ?;''', (new_balance, from_user))
            if new_balance < 0:
                return False
        else:  # user not in db
            return False

        # Get and update to_user balance
        c.execute('''SELECT balance FROM balance WHERE user = ?;''', (to_user,))
        result = c.fetchone()
        if result is not None:  # user in db
            new_balance = result[0] + amount
            c.execute('''UPDATE balance SET balance = ? WHERE user = ?;''', (new_balance, to_user))
        else:  # user not in db
            new_balance = amount
            c.execute('''INSERT INTO balance VALUES (?, ?);''', (to_user, new_balance))

        conn.commit()
        conn.close()
        return True

    def deposit(self, user, amount):
        """
        Adds amount to a user's balance
        :param user: String, username to deposit to
        :param amount: Int, amount to add (must be positive)
        :return: None, modifies database directly
        :raise: ValueError if amount is not positive
        """
        if amount < 1:
            raise ValueError
        conn = sqlite3.connect(self.econ_db)
        c = conn.cursor()

        # Get and update user balance
        c.execute('''SELECT balance FROM balance WHERE user = ?;''', (user,))
        result = c.fetchone()
        if result is not None:  # user in db
            new_balance = result[0] + amount
            c.execute('''UPDATE balance SET balance = ? WHERE user = ?;''', (new_balance, user))
        else:  # user not in db
            new_balance = amount
            c.execute('''INSERT INTO balance VALUES (?, ?);''', (user, new_balance))

        conn.commit()
        conn.close()

    def deposit_all(self, users, amount):
        """
        Adds amount to every user's balance
        :param users: Set of strings representing users to deposit to
        :param amount: Int, amount to add (must be positive)
        :return: None, modifies database directly
        :raise: ValueError if amount is not positive
        """
        if amount < 1:
            raise ValueError
        conn = sqlite3.connect(self.econ_db)
        c = conn.cursor()

        for user in users:
            c.execute('''SELECT balance FROM balance WHERE user = ?;''', (user,))
            result = c.fetchone()
            if result is not None:  # user in db
                new_balance = result[0] + amount
                c.execute('''UPDATE balance SET balance = ? WHERE user = ?;''', (new_balance, user))
            else:  # user not in db
                new_balance = amount
                c.execute('''INSERT INTO balance VALUES (?, ?);''', (user, new_balance))

        conn.commit()
        conn.close()


econ = Economy()


# Command handler function allows commands to be handled from main python file. REQUIRED.
def command_handler(command):
    econ_command = command.get_command()
    econ_args = command.get_args()
    sender_is_mod = command.is_sender_mod()

    if econ_command == "pay":
        if len(econ_args) == 2:
            payer = command.get_sender()
            payee = econ_args[0]
            amount = econ_args[1]
            if amount >= 1:
                econ.transfer(payer, payee, amount)
                out.write(payer + " sent " + str(amount) + " " + currency + " to " + payee)

    if econ_command == "balance":
        inquirer = command.get_sender()
        balance = econ.get_balance(inquirer)
        out.write(inquirer + "'s balance is " + str(balance) + " " + currency)

    if econ_command == "deposit" and sender_is_mod:
        if len(econ_args) == 2:
            payee = econ_args[0]
            amount = econ_args[1]
            if amount >= 1:
                econ.deposit(payee, amount)
                out.write(str(amount) + " " + currency + " has been paid to " + payee)

    if econ_command == "depositall" and sender_is_mod:
        if len(econ_args) == 1:
            amount = econ_args[0]
            if amount >= 1:
                users = get_users()
                econ.deposit_all(users, amount)
                out.write(str(amount) + " " + currency + " has been paid to " + str(len(users)) + " chatters.")


# You can add additional functions your module may need here.
def get_users():
    """
    Using a Twitch JSON endpoint, retrieve current viewers in stream
    :return: Set of strings, where each string is a viewer's username
    """
    r = requests.get("http://tmi.twitch.tv/group/user/" + Config.JOIN_CHANNEL + "/chatters")
    data = r.json()
    chatters = data.get("chatters")
    all_users = set()
    for rank, users in chatters.items():
        all_users.update(users)
    return all_users


def store_time(timer, value):
    """
    Stores time value in database
    :param timer: String, what to call timer
    :param value: Float, timer value
    :return: None, modifies database directly
    """
    conn = sqlite3.connect(econ.econ_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS timers (timer text, time_val real);''')

    c.execute('''SELECT time_val FROM timers WHERE timer = ?;''', (timer,))
    result = c.fetchone()
    if result is not None:  # timer in db
        c.execute('''UPDATE timers SET time_val = ? WHERE timer = ?;''', (value, timer))
    else:  # timer not in db
        c.execute('''INSERT INTO timers VALUES (?, ?);''', (timer, value))

    conn.commit()
    conn.close()


def get_time(timer):
    """
    Retrieves timer value in database
    :param timer: Name of timer
    :return: Value of timer if exists, or None otherwise
    """
    conn = sqlite3.connect(econ.econ_db)
    c = conn.cursor()

    c.execute('''SELECT time_val FROM timers WHERE timer = ?;''', (timer,))
    result = c.fetchone()
    if result is not None:  # timer in db
        value = result[0]
    else:  # timer not in db
        value = None

    conn.commit()
    conn.close()
    return value


# Put any initialization code here
currency = "berries"  # move to config once config manager is working

# Reward info
small_deposit_period = 5*60
big_deposit_period = 60*60
small_deposit_amount = 10
big_deposit_amount = 50

store_time("small", time.time())
store_time("big", time.time())


# Finally, anything that needs to be ran in a loop should be in the update() function. This can be empty. REQUIRED.
def update():
    if time.time() - get_time("big") > big_deposit_period:
        users = get_users()
        econ.deposit_all(users, big_deposit_amount)
        out.write("Everyone has received " + str(big_deposit_amount) + " " + currency + ". Thanks for your support!")
        store_time("big", time.time())
    elif time.time() - get_time("small") > small_deposit_period:
        users = get_users()
        econ.deposit_all(users, small_deposit_amount)
        store_time("small", time.time())
