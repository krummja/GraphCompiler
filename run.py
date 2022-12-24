from graph_compiler.parser import Parser
from graph_compiler.lexer import Lexer


if __name__ == '__main__':
    # parser = Parser(Lexer('abc { x: 10 }'))
    parser = Parser(Lexer('7 + ((10 * 2))'))
    result = parser.parse()
    print(result)
