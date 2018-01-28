import unittest

from parser import tokenize, parse_tokens


class ParserTest(unittest.TestCase):
    def test_tokenize(self):
        text = '''
        ()
        (+ 123 ;; some comment!
            ( * xyz 34))
        '''
        expected = '( ) ( + 123 ( * xyz 34 ) )'.split()
        self.assertEqual(expected, tokenize(text))

    def test_parse_tokens(self):
        tokens = '( ) ( + 123 ( * xyz 34.05E-7 ) )'.split()
        expected = [[], ['+', 123, ['*', 'xyz', 34.05E-7]]]
        self.assertEqual(expected, parse_tokens(tokens))


if __name__ == '__main__':
    unittest.main()
