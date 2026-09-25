"""El registro de reglas de liquidacion.

ETAPA 4.

  construir_registro(reglas) -> Mapping[str, ReglaDeLiquidacion]

Recibe un iterable de reglas y devuelve un mapa indexado por
`regla.cooperativa`. Si llegan dos reglas para la misma cooperativa,
levanta ValueError: un duplicado silencioso es un error que aparece meses
despues, en la liquidacion equivocada.

Este archivo es infraestructura a proposito: es el unico que sabe cuales
cooperativas existen hoy.
"""
from __future__ import annotations

from typing import Iterable, Mapping
from cafetrace.dominio.liquidacion import ReglaDeLiquidacion

def construir_registro(reglas: Iterable[ReglaDeLiquidacion]) -> Mapping[str, ReglaDeLiquidacion]:
    mapa = {}
    for regla in reglas:
        nombre = regla.cooperativa
        if nombre in mapa:
            raise ValueError(f"Regla duplicada para la cooperativa: {nombre}")
        mapa[nombre] = regla
    return mapa
