from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from .errors import LexerError


class TokenType(Enum):
    # Palabras clave de Python
    DEF = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    RANGE = auto()
    NOT = auto()
    # Identificadores y literales
    IDENTIFIER = auto()
    INTEGER = auto()
    # Puntuación
    LPAREN = auto()
    RPAREN = auto()
    COLON = auto()
    COMMA = auto()
    # Estructura (indentación)
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


KEYWORDS: dict[str, TokenType] = {
    "def": TokenType.DEF,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "range": TokenType.RANGE,
    "not": TokenType.NOT,
}


@dataclass
class Token:
    type: TokenType
    value: object
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


class Lexer:
    def __init__(self, source: str):
        self.source = source

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        indent_stack = [0]
        lines = self.source.splitlines()

        for line_num, line in enumerate(lines, start=1):
            # Eliminar comentario inline
            comment_pos = line.find("#")
            effective = line[:comment_pos] if comment_pos >= 0 else line

            # Saltar líneas vacías
            if not effective.strip():
                continue

            # Medir indentación (solo espacios)
            indent = 0
            while indent < len(effective) and effective[indent] == " ":
                indent += 1

            current_indent = indent_stack[-1]

            if indent > current_indent:
                tokens.append(Token(TokenType.INDENT, indent, line_num, 1))
                indent_stack.append(indent)
            elif indent < current_indent:
                while indent_stack[-1] > indent:
                    indent_stack.pop()
                    tokens.append(Token(TokenType.DEDENT, indent_stack[-1], line_num, 1))
                if indent_stack[-1] != indent:
                    raise LexerError("Indentación inconsistente", line_num, 1)

            # Tokenizar el contenido de la línea (sin la indentación)
            self._tokenize_line(effective.strip(), line_num, indent + 1, tokens)
            tokens.append(Token(TokenType.NEWLINE, "\n", line_num, len(effective) + 1))

        # Cerrar bloques de indentación abiertos al final del archivo
        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, 0, len(lines) + 1, 1))

        tokens.append(Token(TokenType.EOF, None, len(lines) + 1, 1))
        return tokens

    def _tokenize_line(self, line: str, line_num: int, col_offset: int, tokens: List[Token]):
        pos = 0
        while pos < len(line):
            ch = line[pos]

            # Espacios (pueden aparecer entre tokens en la misma línea)
            if ch == " ":
                pos += 1
                continue

            col = col_offset + pos

            # Entero
            if ch.isdigit():
                start = pos
                while pos < len(line) and line[pos].isdigit():
                    pos += 1
                tokens.append(Token(TokenType.INTEGER, int(line[start:pos]), line_num, col))
                continue

            # Identificador o palabra clave
            if ch.isalpha() or ch == "_":
                start = pos
                while pos < len(line) and (line[pos].isalnum() or line[pos] == "_"):
                    pos += 1
                word = line[start:pos]
                ttype = KEYWORDS.get(word, TokenType.IDENTIFIER)
                tokens.append(Token(ttype, word, line_num, col))
                continue

            # Tokens de un solo carácter
            singles = {
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                ":": TokenType.COLON,
                ",": TokenType.COMMA,
            }
            if ch in singles:
                tokens.append(Token(singles[ch], ch, line_num, col))
                pos += 1
                continue

            raise LexerError(f"Carácter inesperado: {ch!r}", line_num, col)
