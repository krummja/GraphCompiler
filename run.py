from graph_compiler.parser import Parser, TestParser
from graph_compiler.lexer import Lexer


if __name__ == '__main__':
    lexer = Lexer('a + b { 100 x 1 };')

    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    value = lexer.next_token()
    print(value)
    
    parser = TestParser(Lexer('abc { a = 10 };'))
    ast = parser.parse()
