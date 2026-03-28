from dataclasses import dataclass

from .world import NORTH


@dataclass
class Robot:
    col: int = 1
    row: int = 1
    direction: str = NORTH
    # Cantidad de zumbadores en la mochila. -1 = infinito.
    bag: int = 0

    def to_dict(self) -> dict:
        return {
            "col": self.col,
            "row": self.row,
            "dir": self.direction,
            "bag": self.bag,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Robot":
        return cls(
            col=data.get("col", 1),
            row=data.get("row", 1),
            direction=data.get("dir", NORTH),
            bag=data.get("bag", 0),
        )
