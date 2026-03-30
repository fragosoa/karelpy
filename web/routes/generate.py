import os
import re
from pathlib import Path

from openai import OpenAI
from fastapi import APIRouter
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
router = APIRouter(prefix="/api")

SINTAXIS_PATH = Path(__file__).parent.parent.parent / "SINTAXIS.md"

FEW_SHOT = """
## Ejemplos de referencia

PROBLEMA: Karel avanza hasta encontrar una pared.
SOLUCIÓN:
```python
def avanza_hasta_pared():
    if frente_bloqueado():
        termina()
    avanza()
    avanza_hasta_pared()

def programa():
    avanza_hasta_pared()
    apagate()
```

PROBLEMA: Karel recoge todos los zumbadores de la casilla actual.
SOLUCIÓN:
```python
def programa():
    while junto_a_zumbador():
        coge_zumbador()
    apagate()
```

PROBLEMA: Karel gira a la derecha.
SOLUCIÓN:
```python
def gira_derecha():
    gira_izquierda()
    gira_izquierda()
    gira_izquierda()

def programa():
    gira_derecha()
    apagate()
```

PROBLEMA: Karel recorre el perímetro de un mundo rectangular.
SOLUCIÓN:
```python
def avanza_hasta_pared():
    if frente_bloqueado():
        termina()
    avanza()
    avanza_hasta_pared()

def programa():
    for i in range(4):
        avanza_hasta_pared()
        gira_izquierda()
    apagate()
```

PROBLEMA: Karel deja una torre de zumbadores en su posición actual usando todos los de la mochila.
SOLUCIÓN:
```python
def programa():
    while mochila_con_zumbadores():
        deja_zumbador()
    apagate()
```
"""


def _build_system_prompt() -> str:
    try:
        sintaxis = SINTAXIS_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        sintaxis = ""

    return f"""Eres un experto en KarelPy, un lenguaje para programar al robot Karel con sintaxis estilo Python en español.

Tu única tarea es generar código KarelPy correcto y funcional que resuelva el problema que te describe el usuario.

REGLAS ESTRICTAS:
- Responde ÚNICAMENTE con el bloque de código, sin explicaciones ni texto adicional.
- El código debe ir dentro de un bloque ```python ... ```.
- Siempre define la función `programa()` como punto de entrada.
- Usa SOLO las instrucciones y condiciones definidas en la referencia de sintaxis.
- No uses variables, parámetros, print(), ni ninguna construcción de Python estándar fuera de las permitidas.
- La indentación debe ser de 4 espacios.

{sintaxis}

{FEW_SHOT}"""


def _extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


class GenerateRequest(BaseModel):
    prompt: str


@router.post("/generate")
def generate_karel(req: GenerateRequest) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "ok": False,
            "error": "OPENAI_API_KEY no está configurada. Agrégala en el archivo .env.",
        }

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user",   "content": req.prompt},
            ],
        )
        raw  = response.choices[0].message.content
        code = _extract_code(raw)
        return {"ok": True, "code": code}
    except Exception as exc:
        return {"ok": False, "error": f"Error al generar código: {exc}"}
