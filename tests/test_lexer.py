import pytest
from karelpy.lexer import Lexer, TokenType


def types(source: str):
    return [t.type for t in Lexer(source).tokenize()]


def test_simple_program_tokens():
    source = """\
def programa():
    avanza()
    apagate()
"""
    result = types(source)
    assert TokenType.DEF in result
    assert TokenType.IDENTIFIER in result
    assert TokenType.INDENT in result
    assert TokenType.DEDENT in result
    assert TokenType.NEWLINE in result
    assert TokenType.EOF in result


def test_if_else_tokens():
    source = """\
def programa():
    if frente_libre():
        avanza()
    else:
        gira_izquierda()
    apagate()
"""
    result = types(source)
    assert TokenType.IF in result
    assert TokenType.ELSE in result


def test_while_tokens():
    source = """\
def programa():
    while frente_libre():
        avanza()
    apagate()
"""
    result = types(source)
    assert TokenType.WHILE in result


def test_for_tokens():
    source = """\
def programa():
    for i in range(3):
        gira_izquierda()
    apagate()
"""
    result = types(source)
    assert TokenType.FOR in result
    assert TokenType.IN in result
    assert TokenType.RANGE in result
    assert TokenType.INTEGER in result


def test_not_token():
    source = """\
def programa():
    if not frente_libre():
        gira_izquierda()
    apagate()
"""
    result = types(source)
    assert TokenType.NOT in result


def test_comment_ignored():
    source = """\
# Este es un comentario
def programa():
    avanza()  # también aquí
    apagate()
"""
    tokens = Lexer(source).tokenize()
    identifiers = [t.value for t in tokens if t.type == TokenType.IDENTIFIER]
    assert "programa" in identifiers
    assert "avanza" in identifiers


def test_unexpected_character_raises():
    from karelpy.errors import LexerError
    with pytest.raises(LexerError):
        Lexer("def programa():\n    @avanza()\n").tokenize()
