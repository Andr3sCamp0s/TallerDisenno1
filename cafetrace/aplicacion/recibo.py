"""Registrar una entrega. El caso de uso central del taller.

ETAPA 5.

  Comprobante        dataclass con: id_entrega, id_lote, emitido_en, duplicado
                     `duplicado` dice si esta entrega ya habia llegado antes.

  RegistrarEntrega   Se construye SOLO por constructor, con estos nombres
                     exactos:
                         RegistrarEntrega(repositorio, reloj, bitacora)

                     .ejecutar(solicitud, id_lote) -> Comprobante

                     Tiene que ser IDEMPOTENTE por id_entrega: si la misma
                     entrega llega dos veces, la segunda NO agrega nada al
                     lote y devuelve un comprobante con duplicado=True y el
                     mismo id_lote. No es un error: es el caso normal cuando
                     la tableta reintenta despues de estar sin red.

                     Deja rastro en la bitacora en los dos casos.

Por que importa: el requisito 3 dice que los patios se quedan sin senial, y
el 4 dice que la tableta no puede rechazar la entrega. Las dos cosas juntas
significan que la tableta va a guardar y reintentar, y que usted va a recibir
la misma entrega mas de una vez. Eso no se arregla pidiendole a la tableta
que no reintente.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# TODO etapa 5
