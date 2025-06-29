# app/filter_engine.py
"""
Lógica principal para el filtrado de citas médicas según reglas de negocio dinámicas (mini-DSL).

Provee:
- Evaluación de condiciones lógicas sobre objetos de citas.
- Aplicación de acciones definidas externamente para decidir el contacto a pacientes.
"""
from app.models import Cita, ResultadoFiltro
from typing import List, Dict, Any
from datetime import datetime, timezone
import operator
import json

# Diccionario de operadores admitidos en el DSL
OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b
}

def calcular_dias_antes(fecha_cita: datetime) -> int:
    """
    Calcula los días de anticipación entre la fecha actual y la cita.

    @param fecha_cita: Fecha y hora de la cita (con zona horaria).
    @return: Número de días hasta la cita.
    """
    ahora = datetime.now(timezone.utc).astimezone(fecha_cita.tzinfo)
    diff = (fecha_cita.date() - ahora.date()).days
    return diff

def eval_condicion(cita: Cita, condicion: Dict[str, Any]) -> bool:
    """
    Evalúa una condición lógica simple o compuesta sobre una cita.

    @param cita: Instancia de Cita.
    @param condicion: Estructura dict: puede ser cond compuesta (and/or/not) o simple.
    @return: True si se cumple la condición.
    @raises: ValueError si operador no es soportado.
    """
    # Lógica compuesta (soporte para anidamiento)
    if "and" in condicion:
        return all(eval_condicion(cita, c) for c in condicion["and"])
    if "or" in condicion:
        return any(eval_condicion(cita, c) for c in condicion["or"])
    if "not" in condicion:
        return not all(eval_condicion(cita, c) for c in condicion["not"])

    # Lógica simple
    campo = condicion["campo"]
    operador_str = condicion["operador"]
    valor = condicion["valor"]

    # Permite campos calculados (ej: días_antes)
    if campo == "dias_antes":
        left = calcular_dias_antes(cita.fecha_cita)
    else:
        left = getattr(cita, campo)
        if isinstance(left, str):
            left = left.lower()
        if isinstance(valor, str):
            valor = valor.lower()

    if operador_str in OPERATORS:
        return OPERATORS[operador_str](left, valor)
    raise ValueError(f"Operador no soportado: {operador_str}")

def filtrar_citas(citas: List[Cita], reglas: List[Dict[str, Any]]) -> List[ResultadoFiltro]:
    """
    Filtra citas médicas según reglas mini-DSL externas,
    Cada cita será evaluada contra las reglas en orden, soportando exclusión prioritaria
    Se reporta el motivo del resultado (id/nombre de la regla aplicada o ausencia de coincidencia)
    
    @param citas: Lista de instancias Cita.
    @param reglas: Lista de reglas en mini-DSL (dict).
    @return: Lista de objetos ResultadoFiltro.
    """
    resultados: List[ResultadoFiltro] = []

    for cita in citas:
        accion_aplicada = False
        for regla in reglas:
            if eval_condicion(cita, regla["condiciones"]):
                accion = regla["accion"]
                motivo = regla.get("nombre") or regla.get("id") or "Regla aplicada"

                # Regla de exclusión: prioridad absoluta, no se evalúan más reglas
                if accion["tipo"] == "excluir":
                    resultados.append(ResultadoFiltro(
                        paciente=cita.nombre_paciente,
                        fecha_cita=cita.fecha_cita,
                        accion="excluir",
                        via=None,
                        motivo=f"Exclusión por {motivo}"
                    ))
                    accion_aplicada = True
                    break

                # Si no se ha aplicado una acción aún, se aplica la regla actual
                if not accion_aplicada:
                    resultados.append(ResultadoFiltro(
                        paciente=cita.nombre_paciente,
                        fecha_cita=cita.fecha_cita,
                        accion=accion["tipo"],
                        via=accion.get("via", None),
                        motivo=f"Por {motivo}"
                    ))
                    accion_aplicada = True  # Evita doble contacto
        # Si ninguna regla aplicó, se declara explícitamente que NO se debe contactar
        if not accion_aplicada:
            resultados.append(ResultadoFiltro(
                paciente=cita.nombre_paciente,
                fecha_cita=cita.fecha_cita,
                accion="excluir",
                via=None,
                motivo="Sin regla aplicable"
            ))
    return resultados

def cargar_reglas(path: str) -> List[Dict[str, Any]]:
    """
    Carga reglas desde un archivo JSON con mini-DSL.

    @param path: Ruta al archivo.
    @return: Lista de reglas.
    @raises: Exception si hay error de lectura o formato.
    """
    try:
        with open(path, encoding="utf-8") as f:
            reglas = json.load(f)
            if not isinstance(reglas, list):
                raise ValueError("El archivo de reglas debe contener una lista de reglas")
            return reglas
    except Exception as e:
        raise RuntimeError(f"Error cargando reglas desde {path}: {e}")