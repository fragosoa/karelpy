from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routes.run import router

BASE = Path(__file__).parent

app = FastAPI(title="KarelPy")

app.include_router(router)

app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/")
def index():
    return FileResponse(BASE / "templates" / "index.html")
