"""
karelpy — Motor Karel con sintaxis Python.

Uso básico:
    from karelpy import run

    result = run(code, world_dict, robot_dict)
    if result["ok"]:
        for step in result["steps"]:
            print(step)
    else:
        print(result["error"])
"""

from .errors import KarelError, KarelRuntimeError, LexerError, MaxStepsError, ParseError
from .interpreter import Interpreter
from .lexer import Lexer
from .parser import Parser
from .robot import Robot
from .world import World


def run(code: str, world_dict: dict, robot_dict: dict) -> dict:
    """
    Compila y ejecuta un programa Karel.

    Args:
        code:       Código fuente Karel (sintaxis Python).
        world_dict: Estado inicial del mundo  (salida de World.to_dict()).
        robot_dict: Estado inicial del robot  (salida de Robot.to_dict()).

    Returns:
        {"ok": True,  "steps": [...]}         — ejecución exitosa
        {"ok": False, "error": "...", "line": N} — error de compilación o runtime
    """
    try:
        tokens = Lexer(code).tokenize()
        program = Parser(tokens).parse()
        world = World.from_dict(world_dict)
        robot = Robot.from_dict(robot_dict)
        steps = Interpreter(world, robot).run(program)
        return {"ok": True, "steps": steps}
    except KarelError as exc:
        return {
            "ok": False,
            "error": str(exc),
            "line": getattr(exc, "line", None),
        }


__all__ = [
    "run",
    "Lexer",
    "Parser",
    "Interpreter",
    "World",
    "Robot",
    "KarelError",
    "LexerError",
    "ParseError",
    "KarelRuntimeError",
    "MaxStepsError",
]
