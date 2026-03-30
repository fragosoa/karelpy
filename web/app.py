from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routes.generate import router as generate_router
from .routes.run import router as run_router

BASE = Path(__file__).parent

app = FastAPI(title="KarelPy")

app.include_router(run_router)
app.include_router(generate_router)

app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/")
def index():
    return FileResponse(BASE / "templates" / "index.html")
