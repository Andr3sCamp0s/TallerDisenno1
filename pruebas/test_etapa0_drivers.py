"""ETAPA 0 · Del caso a los drivers.

EL CONCEPTO
Una arquitectura no se decide leyendo un enunciado: se decide leyendo los
drivers. Un driver es un requisito que dobla la estructura. Los demás
requisitos se implementan; los drivers se diseñan alrededor.

Tres tipos, y conviene no confundirlos:
  · atributo de calidad (QA): dice QUÉ TAN BIEN, y trae medida.
  · restricción (R): no se negocia, se acata.
  · funcional (F): dice QUÉ HACE. Casi nunca cambia la arquitectura.

EL EXPERIMENTO
Antes de llenar la tabla, escriba en un papel cuántos de los dieciocho cree
usted que son atributos de calidad. Luego clasifíquelos y cuente. Casi todo
el mundo predice de más en funcionales y de menos en calidad; la diferencia
entre su número y el real es lo que acaba de aprender sobre su propio ojo.
"""
import re

import pytest

from .apoyo import exige, sin_tildes, texto_de

pytestmark = pytest.mark.etapa0

FILA = re.compile(r"^\|\s*(\d{1,2})\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", re.M)
PARTES = ("fuente", "estimulo", "artefacto", "entorno", "respuesta", "medida")
DEGRADADO = ("sin red", "sin senial", "sin señal", "caida", "caída", "pico",
             "cosecha alta", "degradado", "no responde", "fuera de linea",
             "offline", "sin conectividad", "saturad")


def _filas():
    texto = texto_de("DRIVERS.md")
    if not texto:
        pytest.fail("Falta DRIVERS.md, o está vacío.")
    parte1 = texto.split("Parte 2")[0]      # la tabla de los dieciocho
    return {int(m.group(1)): [c.strip() for c in m.groups()[1:]]
            for m in FILA.finditer(parte1)}


def test_los_dieciocho_requisitos_estan_clasificados():
    filas = _filas()
    faltan = [n for n in range(1, 19) if n not in filas]
    assert not faltan, (
        f"En DRIVERS.md faltan los requisitos {faltan}. Son dieciocho y van "
        f"todos: clasificar tambien es decidir que algo NO es un driver.")
    sin_tipo = [n for n, c in filas.items()
                if sin_tildes(c[0]).strip().upper() not in ("QA", "R", "F")]
    assert not sin_tipo, (
        f"Los requisitos {sorted(sin_tipo)} no tienen tipo, o tienen uno que "
        f"no es QA, R ni F.")


def test_los_atributos_de_calidad_traen_medida():
    filas = _filas()
    qa = {n: c for n, c in filas.items() if c[0].strip().upper() == "QA"}
    assert len(qa) >= 5, (
        f"Marco {len(qa)} atributos de calidad y en este caso hay al menos "
        f"cinco. Vuelva sobre los requisitos 2, 3, 4, 8, 10, 11 y 13: casi "
        f"todos dicen «que tan bien», no «que hace».")
    sin_medida = [n for n, c in qa.items() if not re.search(r"\d", c[2])]
    assert not sin_medida, (
        f"Los atributos de calidad {sorted(sin_medida)} no traen medida. Un "
        f"atributo sin numero no se puede verificar, y entonces no se puede "
        f"disenar para el: «rapido» no es un requisito, «300 ms» si.")


def test_estan_los_seis_que_mandan():
    texto = texto_de("DRIVERS.md")
    bloque = texto.split("Parte 2")[-1].split("Parte 3")[0]
    filas = [l for l in bloque.splitlines()
             if l.strip().startswith("|") and re.search(r"\|\s*[1-6]\s*\|", l)]
    llenas = [l for l in filas if len(l.split("|")[4].strip()) > 25]
    assert len(llenas) >= 6, (
        f"La tabla de «los seis que mandan» tiene {len(llenas)} filas con "
        f"explicacion y se piden seis. Ordenarlos importa: el primero es el "
        f"que va a decidir los cortes.")


def test_hay_tres_escenarios_con_sus_seis_partes():
    texto = sin_tildes(texto_de("DRIVERS.md"))
    bloque = texto.split("parte 3")[-1]
    escenarios = re.split(r"###\s*escenario", bloque)[1:]
    assert len(escenarios) >= 3, (
        f"Encontre {len(escenarios)} escenarios y se piden tres.")
    for i, e in enumerate(escenarios[:3], 1):
        faltan = [p for p in PARTES if p not in e]
        assert not faltan, (
            f"Al escenario {i} le faltan estas partes: {faltan}. Las seis "
            f"son obligatorias; sin entorno y sin medida, un escenario es un "
            f"deseo.")
        cuerpo = re.sub(r"\*\*[^*]*\*\*:?", " ", e)
        assert len(" ".join(cuerpo.split())) > 120, (
            f"El escenario {i} esta casi vacio: tiene los rotulos pero no el "
            f"contenido.")


def test_al_menos_un_escenario_ocurre_en_entorno_degradado():
    texto = sin_tildes(texto_de("DRIVERS.md"))
    # solo los escenarios: el enunciado de la Parte 3 ya nombra ejemplos
    bloque = " ".join(re.split(r"###\s*escenario", texto)[1:])
    assert any(d in bloque for d in DEGRADADO), (
        "Ninguno de los tres escenarios ocurre en entorno degradado. En "
        "CafeTrace eso es medio caso: el requisito 3 dice que los patios se "
        "quedan sin senial y el 2 dice que en cosecha el volumen se "
        "multiplica por cuarenta. Un escenario en el dia soleado no obliga a "
        "decidir nada de arquitectura.")


def test_d0_1_nombra_el_driver_dominante():
    d = exige("D0.1")
    assert re.search(r"\d", d["decision"]), (
        "D0.1 debe nombrar UN requisito por su numero. Escriba por ejemplo "
        "«requisito 4» en la linea de Decision.")


def test_d0_2_nombra_los_dos_que_se_contradicen():
    d = exige("D0.2", minimo=220)
    numeros = re.findall(r"\d{1,2}", d["decision"])
    assert len(numeros) >= 2, (
        "D0.2 debe nombrar DOS requisitos por su numero en la linea de "
        "Decision.")
    bajo = sin_tildes(d["justificacion"])
    assert any(p in bajo for p in ("cede", "cedio", "sacrific", "renunci",
                                   "prioriza", "se pierde", "gana")), (
        "La justificacion de D0.2 no dice cual de los dos cede. Encontrar la "
        "contradiccion es la mitad; la otra mitad es decidir, y decir que se "
        "pierde con esa decision.")
