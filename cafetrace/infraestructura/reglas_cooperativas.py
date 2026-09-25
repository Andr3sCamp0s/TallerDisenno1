"""Las reglas de las cooperativas que existen hoy.

ETAPA 4. Escriba tres, con estos nombres de cooperativa exactos:

  "Naranjo"    paga por calidad: precio_por_quintal x quintales x factor,
               donde el factor es 1.15 si la humedad promedio del lote es
               menor o igual a 11, y 1.0 si no.
  "Palmares"   paga por peso, sin ajustes: precio_por_quintal x quintales.
  "Zarcero"    paga por peso y descuenta un adelanto fijo de 25 000 colones
               por lote. Nunca liquida menos de cero.

Un quintal son 46 kilos. Use Decimal en todo el camino: el dinero nunca es
float. Redondee a dos decimales al final, no antes.

Cada regla es una clase con `.cooperativa` y `.liquidar(lote, precio)`.
"""
from __future__ import annotations

from decimal import Decimal

KILOS_POR_QUINTAL = Decimal("46")

# TODO etapa 4
