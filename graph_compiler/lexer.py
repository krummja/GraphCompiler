from __future__ import annotations
from beartype.typing import Hashable, cast

from enum import Enum, auto


class TokenType(Enum):
    EOF = auto()
    QUOTE = auto()
    SEMICOLON = auto()
    EXCLAMATION = auto() 
    DOLLAR = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto() 
    PERIOD = auto()
    COLON = auto()
    EQUALS = auto()
    AT = auto()
    PIPE = auto()
    POSITIVE = auto()
    NEGATIVE = auto()
    MUL = auto()
    DIV = auto()
    NUMBER = auto()
    ID = auto()


class Token:

    def __init__(self, token_type: TokenType, text: str) -> None:
        self.token_type = token_type
        self.text = text

    def __str__(self) -> str:
        return f"{self.text}, {TokenType(self.token_type).name}"

    def __hash__(self) -> Hashable:
        return hash((self.token_type, self.text))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Token):
            return (
                self.token_type == other.token_type and
                self.text == other.text
            )
        return False


class Lexer:

    def __init__(self, input_stream: str) -> None:
        self.input_stream = input_stream
        self.idx: int = 0
        self.line_num: int = 1
        self.char_num: int = 1

        if len(input_stream) != 0:
            self.char: str | TokenType = self.input_stream[self.idx]
        else:
            self.char: str | TokenType = TokenType.EOF

    def next_token(self) -> Token:        
        while self.char != TokenType.EOF:

            match self.char:

                # IGNORED
                case ' ' | '\t':        # WhiteSpace
                    self.consume()
                case '\n' | '\r':       # LineTerminator
                    self.consume()
                case ',':               # Comma
                    self.consume()
                case '#':               # Comment
                    self.consume()

                # LEXICAL TOKENS
                case '\'' | '\"' as quote:
                    self.consume()
                    return Token(TokenType.QUOTE, quote)
                case ';' as semicolon:
                    self.consume()
                    return Token(TokenType.SEMICOLON, semicolon)
                case '!' as exclamation:
                    self.consume()
                    return Token(TokenType.EXCLAMATION, exclamation)
                case '$' as dollar:
                    self.consume()
                    return Token(TokenType.DOLLAR, dollar)
                case '(' as lparen:
                    self.consume()
                    return Token(TokenType.LPAREN, lparen)
                case ')' as rparen:
                    self.consume()
                    return Token(TokenType.RPAREN, rparen)
                case '[' as lbracket:
                    self.consume()
                    return Token(TokenType.LBRACKET, lbracket)
                case ']' as rbracket:
                    self.consume()
                    return Token(TokenType.RBRACKET, rbracket)
                case '{' as lbrace:
                    self.consume()
                    return Token(TokenType.LBRACE, lbrace)
                case '}' as rbrace:
                    self.consume()
                    return Token(TokenType.RBRACE, rbrace)
                case '.' as period:
                    self.consume()
                    return Token(TokenType.PERIOD, period)
                case ':' as colon:
                    self.consume()
                    return Token(TokenType.COLON, colon)
                case '@' as at:
                    self.consume()
                    return Token(TokenType.AT, at)
                case '|' as pipe:
                    self.consume()
                    return Token(TokenType.PIPE, pipe)
                case '+' as positive:
                    self.consume()
                    return Token(TokenType.POSITIVE, positive)
                case '-' as negative:
                    self.consume()
                    return Token(TokenType.NEGATIVE, negative)
                case '*' as multiply:
                    self.consume()
                    return Token(TokenType.MUL, multiply)
                case '/' as divide:
                    self.consume()
                    return Token(TokenType.DIV, divide)

                # Complex
                case _:
                    if self.char.isdigit():
                        token = self.parse_digits()
                        return token
                    elif self.char.isalpha():
                        token = self.parse_alpha()
                        return token
                    else:
                        self.error()

        else:
            return Token(TokenType.EOF, '<EOF>')
    
    def parse_digits(self):
        lexeme = ""
        while self.char != TokenType.EOF and self.char.isdigit():
            lexeme += self.char
            self.consume()
        return Token(TokenType.NUMBER, lexeme)

    def parse_alpha(self):
        lexeme = ""
        while self.char != TokenType.EOF and self.char.isalpha():
            lexeme += self.char
            self.consume()
        return Token(TokenType.ID, lexeme)

    def consume(self) -> None:
        if self.char in ['\n', '\r']:
            self.line_num += 1
        
        if self.char in ['\t']:
            self.char_num += 4

        self.char_num += 1

        self.idx += 1
        if self.idx >= len(self.input_stream):
            self.char = TokenType.EOF
        else:
            self.char = self.input_stream[self.idx]

    def error(self) -> None:
        msg = f"Invalid character {self.char} at [{self.line_num}:{self.char_num}]"
        raise SyntaxError(msg)
