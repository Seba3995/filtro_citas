# app/models.py
"""
Modelos Pydantic para la entrada y salida del sistema de filtrado de citas.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

class Cita(BaseModel):
    """
    Modelo de entrada para una cita médica.

    """
    fecha_cita: datetime = Field(..., description="Fecha y hora de la cita (formato ISO 8601 con zona horaria)")
    especialidad: str = Field(..., description="Especialidad médica asociada a la cita")
    tipo_atencion: Literal["primera vez", "control"] = Field(..., description="Tipo de atención")
    edad: int = Field(..., ge=0, description="Edad del paciente en años")
    estado_cita: Literal["agendada", "confirmada", "espera"] = Field(..., description="Estado actual de la cita")
    rut_profesional: str = Field(..., description="RUT del profesional tratante")
    nombre_paciente: str = Field(..., description="Nombre completo del paciente")

class ResultadoFiltro(BaseModel):
    """
    Modelo de salida para el resultado del filtrado de citas.

    """
    paciente: str = Field(..., description="Nombre del paciente evaluado")
    fecha_cita: datetime = Field(..., description="Fecha y hora de la cita (formato ISO 8601 con zona horaria)")
    accion: Literal["contactar", "excluir", "no_contactar"] = Field(..., description="Acción resultante para la cita")
    via: Optional[str] = Field(None, description="Canal sugerido para el contacto (ej: WhatsApp), vacío si no aplica")
    motivo: str = Field(..., description="Motivo de la acción: id/nombre de regla aplicada o causa de no contacto")
