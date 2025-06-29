# app/main.py
"""
Punto de entrada principal para el microservicio FastAPI encargado de filtrar citas médicas.
Exposición de la API /filtrar_citas.
"""

from fastapi import FastAPI, HTTPException
from app.filter_engine import filtrar_citas, cargar_reglas
from app.models import Cita, ResultadoFiltro
from typing import List
import logging

app = FastAPI(
    title="Filtro de Citas",
    description="Microservicio para filtrar citas médicas según reglas de negocio dinámicas.",
    version="0.1.0"
)

@app.get("/", tags=["Root"])
def root():
    """
    Endpoint de verificación de estado.

    @return: Mensaje de salud del servicio.
    """
    return {"message": "Servidor activo"}

@app.post(
    "/filtrar_citas",
    response_model=List[ResultadoFiltro],
    summary="Filtra una lista de citas médicas según reglas de negocio",
    description=(
        "Recibe una lista de citas médicas y retorna solo aquellas que cumplen "
        "con las reglas de negocio definidas para ser contactadas. "
        "El campo fecha debe estar en formato ISO 8601 con zona horaria (ej: 2025-07-01T09:00:00-04:00)."
    ),
    tags=["Filtrado"]
)
def endpoint_filtrar_citas(citas: List[Cita]) -> List[ResultadoFiltro]:
    """
    Filtra una lista de citas aplicando reglas clínicas predefinidas.

    @param citas: Lista de objetos Cita a evaluar.
    @return: Lista de objetos ResultadoFiltro con pacientes a contactar.
    @raise HTTPException: Si ocurre un error cargando reglas o procesando las citas.
    """
    try:
        reglas = cargar_reglas("app/rules/rules.json")
    except Exception as e:
        logging.error(f"Error cargando reglas: {e}")
        raise HTTPException(status_code=500, detail="Error cargando reglas clínicas")

    try:
        return filtrar_citas(citas, reglas)
    except Exception as e:
        logging.error(f"Error filtrando citas: {e}")
        raise HTTPException(status_code=500, detail="Error filtrando citas")
