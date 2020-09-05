import unittest
from main import Message, Command, message_factory


class MessageTest(unittest.TestCase):
    """
    Partition on text: empty string, not empty string
    """
    def test_empty(self):
        # Covers text: empty string
        message = Message("")
        self.assertEqual("", message.get_text())
        self.assertEqual(None, message.get_command())
        self.assertEqual([], message.get_args())

    def test_not_empty(self):
        # Covers text: not empty string
        message = Message("test")
        self.assertEqual("test", message.get_text())
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
        command = Command("", [], cmd_prefix)
        self.assertEqual(cmd_prefix, command.get_text())
        self.assertEqual("", command.get_command())
        self.assertEqual([], command.get_args())

    def test_command_no_args_reg_prefix(self):
        # Covers command: not empty string and args: len 0, prefix: len > 0
        cmd_prefix = "!"
        command = Command("test", [], cmd_prefix)
        self.assertEqual(cmd_prefix + "test", command.get_text())
        self.assertEqual("test", command.get_command())
        self.assertEqual([], command.get_args())

    def test_command_and_args_reg_prefix(self):
        # Covers command: not empty string and args: len >0, prefix: len > 0
        cmd_prefix = "!"
        command = Command("test", ['test'], cmd_prefix)
        self.assertEqual(cmd_prefix + "test test", command.get_text())
        self.assertEqual("test", command.get_command())
        self.assertEqual(['test'], command.get_args())

    def test_command_and_args_empty_prefix(self):
        # Covers command: not empty string and args: len >0, prefix: len = 0
        cmd_prefix = ""
        command = Command("test", ['test'], cmd_prefix)
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
        expected_command = "test"
        expected_args = ['test']
        factory_result = message_factory(text, cmd_prefix)
        self.assertEqual(factory_result.get_text(), text)
        self.assertEqual(factory_result.get_command(), expected_command)
        self.assertEqual(factory_result.get_args(), expected_args)

    def test_1char_identifier(self):
        # Covers prefix len >0, text starts with prefix, len(args) > 0
        cmd_prefix = "!"
        text = "!test test"
        expected_command = "test"
        expected_args = ['test']
        factory_result = message_factory(text, cmd_prefix)
        self.assertEqual(factory_result.get_text(), text)
        self.assertEqual(factory_result.get_command(), expected_command)
        self.assertEqual(factory_result.get_args(), expected_args)

    def test_2char_identifier_no_args(self):
        # Covers prefix len >0, text starts with prefix, len(args) = 0
        cmd_prefix = "!!"
        text = "!!test"
        expected_command = "test"
        expected_args = []
        factory_result = message_factory(text, cmd_prefix)
        self.assertEqual(factory_result.get_text(), text)
        self.assertEqual(factory_result.get_command(), expected_command)
        self.assertEqual(factory_result.get_args(), expected_args)

    def test_plain_message(self):
        # Covers prefix len >0, text does not start with prefix, len(args) = 0
        cmd_prefix = "!!"
        text = "test"
        expected_command = None
        expected_args = []
        factory_result = message_factory(text, cmd_prefix)
        self.assertEqual(factory_result.get_text(), text)
        self.assertEqual(factory_result.get_command(), expected_command)
        self.assertEqual(factory_result.get_args(), expected_args)


if __name__ == '__main__':
    unittest.main()
