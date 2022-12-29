from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from graph_compiler.lexer import Lexer
    
from graph_compiler.lexer import Token, TokenType


class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.lookahead: Token = self.lexer.next_token()

    def parse(self) -> None:
        while self.lookahead.token_type != TokenType.EOF:
            pass

    def consume(self) -> None:
        self.lookahead = self.lexer.next_token()

    def error(self, string: str) -> None:
        raise SyntaxError(f"Expecting {string} found {self.lookahead} on line {self.lexer.line_num}")

    def match(self, token_type: TokenType) -> Token | None:
        if self.lookahead.token_type == token_type:
            old_token = self.lookahead
            self.consume()
            return old_token
        self.error(TokenType[token_type.name])


class AST:
    pass


class BinaryOp(AST):
    
    def __init__(self, left: AST, op: AST, right: AST) -> None:
        self.left = left
        self.op = op
        self.right = right


class Number(AST):
    
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.text


class Identifier(AST):
    
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.text


class TestParser(Parser):

    def parse(self) -> None:
        while self.lookahead.token_type != TokenType.EOF:
            current_token = self.lookahead
    
            match current_token.token_type:
                case TokenType.ID:
                    node = self.lookahead
                    if node == TokenType.EQUALS:
                        pass
                    elif node == TokenType.LBRACE:
                        pass 
