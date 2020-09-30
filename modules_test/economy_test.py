import unittest
import sqlite3
from modules.economy import Economy, parse_user_string


class EconomyTest(unittest.TestCase):

    def add_user(self, economy, user, initial_amount):
        """
        Helper function for adding users to database
        :param economy: Economy object to modify
        :param user: Name of user to add
        :param initial_amount: Amount user starts off with
        :return: Nothing, modifies database directly
        """
        conn = sqlite3.connect(economy.econ_db)
        c = conn.cursor()
        c.execute('''INSERT INTO balance VALUES (?, ?);''', (user, initial_amount))
        conn.commit()
        conn.close()

    def drop_table(self, economy):
        """
        Helper function that drops balance table from database
        :param economy: Economy object
        :return: None, modifies database directly
        """
        conn = sqlite3.connect(economy.econ_db)
        c = conn.cursor()
        c.execute('''DROP TABLE balance;''')
        conn.commit()
        conn.close()

    """
    Tests for get_balance()

    Partition on user: user in db, user not in db
    """
    def test_bal_user_in_db(self):
        # Covers user: user in db
        econ = Economy()
        self.add_user(econ, "test_user", 69)
        self.assertEqual(econ.get_balance("test_user"), 69)
        self.drop_table(econ)

    def test_bal_user_not_in_db(self):
        # Covers user: user not in db
        econ = Economy()
        self.assertEqual(econ.get_balance("test_user"), 0)

    """
    Tests for transfer()
    
    Partition on from_user: user in db, user not in db
    Partition on to_user: user in db, user not in db
    """
    def test_tx_neither_in_db(self):
        # Covers from_user: user not in db, to_user: user not in db
        econ = Economy()
        self.assertFalse(econ.transfer("user1", "user2", 69))  # since user1 doesn't exist, nothing to transfer

    def test_tx_from_not_in_db(self):
        # Covers from_user: user not in db, to_user: user in db
        econ = Economy()
        self.add_user(econ, "user2", 69)
        self.assertFalse(econ.transfer("user1", "user2", 69))  # since user1 doesn't exist, nothing to transfer
        self.drop_table(econ)

    def test_tx_to_not_in_db(self):
        # Covers from_user: user in db, to_user: user not in db
        econ = Economy()
        self.add_user(econ, "user1", 69)
        self.assertTrue(econ.transfer("user1", "user2", 69))  # adds user2 to db
        self.assertEqual(econ.get_balance("user1"), 0)
        self.assertEqual(econ.get_balance("user2"), 69)
        self.drop_table(econ)

    def test_tx_both_in_db(self):
        # Covers from_user: user in db, to_user: user in db
        econ = Economy()
        self.add_user(econ, "user1", 69)
        self.add_user(econ, "user2", 69)
        self.assertTrue(econ.transfer("user1", "user2", 69))
        self.assertEqual(econ.get_balance("user1"), 0)
        self.assertEqual(econ.get_balance("user2"), 138)
        self.drop_table(econ)

    """
    Tests for deposit
    
    Partition on user: user in db, user not in db
    """
    def test_deposit_user_in_db(self):
        # Covers user: user in db
        econ = Economy()
        self.add_user(econ, "test_user", 69)
        econ.deposit("test_user", 351)
        self.assertEqual(econ.get_balance("test_user"), 420)
        self.drop_table(econ)

    def test_deposit_user_not_in_db(self):
        # Covers user: user not in db
        econ = Economy()
        econ.deposit("test_user", 420)
        self.assertEqual(econ.get_balance("test_user"), 420)
        self.drop_table(econ)

    """
    Test for deposit_all
    """
    def test_deposit_all(self):
        econ = Economy()
        self.add_user(econ, "user1", 69)
        users = {'user1', 'user2'}
        econ.deposit_all(users, 69)
        self.assertEqual(econ.get_balance("user1"), 138)
        self.assertEqual(econ.get_balance("user2"), 69)
        self.drop_table(econ)


if __name__ == '__main__':
    unittest.main()
