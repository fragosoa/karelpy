from typing import Dict, List

from .ast_nodes import Call, Condition, ForLoop, FunctionDef, IfStatement, Node, Program, WhileLoop
from .errors import KarelReturn, KarelRuntimeError, KarelShutdown, MaxStepsError
from .robot import Robot
from .world import DIRECTION_DELTA, TURN_LEFT, TURN_RIGHT, World

MAX_STEPS = 10_000

# Instrucciones primitivas de Karel
PRIMITIVES = {"avanza", "gira_izquierda", "coge_zumbador", "deja_zumbador", "apagate", "termina"}

# Condiciones válidas de Karel
CONDITIONS = {
    "frente_libre",
    "frente_bloqueado",
    "izquierda_libre",
    "izquierda_bloqueada",
    "derecha_libre",
    "derecha_bloqueada",
    "junto_a_zumbador",
    "no_junto_a_zumbador",
    "mochila_vacia",
    "mochila_con_zumbadores",
    "orientado_al_norte",
    "no_orientado_al_norte",
    "orientado_al_sur",
    "no_orientado_al_sur",
    "orientado_al_este",
    "no_orientado_al_este",
    "orientado_al_oeste",
    "no_orientado_al_oeste",
}


class Interpreter:
    def __init__(self, world: World, robot: Robot):
        self.world = world
        self.robot = robot
        self.functions: Dict[str, FunctionDef] = {}
        self.steps: List[dict] = []
        self.step_count = 0

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def run(self, program: Program) -> List[dict]:
        """Ejecuta el programa y devuelve la lista de snapshots."""
        for func in program.functions:
            self.functions[func.name] = func
        self.functions[program.main.name] = program.main

        self._snapshot()  # estado inicial

        try:
            self._exec_block(program.main.body)
        except (KarelShutdown, KarelReturn):
            pass  # apagate() o termina() al nivel de programa()

        return self.steps

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    def _snapshot(self):
        self.steps.append(
            {
                "robot": self.robot.to_dict(),
                "beepers": {
                    f"{c},{r}": n for (c, r), n in self.world.beepers.items()
                },
            }
        )

    # ------------------------------------------------------------------
    # Ejecución
    # ------------------------------------------------------------------

    def _exec_block(self, statements: List[Node]):
        for stmt in statements:
            self._exec_stmt(stmt)

    def _exec_stmt(self, stmt: Node):
        if isinstance(stmt, Call):
            self._exec_call(stmt)
        elif isinstance(stmt, IfStatement):
            self._exec_if(stmt)
        elif isinstance(stmt, WhileLoop):
            self._exec_while(stmt)
        elif isinstance(stmt, ForLoop):
            self._exec_for(stmt)
        else:
            raise KarelRuntimeError(f"Nodo desconocido: {type(stmt).__name__}")

    def _exec_call(self, stmt: Call):
        name = stmt.name
        # Las funciones del usuario tienen prioridad sobre las primitivas
        if name in self.functions:
            try:
                self._exec_block(self.functions[name].body)
            except KarelReturn:
                pass  # termina() → sale de esta función, continúa en el llamador
        elif name in PRIMITIVES:
            self._exec_primitive(name, stmt.line)
        elif name in CONDITIONS:
            raise KarelRuntimeError(
                f"'{name}' es una condición, no puede usarse como instrucción",
                stmt.line,
            )
        else:
            raise KarelRuntimeError(f"Instrucción desconocida: '{name}'", stmt.line)

    def _exec_primitive(self, name: str, line: int):
        self.step_count += 1
        if self.step_count > MAX_STEPS:
            raise MaxStepsError(
                f"Se superó el límite de {MAX_STEPS} instrucciones. "
                "Revisa si tu programa tiene un ciclo infinito."
            )

        r = self.robot
        w = self.world

        if name == "avanza":
            if w.has_wall(r.col, r.row, r.direction):
                raise KarelRuntimeError(
                    "Karel chocó con una pared al intentar avanzar", line
                )
            dc, dr = DIRECTION_DELTA[r.direction]
            r.col += dc
            r.row += dr

        elif name == "gira_izquierda":
            r.direction = TURN_LEFT[r.direction]

        elif name == "coge_zumbador":
            if w.get_beepers(r.col, r.row) == 0:
                raise KarelRuntimeError(
                    "No hay zumbadores en esta posición para recoger", line
                )
            w.add_beepers(r.col, r.row, -1)
            if r.bag != -1:
                r.bag += 1

        elif name == "deja_zumbador":
            if r.bag == 0:
                raise KarelRuntimeError(
                    "La mochila está vacía, Karel no puede dejar zumbadores", line
                )
            w.add_beepers(r.col, r.row, 1)
            if r.bag != -1:
                r.bag -= 1

        elif name == "apagate":
            raise KarelShutdown()

        elif name == "termina":
            raise KarelReturn()

        self._snapshot()

    def _exec_if(self, stmt: IfStatement):
        if self._eval_condition(stmt.condition):
            self._exec_block(stmt.then_body)
        else:
            self._exec_block(stmt.else_body)

    def _exec_while(self, stmt: WhileLoop):
        iterations = 0
        while self._eval_condition(stmt.condition):
            iterations += 1
            if iterations > MAX_STEPS:
                raise MaxStepsError(
                    f"Se superó el límite de {MAX_STEPS} iteraciones en 'mientras'. "
                    "Revisa si tu programa tiene un ciclo infinito."
                )
            self._exec_block(stmt.body)

    def _exec_for(self, stmt: ForLoop):
        for _ in range(stmt.count):
            self._exec_block(stmt.body)

    # ------------------------------------------------------------------
    # Evaluación de condiciones
    # ------------------------------------------------------------------

    def _eval_condition(self, cond: Condition) -> bool:
        result = self._eval_condition_name(cond.name, cond.line)
        return not result if cond.negated else result

    def _eval_condition_name(self, name: str, line: int) -> bool:
        r = self.robot
        w = self.world

        if name == "frente_libre":
            return not w.has_wall(r.col, r.row, r.direction)
        if name == "frente_bloqueado":
            return w.has_wall(r.col, r.row, r.direction)
        if name == "izquierda_libre":
            return not w.has_wall(r.col, r.row, TURN_LEFT[r.direction])
        if name == "izquierda_bloqueada":
            return w.has_wall(r.col, r.row, TURN_LEFT[r.direction])
        if name == "derecha_libre":
            return not w.has_wall(r.col, r.row, TURN_RIGHT[r.direction])
        if name == "derecha_bloqueada":
            return w.has_wall(r.col, r.row, TURN_RIGHT[r.direction])
        if name == "junto_a_zumbador":
            return w.get_beepers(r.col, r.row) > 0
        if name == "no_junto_a_zumbador":
            return w.get_beepers(r.col, r.row) == 0
        if name == "mochila_vacia":
            return r.bag == 0
        if name == "mochila_con_zumbadores":
            return r.bag != 0  # -1 = infinito también cuenta
        if name == "orientado_al_norte":
            return r.direction == "NORTH"
        if name == "no_orientado_al_norte":
            return r.direction != "NORTH"
        if name == "orientado_al_sur":
            return r.direction == "SOUTH"
        if name == "no_orientado_al_sur":
            return r.direction != "SOUTH"
        if name == "orientado_al_este":
            return r.direction == "EAST"
        if name == "no_orientado_al_este":
            return r.direction != "EAST"
        if name == "orientado_al_oeste":
            return r.direction == "WEST"
        if name == "no_orientado_al_oeste":
            return r.direction != "WEST"

        raise KarelRuntimeError(f"Condición desconocida: '{name}'", line)
