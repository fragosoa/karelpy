from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Node:
    line: int = 0


@dataclass
class Program(Node):
    functions: List["FunctionDef"] = field(default_factory=list)
    main: Optional["FunctionDef"] = None


@dataclass
class FunctionDef(Node):
    name: str = ""
    body: List[Node] = field(default_factory=list)


@dataclass
class Call(Node):
    """Llamada a una instrucción primitiva o función definida por el usuario."""
    name: str = ""


@dataclass
class Condition(Node):
    name: str = ""
    negated: bool = False


@dataclass
class IfStatement(Node):
    condition: Optional[Condition] = None
    then_body: List[Node] = field(default_factory=list)
    else_body: List[Node] = field(default_factory=list)


@dataclass
class WhileLoop(Node):
    condition: Optional[Condition] = None
    body: List[Node] = field(default_factory=list)


@dataclass
class ForLoop(Node):
    count: int = 0
    body: List[Node] = field(default_factory=list)
