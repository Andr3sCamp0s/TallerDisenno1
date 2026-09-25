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

from decimal import Decimal, ROUND_HALF_UP
from cafetrace.dominio.modelos import Lote

KILOS_POR_QUINTAL = Decimal("46")

class ReglaNaranjo:
    cooperativa = "Naranjo"

    def liquidar(self, lote: Lote, precio_por_quintal: Decimal):
        quintales = lote.peso_total.kilos / KILOS_POR_QUINTAL
        humedad_promedio = sum(e.humedad for e in lote.entregas) / Decimal(len(lote.entregas))
        factor = Decimal("1.15") if humedad_promedio <= Decimal("11") else Decimal("1.0")
        bruto = precio_por_quintal * quintales * factor
        return bruto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class ReglaPalmares:
    cooperativa = "Palmares"

    def liquidar(self, lote: Lote, precio_por_quintal: Decimal):
        quintales = lote.peso_total.kilos / KILOS_POR_QUINTAL
        bruto = precio_por_quintal * quintales
        return bruto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class ReglaZarcero:
    cooperativa = "Zarcero"

    def liquidar(self, lote: Lote, precio_por_quintal: Decimal):
        quintales = lote.peso_total.kilos / KILOS_POR_QUINTAL
        bruto = precio_por_quintal * quintales
        neto = bruto - Decimal("25000")
        resultado = max(neto, Decimal("0"))
        return resultado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)