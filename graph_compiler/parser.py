from __future__ import annotations
from typing import *

import re

from graph_compiler.lexer import Lexer, Token, TokenType


class AST:
    pass


class BinaryOp(AST):
    
    def __init__(self, left: AST, op: AST, right: AST) -> None:
        self.left = left
        self.token = self.op = op
        self.right = right

    def __repr__(self) -> str:
        left = self.left.text if isinstance(self.left, Token) else self.left
        op = self.op.text if isinstance(self.op, Token) else self.op
        right = self.right.text if isinstance(self.right, Token) else self.right
        return f"<{left} <{op} {right}>>"


class Terminal(AST):

    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.text

    def __repr__(self) -> str:
        return f"{self.value}"


class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.lookahead = self.lexer.next_token()
        
    def parse(self) -> AST:
        """
        Run through the input code and map each segment to appropriate Tokens.

        We can then parse the Token sequences into an Abstract Syntax Tree in
        order to assign semantics to the structural constituents.
        """
        return self.expression()

    def consume(self) -> None:
        self.lookahead = self.lexer.next_token()

    def error(self, string: str) -> None:
        msg = f"Expecting {string} found {self.lookahead} on line {self.lexer.line_num}"
        raise SyntaxError(msg)

    def match(self, token_type: TokenType) -> Token | None:
        """
        Match the passed TokenType against the lexer's lookahead.

        If matching, cache the lookahead Token and consume it so that we can
        get the next Token in sequence. Return the cached Token to use in
        AST construction.
        """
        if self.lookahead.token_type == token_type:
            old_token = self.lookahead
            self.consume()
            return old_token
        self.error(TokenType[token_type.name])

    def term(self) -> AST:
        node = self.factor()

        #! Binary Operation
        while self.lookahead.token_type in (
            TokenType.MUL, 
            TokenType.DIV,
        ):
            token = self.lookahead
            if token.token_type == TokenType.MUL:
                token = self.match(TokenType.MUL)
            elif token.token_type == TokenType.DIV:
                token = self.match(TokenType.DIV)

            node = BinaryOp(left=node, op=token, right=self.factor())

        return node

    def factor(self) -> AST:
        token = self.lookahead

        #! Terminal
        if token.token_type == TokenType.NUMBER:
            self.match(TokenType.NUMBER)
            expr = Terminal(token)

        #! Expression
        elif token.token_type == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            expr = self.expression()
            self.match(TokenType.RPAREN)

        return expr

    def expression(self) -> AST:
        node = self.term()

        while self.lookahead.token_type in (
            TokenType.POSITIVE, 
            TokenType.NEGATIVE,
        ):
            token = self.lookahead
            if token.token_type == TokenType.POSITIVE:
                token = self.match(TokenType.POSITIVE)
            elif token.token_type == TokenType.NEGATIVE:
                token = self.match(TokenType.NEGATIVE)
            
            node = BinaryOp(left=node, op=token, right=self.term())

        return node
