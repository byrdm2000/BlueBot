import unittest
from modules.module_example import Output


class OutputTest(unittest.TestCase):
    """
    Testing strategy:

    read(): self.updated = True, self.updated = False
    write(): self.updated = True, self.updated = False
    is_updated(): self.updated = True, self.updated = False
    """

    def test_read_updated(self):
        # Covers read(): self.updated = True
        test_out = Output()
        test_out.write('test')
        self.assertEqual(test_out.read(), 'test')
        self.assertFalse(test_out.is_updated())

    def test_read_not_updated(self):
        # Covers read(): self.updated = False
        test_out = Output()
        test_out.write('test')
        test_out.read()
        self.assertEqual(test_out.read(), 'test')
        self.assertFalse(test_out.is_updated())

    def test_write_updated(self):
        # Covers write(): self.updated = True
        test_out = Output()
        test_out.write('foo')
        test_out.write('test')
        self.assertTrue(test_out.is_updated())
        self.assertEqual(test_out.read(), 'test')

    def test_write_not_updated(self):
        # Covers write(): self.updated = False
        test_out = Output()
        test_out.write('test')
        self.assertTrue(test_out.is_updated())
        self.assertEqual(test_out.read(), 'test')

    def test_is_updated_updated(self):
        # Covers is_updated(): self.updated = True
        test_out = Output()
        test_out.write('test')
        self.assertTrue(test_out.is_updated())

    def test_is_updated_not_updated(self):
        # Covers is_updated(): self.updated = False
        test_out = Output()
        test_out.write('test')
        test_out.read()
        self.assertFalse(test_out.is_updated())


if __name__ == '__main__':
    unittest.main()
