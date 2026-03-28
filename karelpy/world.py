from typing import Dict, Set, Tuple

NORTH = "NORTH"
SOUTH = "SOUTH"
EAST = "EAST"
WEST = "WEST"

DIRECTIONS = (NORTH, SOUTH, EAST, WEST)

# Delta (dcol, drow) por dirección. La fila aumenta hacia el norte.
DIRECTION_DELTA: Dict[str, Tuple[int, int]] = {
    NORTH: (0, 1),
    SOUTH: (0, -1),
    EAST: (1, 0),
    WEST: (-1, 0),
}

OPPOSITE: Dict[str, str] = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}

# Girar a la izquierda: N→O→S→E→N
TURN_LEFT: Dict[str, str] = {NORTH: WEST, WEST: SOUTH, SOUTH: EAST, EAST: NORTH}

# Girar a la derecha: N→E→S→O→N
TURN_RIGHT: Dict[str, str] = {NORTH: EAST, EAST: SOUTH, SOUTH: WEST, WEST: NORTH}


class World:
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        # {(col, row): cantidad_de_zumbadores}
        self.beepers: Dict[Tuple[int, int], int] = {}
        # {(col, row, direction)} — paredes interiores almacenadas en ambos lados
        self.walls: Set[Tuple[int, int, str]] = set()

    # ------------------------------------------------------------------
    # Geometría
    # ------------------------------------------------------------------

    def in_bounds(self, col: int, row: int) -> bool:
        return 1 <= col <= self.width and 1 <= row <= self.height

    def has_wall(self, col: int, row: int, direction: str) -> bool:
        """Devuelve True si hay una pared en esa dirección (incluye límites del mundo)."""
        dc, dr = DIRECTION_DELTA[direction]
        ncol, nrow = col + dc, row + dr
        if not self.in_bounds(ncol, nrow):
            return True  # pared de frontera
        return (col, row, direction) in self.walls

    def add_wall(self, col: int, row: int, direction: str):
        """Agrega una pared y su espejo en la celda vecina."""
        self.walls.add((col, row, direction))
        dc, dr = DIRECTION_DELTA[direction]
        ncol, nrow = col + dc, row + dr
        if self.in_bounds(ncol, nrow):
            self.walls.add((ncol, nrow, OPPOSITE[direction]))

    # ------------------------------------------------------------------
    # Zumbadores
    # ------------------------------------------------------------------

    def get_beepers(self, col: int, row: int) -> int:
        return self.beepers.get((col, row), 0)

    def add_beepers(self, col: int, row: int, delta: int):
        current = self.beepers.get((col, row), 0)
        new_count = current + delta
        if new_count <= 0:
            self.beepers.pop((col, row), None)
        else:
            self.beepers[(col, row)] = new_count

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "beepers": {f"{c},{r}": n for (c, r), n in self.beepers.items()},
            "walls": [[c, r, d] for c, r, d in self.walls],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "World":
        world = cls(data.get("width", 10), data.get("height", 10))
        for key, count in data.get("beepers", {}).items():
            col, row = map(int, key.split(","))
            world.beepers[(col, row)] = count
        for wall in data.get("walls", []):
            col, row, direction = int(wall[0]), int(wall[1]), wall[2]
            world.add_wall(col, row, direction)  # agrega el espejo automáticamente
        return world
