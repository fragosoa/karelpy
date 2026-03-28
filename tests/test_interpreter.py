import pytest
from karelpy import run


def make_result(code: str, col=1, row=1, direction="NORTH", bag=0, width=10, height=10, beepers=None, walls=None):
    world_dict = {
        "width": width,
        "height": height,
        "beepers": beepers or {},
        "walls": walls or [],
    }
    robot_dict = {"col": col, "row": row, "dir": direction, "bag": bag}
    return run(code, world_dict, robot_dict)


# ------------------------------------------------------------------
# Instrucciones básicas
# ------------------------------------------------------------------

def test_avanza_norte():
    result = make_result("""\
def programa():
    avanza()
    apagate()
""")
    assert result["ok"]
    # steps[0] = inicial, steps[1] = después de avanza
    assert result["steps"][0]["robot"]["row"] == 1
    assert result["steps"][1]["robot"]["row"] == 2


def test_gira_izquierda():
    result = make_result("""\
def programa():
    gira_izquierda()
    apagate()
""")
    assert result["ok"]
    assert result["steps"][1]["robot"]["dir"] == "WEST"


def test_cuatro_giros_regresa_al_norte():
    result = make_result("""\
def programa():
    for i in range(4):
        gira_izquierda()
    apagate()
""")
    assert result["ok"]
    assert result["steps"][-1]["robot"]["dir"] == "NORTH"


# ------------------------------------------------------------------
# Zumbadores
# ------------------------------------------------------------------

def test_coge_zumbador():
    result = make_result("""\
def programa():
    coge_zumbador()
    apagate()
""", beepers={"1,1": 2}, bag=0)
    assert result["ok"]
    last = result["steps"][-1]
    assert last["beepers"].get("1,1", 0) == 1
    assert last["robot"]["bag"] == 1


def test_deja_zumbador():
    result = make_result("""\
def programa():
    deja_zumbador()
    apagate()
""", bag=3)
    assert result["ok"]
    last = result["steps"][-1]
    assert last["beepers"].get("1,1", 0) == 1
    assert last["robot"]["bag"] == 2


def test_coge_sin_zumbadores_error():
    result = make_result("""\
def programa():
    coge_zumbador()
    apagate()
""")
    assert not result["ok"]
    assert "zumbador" in result["error"].lower()


def test_deja_mochila_vacia_error():
    result = make_result("""\
def programa():
    deja_zumbador()
    apagate()
""", bag=0)
    assert not result["ok"]


# ------------------------------------------------------------------
# Control de flujo
# ------------------------------------------------------------------

def test_if_frente_libre():
    # Sin paredes → avanza
    result = make_result("""\
def programa():
    if frente_libre():
        avanza()
    apagate()
""")
    assert result["ok"]
    assert result["steps"][-1]["robot"]["row"] == 2


def test_if_else_frente_bloqueado():
    # Karel en row=10 (borde norte) → frente bloqueado → gira
    result = make_result("""\
def programa():
    if frente_libre():
        avanza()
    else:
        gira_izquierda()
    apagate()
""", row=10)
    assert result["ok"]
    assert result["steps"][-1]["robot"]["dir"] == "WEST"


def test_while_avanza():
    result = make_result("""\
def programa():
    while frente_libre():
        avanza()
    apagate()
""", row=1)
    assert result["ok"]
    # Karel debe quedar en row=10 (borde norte)
    assert result["steps"][-1]["robot"]["row"] == 10


def test_for_loop():
    result = make_result("""\
def programa():
    for i in range(3):
        avanza()
    apagate()
""")
    assert result["ok"]
    assert result["steps"][-1]["robot"]["row"] == 4


# ------------------------------------------------------------------
# Funciones de usuario
# ------------------------------------------------------------------

def test_funcion_usuario():
    result = make_result("""\
def gira_derecha():
    gira_izquierda()
    gira_izquierda()
    gira_izquierda()

def programa():
    gira_derecha()
    apagate()
""")
    assert result["ok"]
    assert result["steps"][-1]["robot"]["dir"] == "EAST"


# ------------------------------------------------------------------
# Errores de runtime
# ------------------------------------------------------------------

def test_choca_con_pared():
    result = make_result("""\
def programa():
    avanza()
    apagate()
""", row=10)  # Borde norte
    assert not result["ok"]
    assert "pared" in result["error"].lower()


def test_snapshots_iniciales():
    result = make_result("""\
def programa():
    apagate()
""")
    assert result["ok"]
    # Debe haber al menos el snapshot inicial
    assert len(result["steps"]) >= 1
