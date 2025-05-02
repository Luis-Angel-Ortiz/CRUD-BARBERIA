from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")


class CitaIn(BaseModel):
    cliente: str
    fecha: str
    hora: str
    servicio: str

class Cita(CitaIn):
    id: int


citas: List[Cita] = []
next_id = 1


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/citas", response_model=List[Cita])
async def listar_citas():
    return citas


@app.post("/api/citas", response_model=Cita)
async def crear_cita(cita_in: CitaIn):
    global next_id
    cita = Cita(id=next_id, **cita_in.dict())
    next_id += 1
    citas.append(cita)
    return cita


@app.put("/api/citas/{cita_id}", response_model=Cita)
async def actualizar_cita(cita_id: int, cita_in: CitaIn):
    for idx, c in enumerate(citas):
        if c.id == cita_id:
            updated = Cita(id=cita_id, **cita_in.dict())
            citas[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Cita no encontrada")


@app.delete("/api/citas/{cita_id}")
async def eliminar_cita(cita_id: int):
    global citas
    original_len = len(citas)
    citas = [c for c in citas if c.id != cita_id]
    if len(citas) == original_len:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return {"mensaje": "Cita eliminada"}


# uvicorn main:app --reload
