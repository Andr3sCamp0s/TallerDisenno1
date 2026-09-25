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

from .errores import ErrorDominio  # noqa: F401  (lo va a necesitar)

# TODO etapa 3
