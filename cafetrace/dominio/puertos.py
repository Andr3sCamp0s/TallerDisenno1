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

from typing import Protocol, runtime_checkable

# TODO etapa 3
