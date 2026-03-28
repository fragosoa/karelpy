# Manual de sintaxis — KarelPy

KarelPy usa una sintaxis estilo Python con indentación significativa y comandos en español. Los programas deben definir una función llamada `programa()` que es el punto de entrada.

---

## Estructura básica

```python
def programa():
    avanza()
    avanza()
    apagate()
```

Las reglas generales son:
- La indentación es de **4 espacios** por nivel (como Python)
- Cada instrucción va en su propia línea
- Los comentarios se escriben con `#`
- El programa siempre debe terminar con `apagate()` o `termina()`

---

## Instrucciones primitivas

Estas son las únicas instrucciones que mueven o modifican el estado de Karel:

| Instrucción | Descripción |
|---|---|
| `avanza()` | Karel avanza una casilla en la dirección que mira |
| `gira_izquierda()` | Karel gira 90° a la izquierda |
| `coge_zumbador()` | Karel recoge un zumbador de la casilla actual |
| `deja_zumbador()` | Karel deja un zumbador en la casilla actual |
| `apagate()` | Termina la ejecución del programa |
| `termina()` | Sale de la función actual y regresa al llamador |

> `apagate()` detiene a Karel completamente desde cualquier punto del programa.
> `termina()` solo sale de la función donde se ejecuta, como un `return` vacío.

---

## Condiciones

Las condiciones se usan dentro de `si` y `mientras`. No se pueden llamar como instrucciones.

### Estado del frente, izquierda y derecha

| Condición | Verdadero cuando... |
|---|---|
| `frente_libre()` | No hay pared ni límite del mundo al frente |
| `frente_bloqueado()` | Hay pared o límite del mundo al frente |
| `izquierda_libre()` | No hay pared a la izquierda |
| `izquierda_bloqueada()` | Hay pared a la izquierda |
| `derecha_libre()` | No hay pared a la derecha |
| `derecha_bloqueada()` | Hay pared a la derecha |

### Zumbadores

| Condición | Verdadero cuando... |
|---|---|
| `junto_a_zumbador()` | Hay al menos un zumbador en la casilla actual |
| `no_junto_a_zumbador()` | No hay zumbadores en la casilla actual |
| `mochila_vacia()` | La mochila de Karel no tiene zumbadores |
| `mochila_con_zumbadores()` | La mochila tiene uno o más zumbadores |

### Orientación

| Condición | Verdadero cuando... |
|---|---|
| `orientado_al_norte()` | Karel mira al norte |
| `orientado_al_sur()` | Karel mira al sur |
| `orientado_al_este()` | Karel mira al este |
| `orientado_al_oeste()` | Karel mira al oeste |
| `no_orientado_al_norte()` | Karel **no** mira al norte |
| `no_orientado_al_sur()` | Karel **no** mira al sur |
| `no_orientado_al_este()` | Karel **no** mira al este |
| `no_orientado_al_oeste()` | Karel **no** mira al oeste |

---

## Estructuras de control

### Condicional `if` / `else`

```python
if frente_libre():
    avanza()
else:
    gira_izquierda()
```

El bloque `else` es opcional:

```python
if junto_a_zumbador():
    coge_zumbador()
```

Para negar una condición se usa `not`:

```python
if not frente_libre():
    gira_izquierda()
```

### Ciclo `while`

Repite el bloque mientras la condición sea verdadera:

```python
while frente_libre():
    avanza()
```

### Ciclo `for`

Repite el bloque un número fijo de veces:

```python
for i in range(4):
    gira_izquierda()
```

> La variable `i` no se puede usar dentro del cuerpo — solo sirve para contar.

---

## Funciones de usuario

Se definen con `def` antes de `programa()`. No reciben parámetros ni devuelven valores.

```python
def gira_derecha():
    gira_izquierda()
    gira_izquierda()
    gira_izquierda()

def gira_media_vuelta():
    gira_izquierda()
    gira_izquierda()

def programa():
    gira_derecha()
    avanza()
    gira_media_vuelta()
    apagate()
```

Las funciones pueden llamarse entre sí y también pueden llamarse a sí mismas (recursión).

---

## Recursión

Karel soporta funciones recursivas. El caso base debe usar `termina()` para salir anticipadamente:

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

También se puede usar la estructura `if/else` clásica sin `termina()`:

```python
def avanza_hasta_pared():
    if frente_libre():
        avanza()
        avanza_hasta_pared()

def programa():
    avanza_hasta_pared()
    apagate()
```

> El límite de instrucciones es de **10,000 pasos**. Si se supera (por ejemplo, en un ciclo infinito), el programa se detiene con un error.

---

## Ejemplos completos

### Recoger todos los zumbadores del camino

```python
def programa():
    while frente_libre():
        if junto_a_zumbador():
            coge_zumbador()
        avanza()
    apagate()
```

### Recorrer el perímetro de un mundo rectangular

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

### Giro a la derecha (función auxiliar clásica)

```python
def gira_derecha():
    gira_izquierda()
    gira_izquierda()
    gira_izquierda()

def programa():
    avanza()
    gira_derecha()
    avanza()
    apagate()
```

---

## Errores comunes

| Error | Causa |
|---|---|
| `Karel chocó con una pared` | Se llamó `avanza()` hacia una pared o el borde del mundo |
| `No hay zumbadores en esta posición` | Se llamó `coge_zumbador()` en una casilla vacía |
| `La mochila está vacía` | Se llamó `deja_zumbador()` con la mochila en 0 |
| `Se superó el límite de 10,000 instrucciones` | Posible ciclo infinito |
| `Instrucción desconocida: 'x'` | Se llamó a una función que no existe |
| `'x' es una condición, no puede usarse como instrucción` | Se intentó llamar una condición fuera de `if`/`while` |
