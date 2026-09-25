"""Tipos del negocio. Todos inmutables.

ETAPA 3.

Lo que las pruebas esperan:

  Peso          Tiene .kilos (Decimal). Construirlo con cero o con un
                negativo levanta EntregaInvalida. Es un tipo propio, no un
                alias de float: la decision D3.1 tiene que cuadrar con esto.

  Entrega       id_entrega: str, cedula_productor: str, peso: Peso,
                humedad: Decimal, recibida_en: datetime.
                Inmutable (frozen).

  Lote          id_lote: str, cooperativa: str, entregas: tuple[Entrega, ...],
                cerrado: bool = False.
                .peso_total -> Peso   (suma de las entregas)
                .agregar(entrega) -> Lote   devuelve un Lote NUEVO
                .cerrar() -> Lote           devuelve un Lote NUEVO, cerrado
                Agregar a un lote cerrado levanta LoteYaCerrado. Ese es el
                requisito 5, y es la razon de que estas clases sean frozen.

No importe aqui datetime.now, ni requests, ni psycopg. Si necesita la hora,
pidasela al puerto Reloj.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .errores import ErrorDominio, EntregaInvalida, LoteYaCerrado  # noqa: F401  (lo va a necesitar)

@dataclass(frozen=True)
class Peso:
    kilos: Decimal

    def __init__(self, kilos: Decimal):
        if kilos <= Decimal("0"):
            raise EntregaInvalida("El peso debe ser mayor a cero.")
        object.__setattr__(self, "kilos", kilos)

@dataclass(frozen=True)
class Entrega:
    id_entrega: str
    cedula_productor: str
    peso: Peso
    humedad: Decimal
    recibida_en: datetime

@dataclass(frozen=True)
class Lote:
    id_lote: str
    cooperativa: str
    entregas: tuple[Entrega, ...] = ()
    cerrado: bool = False

    @property
    def peso_total(self):
        if not self.entregas:
            return Peso(Decimal("0.0001"))
        total = sum((e.peso.kilos for e in self.entregas), Decimal("0"))
        return Peso(total)

    def agregar(self, entrega: Entrega):
        if self.cerrado:
            raise LoteYaCerrado("Lote cerrado.")
        return Lote(
            id_lote=self.id_lote,
            cooperativa=self.cooperativa,
            entregas=self.entregas + (entrega,),
            cerrado=self.cerrado)

    def cerrar(self) -> Lote:
        return Lote(
            id_lote=self.id_lote,
            cooperativa=self.cooperativa,
            entregas=self.entregas,
            cerrado=True)
