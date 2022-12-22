from graph_compiler.lexer import *


def test_token_equivalence():
    EOF_1 = Token(TokenType.EOF, "EOF")
    EOF_2 = Token(TokenType.EOF, "EOF")
    EOF_3 = Token(TokenType.EOF, "eof")
    SC_1 = Token(TokenType.SEMICOLON, ";")

    assert EOF_1 == EOF_1
    assert EOF_1 == EOF_2
    assert EOF_1 != EOF_3

    assert SC_1 == SC_1
    assert EOF_1 != SC_1


def test_lex():
    lexer = Lexer(" ;     \n")

    # no return on whitespace
    l1 = lexer.next_token()  # returns on ';'
    l2 = lexer.next_token()  # returns on '<EOF>'

    print(l1)
    print(l2)

    assert l1.text == ';'
    assert l2.text == '<EOF>'

    lexer = Lexer(';;;;;')
    lexer.next_token()
