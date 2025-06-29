# app/tests/test_filter_engine.py
"""
Tests automáticos para el motor de filtrado de citas médicas (filtro_citas).

Verifica el correcto funcionamiento para cada una de las reglas de negocio propuestas
por el desafío Cero, cubriendo tanto casos positivos (debe contactar) como negativos
(no debe contactar o debe excluir).
"""

from datetime import datetime, timedelta, timezone
from app.models import Cita
from app.filter_engine import filtrar_citas, cargar_reglas
from typing import Literal
import sys
import os
# Asegurar que el directorio raíz del proyecto esté en el path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Fecha base fija para todos los tests (Chile invierno UTC-4)
NOW = datetime(2025, 6, 28, 9, 0, 0, tzinfo=timezone(timedelta(hours=-4)))

def cita_relativa(
    dias_offset: int,
    especialidad: str = "cardiología",
    tipo_atencion: Literal["primera vez", "control"] = "primera vez",
    edad: int = 30,
    estado_cita: Literal["agendada", "confirmada", "espera"] = "confirmada",
    rut_profesional: str = "12345678-1",
    nombre_paciente: str = "Paciente Test"
    ) -> Cita:
    """
    Crea una cita válida para el modelo, controlando el dominio de los valores con Literal.
    """
    # Normalizar y validar los dominios
    if tipo_atencion not in {"primera vez", "control"}:
        raise ValueError(f"tipo_atencion no válido: {tipo_atencion}")
    if estado_cita not in {"agendada", "confirmada", "espera"}:
        raise ValueError(f"estado_cita no válido: {estado_cita}")
    
    return Cita(
        fecha_cita = NOW + timedelta(days=dias_offset),
        especialidad = especialidad,
        tipo_atencion = tipo_atencion,
        edad = edad,
        estado_cita = estado_cita,
        rut_profesional = rut_profesional,
        nombre_paciente = nombre_paciente
    )

def test_regla_1():
    """
    Regla 1: Notificar pacientes de cardiología 2 días antes, solo primera vez.
    """
    reglas = cargar_reglas("app/rules/rules.json")
    # Caso positivo: cumple todos los requisitos
    cita_ok = cita_relativa(2, especialidad="cardiología", tipo_atencion="primera vez", nombre_paciente="Positivo R1")
    # Caso negativo: es control, no primera vez
    cita_fail = cita_relativa(2, especialidad="cardiología", tipo_atencion="control", nombre_paciente="Negativo R1")
    resultados = filtrar_citas([cita_ok, cita_fail], reglas, now=NOW)
    assert any(r.paciente == "Positivo R1" and r.accion == "contactar" for r in resultados)
    assert any(r.paciente == "Negativo R1" and r.accion != "contactar" for r in resultados)

def test_regla_2():
    """
    Regla 2: Contactar pacientes del Dr. Martínez 1 día antes, excepto tercera edad.
    """
    reglas = cargar_reglas("app/rules/rules.json")
    # Caso positivo: Dr. Martínez, menor de 65 años
    cita_ok = cita_relativa(1, rut_profesional="9111666-9", edad=40, nombre_paciente="Positivo R2")
    # Caso negativo: Dr. Martínez, tercera edad
    cita_fail = cita_relativa(1, rut_profesional="9111666-9", edad=68, nombre_paciente="Negativo R2")
    resultados = filtrar_citas([cita_ok, cita_fail], reglas, now=NOW)
    assert any(r.paciente == "Positivo R2" and r.accion == "contactar" for r in resultados)
    assert any(r.paciente == "Negativo R2" and r.accion != "contactar" for r in resultados)

def test_regla_3():
    """
    Regla 3: Contactar solo controles pediátricos agendados.
    """
    reglas = cargar_reglas("app/rules/rules.json")
    # Caso positivo: pediatría, control, agendada
    cita_ok = cita_relativa(3, especialidad="pediatría", tipo_atencion="control", estado_cita="agendada", nombre_paciente="Positivo R3")
    # Caso negativo: pediatría, control, espera
    cita_fail = cita_relativa(3, especialidad="pediatría", tipo_atencion="control", estado_cita="espera", nombre_paciente="Negativo R3")
    resultados = filtrar_citas([cita_ok, cita_fail], reglas, now=NOW)
    assert any(r.paciente == "Positivo R3" and r.accion == "contactar" for r in resultados)
    assert any(r.paciente == "Negativo R3" and r.accion != "contactar" for r in resultados)

def test_regla_4():
    """
    Regla 4: Excluir completamente pacientes de la Dra. Gómez (RUT 15678432-9).
    """
    reglas = cargar_reglas("app/rules/rules.json")
    # Caso negativo: Dra. Gómez, debe ser excluido
    cita_fail = cita_relativa(2, rut_profesional="15678432-9", nombre_paciente="Negativo R4")
    # Caso positivo: otro médico
    cita_ok = cita_relativa(2, rut_profesional="00000000-0", nombre_paciente="Positivo R4")
    resultados = filtrar_citas([cita_fail, cita_ok], reglas, now=NOW)
    assert any(r.paciente == "Negativo R4" and r.accion == "excluir" for r in resultados)
    assert any(r.paciente == "Positivo R4" and r.accion == "contactar" for r in resultados)

def test_regla_5():
    """
    Regla 5: Pacientes de cardiología deben recibir dos mensajes (5 días antes y el mismo día).
    """
    reglas = cargar_reglas("app/rules/rules.json")
    # Caso positivo: 5 días antes (cualquier tipo_atencion)
    cita_ok_5 = cita_relativa(5, especialidad="cardiología", tipo_atencion="control", nombre_paciente="Positivo R5_5")
    # Caso positivo: mismo día (cualquier tipo_atencion)
    cita_ok_0 = cita_relativa(0, especialidad="cardiología", tipo_atencion="primera vez", nombre_paciente="Positivo R5_0")
    # Caso negativo: otro día y otra especialidad
    cita_fail = cita_relativa(4, especialidad="urología", nombre_paciente="Negativo R5")
    resultados = filtrar_citas([cita_ok_5, cita_ok_0, cita_fail], reglas, now=NOW)
    assert any(r.paciente == "Positivo R5_5" and r.accion == "contactar" for r in resultados)
    assert any(r.paciente == "Positivo R5_0" and r.accion == "contactar" for r in resultados)
    assert any(r.paciente == "Negativo R5" and r.accion != "contactar" for r in resultados)
    