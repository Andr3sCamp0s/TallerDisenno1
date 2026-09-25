"""El borde: donde se parsea lo que llega de afuera.

ETAPA 5.

  SolicitudEntrega   modelo de pydantic, con extra="forbid" y frozen=True.
                     Campos:
                       id_entrega: str, no vacio
                       cedula_productor: str, exactamente 9 digitos
                       kilos: Decimal, mayor que 0 y menor o igual a 5000
                       humedad: Decimal, entre 8 y 30 inclusive
                     .a_entrega(recibida_en) -> Entrega   traduce al dominio

Afuera nada es confiable: aqui se parsea, y el dato entra como un tipo valido
o no entra. Adentro ya no se vuelve a verificar lo mismo: eso seria codigo
paranoico, y la etapa 6 de la practica anterior lo penalizaba.
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# TODO etapa 5
