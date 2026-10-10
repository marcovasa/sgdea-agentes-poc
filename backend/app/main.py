from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.models import Radicado, TipoPQRSDF
from app.routers import radicados
from app.schemas import RadicadoCrear
from app.services.radicacion import crear_radicado

DEMO = [
    (TipoPQRSDF.PETICION, "Petición de copia de resolución de pensión", "Ana Gómez"),
    (TipoPQRSDF.QUEJA, "Queja por demora en atención en ventanilla", "Luis Pérez"),
    (TipoPQRSDF.CONSULTA, "Consulta sobre requisitos de licencia", "María Ruiz"),
    (TipoPQRSDF.INFORMACION, "Solicitud de información contractual 2025", "Carlos Díaz"),
    (TipoPQRSDF.RECLAMO, "Reclamo por cobro de estampilla", "Sofía León"),
]


def sembrar_demo() -> None:
    with SessionLocal() as session:
        if session.scalar(select(func.count()).select_from(Radicado)):
            return
        hoy = date.today()
        for i, (tipo, asunto, remitente) in enumerate(DEMO):
            crear_radicado(
                session,
                RadicadoCrear(
                    tipo=tipo,
                    asunto=asunto,
                    remitente=remitente,
                    fecha_radicacion=hoy - timedelta(days=i * 3),
                ),
            )


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    if settings.seed_demo:
        sembrar_demo()
    yield


app = FastAPI(title="Mini-SGDEA Radicación", version=settings.version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(radicados.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": settings.version}
