"""Lo que el dominio NECESITA del mundo, dicho en su propio idioma.

ETAPA 3.

Cuatro Protocol, con estos nombres exactos:

  RepositorioDeLotes   .guardar(lote) -> None
                       .por_id(id_lote) -> Lote | None
                       .entrega_registrada(id_entrega) -> bool

  Reloj                .ahora() -> datetime

  PrecioDelDia         .por_quintal() -> Decimal

  Bitacora             .registrar(evento, **datos) -> None

Fijese en los nombres: son del negocio, no del mecanismo. Se llama
`por_quintal`, no `get_price`; se llama `guardar`, no `insert`. El dia que
cambie el proveedor, el dominio no se entera.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol, runtime_checkable, Any
from cafetrace.dominio.modelos import Lote

@runtime_checkable
class RepositorioDeLotes(Protocol):
    def guardar(self, lote: Lote): ...
    def por_id(self, id_lote: str): ...
    def entrega_registrada(self, id_entrega: str): ...

@runtime_checkable
class Reloj(Protocol):
    def ahora(self): ...

@runtime_checkable
class PrecioDelDia(Protocol):
    def por_quintal(self): ...

@runtime_checkable
class Bitacora(Protocol):
    def registrar(self, evento: str, **datos: Any): ...
