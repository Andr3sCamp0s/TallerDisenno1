"""ETAPA 6 · Registro de decisiones.

EL CONCEPTO
Un ADR es media pagina: contexto, decision, alternativas descartadas,
consecuencias y estado. La seccion que casi nadie escribe, y la unica que le
sirve a quien llegue despues, es la de alternativas descartadas: porque lo
que a esa persona se le va a ocurrir es exactamente lo que usted ya descarto.

EL EXPERIMENTO
Escriba los dos ADR y despues conteste D6.1 sin volver a abrir el codigo. Si
no puede decir cuantos archivos toca cada cambio, su arquitectura todavia no
esta en su cabeza, esta solo en la pantalla.
"""
import re
from pathlib import Path

import pytest

from .apoyo import RAIZ, exige, sin_tildes

pytestmark = pytest.mark.etapa6
SECCIONES = ("contexto", "decision", "alternativas descartadas",
             "consecuencias")


def _adrs():
    return sorted(p for p in (RAIZ / "ADR").glob("*.md")
                  if "titulo-de-su-decision" not in p.name)


def test_hay_al_menos_dos_registros_de_decision():
    a = _adrs()
    assert len(a) >= 2, (
        f"Hay {len(a)} ADR propios en ADR/ y se piden dos. Renombre la "
        f"plantilla: el nombre del archivo lleva el numero y el titulo, por "
        f"ejemplo 0001-cobro-sin-red.md")


@pytest.mark.parametrize("i", (0, 1))
def test_cada_adr_trae_sus_secciones(i):
    a = _adrs()
    if len(a) <= i:
        pytest.skip("todavia no existe este ADR")
    texto = sin_tildes(a[i].read_text(encoding="utf-8", errors="replace"))
    faltan = [s for s in SECCIONES if s not in texto]
    assert not faltan, f"A {a[i].name} le faltan las secciones: {faltan}"
    assert re.search(r"estado\s*:", texto), (
        f"{a[i].name} no dice su estado (propuesto, aceptado, sustituido).")
    assert re.search(r"\d{4}-\d{2}-\d{2}", texto), (
        f"{a[i].name} no tiene fecha. Un ADR sin fecha no se puede ordenar "
        f"en el tiempo, y el orden es la mitad de su valor.")


@pytest.mark.parametrize("i", (0, 1))
def test_cada_adr_descarta_algo_con_una_razon(i):
    a = _adrs()
    if len(a) <= i:
        pytest.skip("todavia no existe este ADR")
    texto = a[i].read_text(encoding="utf-8", errors="replace")
    bloque = re.split(r"(?i)##\s*alternativas descartadas", texto)
    assert len(bloque) > 1, "Falta la seccion de alternativas descartadas."
    cuerpo = re.split(r"^##\s", bloque[1], flags=re.M)[0]
    puntos = [l for l in cuerpo.splitlines()
              if l.strip().startswith(("-", "*")) and len(l.strip()) > 45]
    assert puntos, (
        f"En {a[i].name} la seccion de alternativas descartadas esta vacia o "
        f"es de una linea. Es la seccion que convierte el ADR en documento "
        f"de arquitectura y no en acta de reunion: nombre la alternativa y "
        f"diga con que numero la descarto.")
    assert "<" not in cuerpo, (
        f"{a[i].name} todavia trae los marcadores <...> de la plantilla.")


def test_un_adr_explica_una_decision_de_este_taller():
    a = _adrs()
    texto = sin_tildes(" ".join(p.read_text(encoding="utf-8",
                                            errors="replace") for p in a))
    pistas = ("cooperativa", "idempot", "monolito", "servicio", "tableta",
              "icafe", "aduana", "liquidacion", "offline", "sin red",
              "reintent", "contenedor", "puerto")
    assert any(p in texto for p in pistas), (
        "Ninguno de los ADR habla de una decision de CafeTrace. Los dos ADR "
        "documentan decisiones que usted tomo en este taller, no decisiones "
        "genericas.")


def test_d6_1_cuenta_los_archivos_de_cada_cambio():
    d = exige("D6.1", minimo=200)
    bajo = d["crudo"]
    for letra in ("a)", "b)", "c)"):
        assert letra in bajo, f"D6.1 no contesta el caso {letra}."
    assert re.search(r"\.py|\.md|\.mmd|archivo", d["crudo"], re.I), (
        "D6.1 no nombra ningun archivo. La prueba del cambio se contesta con "
        "rutas, no con adjetivos.")


def test_los_dos_conflictos_estan_escritos():
    from .apoyo import texto_de
    t = texto_de("DECISIONES.md")
    cierre = t.split("## Cierre")[-1]
    uno = re.search(r"\*\*Conflicto 1:\*\*(.*?)(?=\*\*Conflicto 2|\Z)",
                    cierre, re.S)
    dos = re.search(r"\*\*Conflicto 2:\*\*(.*)", cierre, re.S)
    for n, m in ((1, uno), (2, dos)):
        cuerpo = " ".join(m.group(1).split()) if m else ""
        assert len(cuerpo) > 150, (
            f"El conflicto {n} del cierre tiene {len(cuerpo)} caracteres. "
            f"Cuente que pedia cada lado, cual cedio y por que: son las "
            f"tensiones las que ensenian que no hay disenio gratis.")
