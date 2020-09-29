import unittest
from main import ServerMessage, Message, Command, message_factory, parse_mods_list


class ServerMessageTest(unittest.TestCase):
    """
    Partiton on response: PING message, chat message, empty message
    """
    def test_ping(self):
        # Covers response: PING message
        ping_text = b"PING :tmi.twitch.tv\r\n"
        message = ServerMessage(ping_text)
        self.assertEqual(True, message.is_ping())
        self.assertEqual("", message.get_sender())
        self.assertEqual("", message.get_content())

    def test_msg(self):
        # Covers response: chat message
        chat_text = b":testuser!testuser@testuser.tmi.twitch.tv PRIVMSG #testuser :test\r\n"
        message = ServerMessage(chat_text)
        self.assertEqual(False, message.is_ping())
        self.assertEqual("testuser", message.get_sender())
        self.assertEqual("test", message.get_content())

    def test_blank(self):
        # Covers response: empty message
        empty_text = b''
        message = ServerMessage(empty_text)
        self.assertEqual(False, message.is_ping())
        self.assertEqual("", message.get_sender())
        self.assertEqual("", message.get_content())


class MessageTest(unittest.TestCase):
    """
    Partition on text: empty string, not empty string
    """
    def test_empty(self):
        # Covers text: empty string
        message = Message("", "testuser")
        self.assertEqual("", message.get_text())
        self.assertEqual("testuser", message.get_sender())
        self.assertEqual(None, message.get_command())
        self.assertEqual([], message.get_args())

    def test_not_empty(self):
        # Covers text: not empty string
        message = Message("test", "testuser")
        self.assertEqual("test", message.get_text())
        self.assertEqual("testuser", message.get_sender())
        self.assertEqual(None, message.get_command())
        self.assertEqual([], message.get_args())


class CommandTest(unittest.TestCase):
    """
    Partition on command: empty string, not empty string
    Partition on args: len = 0, len > 0
    Partition on prefix: len = 0, len > 0
    """
    def test_empty_command_no_args_reg_prefix(self):
        # Covers command: empty string, args: len 0, prefix: len > 0
        cmd_prefix = "!"
        command = Command("", [], "testuser", cmd_prefix)
        self.assertEqual(cmd_prefix, command.get_text())
        self.assertEqual("", command.get_command())
        self.assertEqual([], command.get_args())

    def test_command_no_args_reg_prefix(self):
        # Covers command: not empty string and args: len 0, prefix: len > 0
        cmd_prefix = "!"
        command = Command("test", [], "testuser", cmd_prefix)
        self.assertEqual(cmd_prefix + "test", command.get_text())
        self.assertEqual("test", command.get_command())
        self.assertEqual([], command.get_args())

    def test_command_and_args_reg_prefix(self):
        # Covers command: not empty string and args: len >0, prefix: len > 0
        cmd_prefix = "!"
        command = Command("test", ['test'], "testuser", cmd_prefix)
        self.assertEqual(cmd_prefix + "test test", command.get_text())
        self.assertEqual("test", command.get_command())
        self.assertEqual(['test'], command.get_args())

    def test_command_and_args_empty_prefix(self):
        # Covers command: not empty string and args: len >0, prefix: len = 0
        cmd_prefix = ""
        command = Command("test", ['test'], "testuser", cmd_prefix)
        self.assertEqual(cmd_prefix + "test test", command.get_text())
        self.assertEqual("test", command.get_command())
        self.assertEqual(['test'], command.get_args())


class FactoryTest(unittest.TestCase):
    """
    Partition on prefix: len = 0, len = >0
    Partition on text: text starts with prefix, text doesn't start with prefix
    Partition on args: len(args) = 0, len(args) > 0
    """
    def test_empty_prefix(self):
        # Covers prefix len = 0, text starts with prefix, len(args) = 0
        cmd_prefix = ""
        text = "test test"
        user = "testuser"
        expected_command = "test"
        expected_args = ['test']
        factory_result = message_factory(text, user, cmd_prefix)
        self.assertIsInstance(factory_result, Command)
        self.assertEqual(factory_result.get_text(), text)
        self.assertEqual(factory_result.get_command(), expected_command)
        self.assertEqual(factory_result.get_args(), expected_args)

    def test_1char_identifier(self):
        # Covers prefix len >0, text starts with prefix, len(args) > 0
        cmd_prefix = "!"
        text = "!test test"
        user = "testuser"
        expected_command = "test"
        expected_args = ['test']
        factory_result = message_factory(text, user, cmd_prefix)
        self.assertIsInstance(factory_result, Command)
        self.assertEqual(factory_result.get_text(), text)
        self.assertEqual(factory_result.get_command(), expected_command)
        self.assertEqual(factory_result.get_args(), expected_args)

    def test_2char_identifier_no_args(self):
        # Covers prefix len >0, text starts with prefix, len(args) = 0
        cmd_prefix = "!!"
        text = "!!test"
        user = "testuser"
        expected_command = "test"
        expected_args = []
        factory_result = message_factory(text, user, cmd_prefix)
        self.assertIsInstance(factory_result, Command)
        self.assertEqual(factory_result.get_text(), text)
        self.assertEqual(factory_result.get_command(), expected_command)
        self.assertEqual(factory_result.get_args(), expected_args)

    def test_plain_message(self):
        # Covers prefix len >0, text does not start with prefix, len(args) = 0
        cmd_prefix = "!!"
        text = "test"
        user = "testuser"
        expected_command = None
        expected_args = []
        factory_result = message_factory(text, user, cmd_prefix)
        self.assertIsInstance(factory_result, Message)
        self.assertEqual(factory_result.get_text(), text)
        self.assertEqual(factory_result.get_command(), expected_command)
        self.assertEqual(factory_result.get_args(), expected_args)


class ParseModStringTest(unittest.TestCase):
    """
    Partition on number of mods: # mods = 0, # mods > 0
    """

    def test_no_mods(self):
        # Covers # mods = 0
        mod_string = b':tmi.twitch.tv NOTICE #test :There are no moderators of this channel.\r\n'
        mods_set = parse_mods_list(mod_string)
        self.assertEqual(mods_set, set())

    def test_some_mods(self):
        # Covers # mods > 0
        mod_string = b':tmi.twitch.tv NOTICE #test :The moderators of this channel are: test\r\n'
        mods_set = parse_mods_list(mod_string)
        self.assertEqual(mods_set, {'test'})


if __name__ == '__main__':
    unittest.main()
