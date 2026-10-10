from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import ListaRadicados, RadicadoCrear, RadicadoSalida
from app.services import radicacion

router = APIRouter(prefix="/api/radicados", tags=["radicados"])


@router.get("", response_model=ListaRadicados)
def listar(q: str | None = None, session: Session = Depends(get_session)):
    items = radicacion.buscar_radicados(session, q)
    return ListaRadicados(total=len(items), items=items)


@router.post("", response_model=RadicadoSalida, status_code=status.HTTP_201_CREATED)
def radicar(datos: RadicadoCrear, session: Session = Depends(get_session)):
    return radicacion.crear_radicado(session, datos)


@router.get("/{numero}", response_model=RadicadoSalida)
def obtener(numero: str, session: Session = Depends(get_session)):
    radicado = radicacion.obtener_por_numero(session, numero)
    if radicado is None:
        raise HTTPException(status_code=404, detail="Radicado no encontrado")
    return radicado
