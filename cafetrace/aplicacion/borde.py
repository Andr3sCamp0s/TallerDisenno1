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

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from cafetrace.dominio.modelos import Entrega, Peso

class SolicitudEntrega(BaseModel):
    id_entrega: str = Field(..., min_length=1)
    cedula_productor: str = Field(..., min_length=9, max_length=9)
    kilos: Decimal = Field(..., gt=0, le=5000)
    humedad: Decimal = Field(..., ge=8, le=30)

    model_config = ConfigDict(
        extra="forbid",
        frozen=True)

    @field_validator("cedula_productor")
    @classmethod
    def validar_cedula_numerica(cls, v: str):
        if not v.isdigit():
            raise ValueError("La cédula del productor debe contener únicamente dígitos numéricos.")
        return v

    def a_entrega(self, recibida_en: datetime):
        return Entrega(
            id_entrega=self.id_entrega,
            cedula_productor=self.cedula_productor,
            peso=Peso(self.kilos),
            humedad=self.humedad,
            recibida_en=recibida_en)
