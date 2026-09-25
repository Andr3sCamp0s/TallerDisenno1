"""La liquidacion al productor, que cambia por cooperativa.

ETAPA 4. Aqui vive el requisito 8: cada cooperativa liquida distinto, y cada
una cambia su formula cuando quiere. Hoy son cinco y en tres anios seran diez.

Lo que las pruebas esperan:

  ReglaDeLiquidacion   Protocol con:
                         .cooperativa -> str
                         .liquidar(lote, precio_por_quintal) -> Decimal

  Liquidador           Se construye con un registro:
                         Liquidador(reglas)   donde reglas es un Mapping
                                              de nombre de cooperativa a regla
                       .liquidar(lote, precio_por_quintal) -> Decimal
                       Si la cooperativa del lote no esta en el registro,
                       levanta CooperativaNoRegistrada. NUNCA devuelve None.

Regla dura: en este archivo, y en todo el paquete dominio, no puede aparecer
el nombre de ninguna cooperativa. Si escribe `if cooperativa == "Naranjo"`,
la prueba de la etapa 4 se lo dice.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Mapping, Protocol, runtime_checkable

from cafetrace.dominio.modelos import Lote
from cafetrace.dominio.errores import CooperativaNoRegistrada

@runtime_checkable
class ReglaDeLiquidacion(Protocol):
    cooperativa: str
    def liquidar(self, lote: Lote, precio_por_quintal: Decimal): ...

class Liquidador:
    def __init__(self, reglas: Mapping[str, ReglaDeLiquidacion]):
        self._reglas = reglas

    def liquidar(self, lote: Lote, precio_por_quintal: Decimal):
        if lote.cooperativa not in self._reglas:
            raise CooperativaNoRegistrada(f"La cooperativa '{lote.cooperativa}' no está registrada.")
        
        regla = self._reglas[lote.cooperativa]
        return regla.liquidar(lote, precio_por_quintal)
