"""ETAPA 2 · Contenedores (C4 nivel 2).

EL CONCEPTO
Un contenedor es algo que se arranca y se para por separado: una aplicacion,
un servicio, una base de datos, una app movil. Si dos cajas siempre se
despliegan juntas, son UNA caja en este nivel.

Aqui si va la tecnologia, y tiene que ir: un contenedor sin tecnologia no se
puede desplegar. Y cada flecha dice por donde habla.

EL EXPERIMENTO
Lea otra vez el requisito 2 (el volumen se multiplica por cuarenta en
cosecha) y el 16 (un solo desarrollador, medio tiempo, sin equipo de
operaciones). Prediga, antes de dibujar, cuantos desplegables va a tener su
sistema. Despues cuente los del dibujo. Si le salieron muchos, relea el 16.
"""
import re

import pytest

from .apoyo import (PROTOCOLOS, bosquejo, diagrama, exige, opcion,
                    sin_tildes)

pytestmark = pytest.mark.etapa2
ARCHIVO = "etapa2-contenedores.mmd"
CLIENTE = ("tableta", "movil", "android", "app ", "celular", "navegador",
           "web ", "portal", "tablet")


def _d():
    return diagrama(ARCHIVO)


def _propios(d):
    return [n for n in d.nodos_de_subgrafo("cafetrace")]


def test_hay_bosquejo_a_mano():
    p = bosquejo(2)
    assert p is not None and p.stat().st_size > 15000, (
        "Falta BOSQUEJOS/etapa2.jpg legible.")


def test_estan_los_dos_subgrafos():
    d = _d()
    nombres = {sin_tildes(k) for k in d.subgrafos}
    assert "cafetrace" in nombres, (
        "Falta el subgrafo «cafetrace» con los contenedores propios. El "
        "limite del sistema tiene que verse: es la mitad del valor de este "
        "nivel.")
    assert any("extern" in n for n in nombres), (
        "Falta el subgrafo «externos». Lo de afuera va agrupado y separado.")


def test_cada_contenedor_propio_dice_su_tecnologia():
    d = _d()
    sin_tec = [n.etiqueta for n in _propios(d)
               if not re.search(r"\(.+\)", n.etiqueta)]
    assert not sin_tec, (
        f"Estos contenedores no dicen con que estan hechos: {sin_tec}. "
        f"Escriba la tecnologia entre parentesis, por ejemplo "
        f"«API de recibo (Python FastAPI)». Un contenedor sin tecnologia no "
        f"se despliega.")


def test_cada_flecha_dice_por_donde_habla():
    d = _d()
    malas = []
    for a in d.aristas:
        eti = sin_tildes(a.etiqueta)
        if not eti or not any(p in eti for p in PROTOCOLOS):
            malas.append(f"{a.de} -> {a.a} ({a.etiqueta or 'sin etiqueta'})")
    assert not malas, (
        f"Estas flechas no dicen el medio: {malas}. En el nivel 2 cada "
        f"flecha lleva protocolo o mecanismo: HTTPS/JSON, SQL, archivo "
        f"mensual, evento, cola. Ahi es donde despues se discute el "
        f"acoplamiento.")


def test_la_tableta_aparece_como_contenedor():
    d = _d()
    assert any(any(c in sin_tildes(n.etiqueta) for c in CLIENTE)
               for n in _propios(d)), (
        "No veo la tableta del recibidor entre los contenedores. Es la pieza "
        "donde ocurre el requisito 4: es la que no puede rechazar una "
        "entrega por falta de red, asi que es la que guarda y reintenta.")


def test_el_numero_de_desplegables_cuadra_con_la_decision():
    estilo = opcion("D2.1", ("monolito modular", "servicios", "hibrido"))
    d = _d()
    servidor = [n for n in _propios(d)
                if n.forma != "base_de_datos"
                and not any(c in sin_tildes(n.etiqueta) for c in CLIENTE)]
    cuantos = len(servidor)
    nombres = [n.etiqueta for n in servidor]
    if estilo == "monolito modular":
        assert cuantos == 1, (
            f"En D2.1 escogio monolito modular, que es UN desplegable de "
            f"servidor, pero dibujo {cuantos}: {nombres}. O el dibujo o la "
            f"decision estan mal; las dos cosas no pueden ser ciertas.")
    elif estilo == "servicios":
        assert cuantos >= 3, (
            f"En D2.1 escogio servicios, pero solo dibujo {cuantos} "
            f"desplegable(s) de servidor: {nombres}. Con menos de tres no "
            f"hay arquitectura de servicios que discutir.")
        just = sin_tildes(exige("D2.1")["justificacion"])
        assert "16" in just, (
            "Escogio servicios sin decir nada del requisito 16: un solo "
            "desarrollador, medio tiempo, sin equipo de operaciones. Puede "
            "escoger servicios, pero tiene que enfrentar ese requisito en la "
            "justificacion.")
    else:
        assert cuantos >= 2, (
            f"En D2.1 escogio hibrido y dibujo {cuantos} desplegable(s) de "
            f"servidor. Un hibrido necesita al menos dos.")


def test_el_contenedor_de_la_liquidacion_existe_en_el_dibujo():
    d = _d()
    nombrado = sin_tildes(exige("D2.2")["decision"])
    etiquetas = [sin_tildes(n.etiqueta) for n in _propios(d)]
    ok = any(nombrado and (nombrado in e or e in nombrado) for e in etiquetas)
    assert ok, (
        f"En D2.2 dijo que la liquidacion se calcula en "
        f"«{exige('D2.2')['decision'][:50]}», y ese contenedor no esta en el "
        f"diagrama. Los contenedores del dibujo son: {etiquetas}. El "
        f"documento y el dibujo tienen que hablar del mismo sistema.")


def test_d2_3_esta_respondida():
    opcion("D2.3", ("si", "no"))
