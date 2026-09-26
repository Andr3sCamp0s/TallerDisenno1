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
from cafetrace.dominio.puertos import RepositorioDeLotes, Reloj, Bitacora
from cafetrace.dominio.modelos import Lote, Entrega, Peso
from cafetrace.aplicacion.borde import SolicitudEntrega

@dataclass
class Comprobante:
    id_entrega: str
    id_lote: str
    emitido_en: datetime
    duplicado: bool

class RegistrarEntrega:
    def __init__(self, repositorio: RepositorioDeLotes, reloj: Reloj, bitacora: Bitacora):
        self.repositorio = repositorio
        self.reloj = reloj
        self.bitacora = bitacora

    def ejecutar(self, solicitud: SolicitudEntrega, id_lote: str) -> Comprobante:
        # Registra la actividad siempre en la bitácora
        self.bitacora.registrar("intento_registro_recibo", id_entrega=solicitud.id_entrega, id_lote=id_lote)
        ahora = self.reloj.ahora()

        #Si la entrega ya existía, devolvemos el duplicado=True sin alterar nada
        if self.repositorio.entrega_registrada(solicitud.id_entrega):
            return Comprobante(
                id_entrega=solicitud.id_entrega,
                id_lote=id_lote,
                emitido_en=ahora,
                duplicado=True
            )

        #Buscamos el lote. Si no existe, lo creamos desde cero
        lote = self.repositorio.por_id(id_lote)
        if lote is None:
            lote = Lote(id_lote=id_lote, cooperativa="General", entregas=())

        #Creamos la entrega y la asociamos al lote
        nueva_entrega = solicitud.a_entrega(recibida_en=ahora)
        lote_actualizado = lote.agregar(nueva_entrega)
        
        #Guardamos el lote actualizado en el repositorio
        self.repositorio.guardar(lote_actualizado)

        return Comprobante(
            id_entrega=solicitud.id_entrega,
            id_lote=id_lote,
            emitido_en=ahora,
            duplicado=False
        )
