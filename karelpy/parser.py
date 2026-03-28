from typing import List

from .ast_nodes import (
    Call,
    Condition,
    ForLoop,
    FunctionDef,
    IfStatement,
    Node,
    Program,
    WhileLoop,
)
from .errors import ParseError
from .lexer import Token, TokenType


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------------
    # Helpers de navegación
    # ------------------------------------------------------------------

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        return self.tokens[min(idx, len(self.tokens) - 1)]

    def advance(self) -> Token:
        token = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def expect(self, ttype: TokenType) -> Token:
        if self.current.type != ttype:
            raise ParseError(
                f"Se esperaba {ttype.name}, se encontró "
                f"{self.current.type.name} ({self.current.value!r})",
                self.current.line,
                self.current.col,
            )
        return self.advance()

    def match(self, *types: TokenType) -> bool:
        return self.current.type in types

    # ------------------------------------------------------------------
    # Punto de entrada
    # ------------------------------------------------------------------

    def parse(self) -> Program:
        functions: List[FunctionDef] = []
        main: FunctionDef | None = None

        while not self.match(TokenType.EOF):
            func = self._parse_function_def()
            if func.name == "programa":
                main = func
            else:
                functions.append(func)

        if main is None:
            raise ParseError("No se encontró la función 'programa'", 0, 0)

        return Program(functions=functions, main=main)

    # ------------------------------------------------------------------
    # Reglas de la gramática
    # ------------------------------------------------------------------

    def _parse_function_def(self) -> FunctionDef:
        token = self.expect(TokenType.DEF)
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        body = self._parse_block()
        return FunctionDef(name=name_token.value, body=body, line=token.line)

    def _parse_block(self) -> List[Node]:
        """Consume NEWLINE INDENT statements+ DEDENT."""
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        statements: List[Node] = []
        while not self.match(TokenType.DEDENT, TokenType.EOF):
            stmt = self._parse_statement()
            statements.append(stmt)
        self.expect(TokenType.DEDENT)
        return statements

    def _parse_statement(self) -> Node:
        if self.match(TokenType.IF):
            return self._parse_if()
        if self.match(TokenType.WHILE):
            return self._parse_while()
        if self.match(TokenType.FOR):
            return self._parse_for()
        if self.match(TokenType.IDENTIFIER):
            return self._parse_call()
        raise ParseError(
            f"Instrucción inesperada: {self.current.value!r}",
            self.current.line,
            self.current.col,
        )

    def _parse_call(self) -> Call:
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.NEWLINE)
        return Call(name=name_token.value, line=name_token.line)

    def _parse_if(self) -> IfStatement:
        token = self.expect(TokenType.IF)
        condition = self._parse_condition()
        self.expect(TokenType.COLON)
        then_body = self._parse_block()
        else_body: List[Node] = []
        if self.match(TokenType.ELSE):
            self.advance()  # consume 'else'
            self.expect(TokenType.COLON)
            else_body = self._parse_block()
        return IfStatement(
            condition=condition,
            then_body=then_body,
            else_body=else_body,
            line=token.line,
        )

    def _parse_while(self) -> WhileLoop:
        token = self.expect(TokenType.WHILE)
        condition = self._parse_condition()
        self.expect(TokenType.COLON)
        body = self._parse_block()
        return WhileLoop(condition=condition, body=body, line=token.line)

    def _parse_for(self) -> ForLoop:
        token = self.expect(TokenType.FOR)
        self.expect(TokenType.IDENTIFIER)   # variable de iteración (ignorada)
        self.expect(TokenType.IN)
        self.expect(TokenType.RANGE)
        self.expect(TokenType.LPAREN)
        count_token = self.expect(TokenType.INTEGER)
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        body = self._parse_block()
        return ForLoop(count=count_token.value, body=body, line=token.line)

    def _parse_condition(self) -> Condition:
        negated = False
        if self.match(TokenType.NOT):
            self.advance()
            negated = True
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)
        self.expect(TokenType.RPAREN)
        return Condition(name=name_token.value, negated=negated, line=name_token.line)
