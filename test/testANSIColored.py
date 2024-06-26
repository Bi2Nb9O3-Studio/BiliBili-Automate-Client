import unittest
from prompt_toolkit.document import Document
from cli import ANSIColoredLexer


class TestANSIColoredLexer(unittest.TestCase):
    def test_initialization(self):
        lexer = ANSIColoredLexer()
        self.assertIsNotNone(lexer)

    def test_lexing_with_different_log_levels(self):
        document = Document(
            text="Normal line\n [SUCCESS] Success message\n [WARN] Warning message\n [WARNING] Another warning\n [ERROR] Error message")
        lexer = ANSIColoredLexer()
        get_line = lexer.lex_document(document)
        self.assertEqual(get_line(1), [("#ffffff", "Normal line")])
        self.assertEqual(
            get_line(2), [("#88ff88", " [SUCCESS] Success message")])
        self.assertEqual(get_line(3), [("#ffff88", " [WARN] Warning message")])
        self.assertEqual(
            get_line(4), [("#ffff88", " [WARNING] Another warning")])
        self.assertEqual(get_line(5), [("#ff8888", " [ERROR] Error message")])

    def test_lexing_with_no_lines(self):
        document = Document(text="")
        lexer = ANSIColoredLexer()
        get_line = lexer.lex_document(document)
        self.assertEqual(get_line(1), [])

    def test_lexing_with_invalid_line_number(self):
        document = Document(text="This is a test.")
        lexer = ANSIColoredLexer()
        get_line = lexer.lex_document(document)
        self.assertEqual(get_line(2), [])  # Invalid line number


if __name__ == '__main__':
    unittest.main()
