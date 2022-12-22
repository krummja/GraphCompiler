from __future__ import annotations
from beartype.typing import Hashable, cast

from enum import Enum, auto


class TokenType(Enum):
    EOF = auto()
    SEMICOLON = auto()
    QUOTE = auto()
    

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
                case ' ' | '\t' | '\n' | '\r':
                    self.consume()
                case ',':
                    self.consume()
                case '#':
                    self.consume()
                case '\'' | '\"' as quote:
                    self.consume()
                    return Token(TokenType.QUOTE, quote)
                case ';' as semicolon:
                    self.consume()
                    return Token(TokenType.SEMICOLON, semicolon)
                case _:
                    self.error()

        else:
            return Token(TokenType.EOF, '<EOF>')
    
    def consume(self) -> None:
        if self.char in ['\n', '\r']:
            self.line_num += 1

        self.char_num += 1

        self.idx += 1
        if self.idx >= len(self.input_stream):
            self.char = TokenType.EOF
        else:
            self.char = self.input_stream[self.idx]

    def error(self) -> None:
        msg = f"Invalid character {self.char} at [{self.line_num}:{self.char_num}]"
        raise SyntaxError(msg)
