from fastapi import APIRouter
from pydantic import BaseModel

from karelpy import run

router = APIRouter(prefix="/api")


class RunRequest(BaseModel):
    code: str
    world: dict
    robot: dict


@router.post("/run")
def run_karel(req: RunRequest) -> dict:
    return run(req.code, req.world, req.robot)
