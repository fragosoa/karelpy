import pytest
from karelpy.ast_nodes import Call, ForLoop, IfStatement, WhileLoop
from karelpy.errors import ParseError
from karelpy.lexer import Lexer
from karelpy.parser import Parser


def parse(source: str):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def test_parse_simple():
    program = parse("""\
def programa():
    avanza()
    apagate()
""")
    assert program.main is not None
    assert program.main.name == "programa"
    assert len(program.main.body) == 2
    assert isinstance(program.main.body[0], Call)
    assert program.main.body[0].name == "avanza"


def test_parse_user_function():
    program = parse("""\
def gira_derecha():
    gira_izquierda()
    gira_izquierda()
    gira_izquierda()

def programa():
    gira_derecha()
    apagate()
""")
    assert len(program.functions) == 1
    assert program.functions[0].name == "gira_derecha"


def test_parse_if_else():
    program = parse("""\
def programa():
    if frente_libre():
        avanza()
    else:
        gira_izquierda()
    apagate()
""")
    stmt = program.main.body[0]
    assert isinstance(stmt, IfStatement)
    assert stmt.condition.name == "frente_libre"
    assert not stmt.condition.negated
    assert len(stmt.then_body) == 1
    assert len(stmt.else_body) == 1


def test_parse_if_not():
    program = parse("""\
def programa():
    if not frente_libre():
        gira_izquierda()
    apagate()
""")
    stmt = program.main.body[0]
    assert isinstance(stmt, IfStatement)
    assert stmt.condition.negated


def test_parse_while():
    program = parse("""\
def programa():
    while frente_libre():
        avanza()
    apagate()
""")
    stmt = program.main.body[0]
    assert isinstance(stmt, WhileLoop)
    assert stmt.condition.name == "frente_libre"


def test_parse_for():
    program = parse("""\
def programa():
    for i in range(4):
        gira_izquierda()
    apagate()
""")
    stmt = program.main.body[0]
    assert isinstance(stmt, ForLoop)
    assert stmt.count == 4


def test_missing_programa_raises():
    with pytest.raises(ParseError):
        parse("""\
def otra_funcion():
    avanza()
""")
