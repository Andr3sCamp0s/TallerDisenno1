"""ETAPA 1 · Contexto (C4 nivel 1).

EL CONCEPTO
El nivel 1 dibuja el sistema como una caja negra y todo lo que lo rodea. Es
la lamina que se le ensenia a un gerente el primer dia. No lleva ni una
tecnologia: ni base de datos, ni protocolo, ni lenguaje. Si aparece
«PostgreSQL», usted ya se fue al nivel 2 sin darse cuenta.

La pregunta que resuelve este nivel es una sola: que esta adentro y que esta
afuera. Suena trivial y no lo es, porque de ahi sale quien manda sobre cada
pieza.

EL EXPERIMENTO
Antes de dibujar, escriba cuantas cosas cree que van afuera. Despues cuente
las de su diagrama. Casi todo el mundo se queda corto, y casi siempre olvida
la misma: el que audita.
"""
import pytest

from .apoyo import TECNOLOGIA, bosquejo, diagrama, opcion, sin_tildes

pytestmark = pytest.mark.etapa1
ARCHIVO = "etapa1-contexto.mmd"


def _d():
    return diagrama(ARCHIVO)


def test_hay_bosquejo_a_mano():
    p = bosquejo(1)
    assert p is not None, (
        "Falta BOSQUEJOS/etapa1.jpg (o .png). Dibuje primero a mano y tome "
        "la foto: a mano se disenia, en Mermaid solo se transcribe.")
    assert p.stat().st_size > 15000, (
        f"{p.name} pesa {p.stat().st_size} bytes. Parece una imagen vacia o "
        f"recortada; tiene que leerse el nombre de las cajas.")


def test_hay_exactamente_un_sistema():
    d = _d()
    assert "sistema" in d.nodos, (
        "No encuentro el nodo con identificador «sistema». El nivel 1 tiene "
        "una sola caja negra y tiene que llamarse asi para poder revisarla.")


def test_hay_al_menos_cinco_cosas_afuera_y_todas_conectadas():
    d = _d()
    externos = [n for n in d.nodos if n != "sistema"]
    assert len(externos) >= 5, (
        f"Dibujo {len(externos)} elementos externos y en este caso hay al "
        f"menos cinco. Repase el caso: quien entrega, quien liquida, quien "
        f"audita, quien exige el archivo mensual, quien publica el precio, "
        f"quien consulta desde el puerto.")
    sueltos = [n for n in externos
               if not any((a.de == n and a.a == "sistema")
                          or (a.a == n and a.de == "sistema")
                          for a in d.aristas)]
    assert not sueltos, (
        f"Estos elementos no estan conectados al sistema: {sueltos}. En el "
        f"nivel 1 todo lo de afuera existe porque interactua con el sistema; "
        f"si algo no lo toca, no va en el dibujo.")


def test_toda_flecha_dice_que_pasa_por_ella():
    d = _d()
    mudas = [f"{a.de} -> {a.a}" for a in d.sin_etiqueta()]
    assert not mudas, (
        f"Estas flechas no dicen nada: {mudas}. Una flecha sin verbo no se "
        f"puede revisar: «entrega fruta», «exige el reporte mensual», "
        f"«consulta el estado del contenedor».")


def test_el_nivel_1_no_lleva_tecnologia():
    d = _d()
    texto = sin_tildes(" ".join([n.etiqueta for n in d.nodos.values()]
                                + [a.etiqueta for a in d.aristas]))
    encontradas = sorted({t for t in TECNOLOGIA if t in texto})
    assert not encontradas, (
        f"En el nivel 1 aparece tecnologia: {encontradas}. Ese es el nivel "
        f"2. Aqui solo van el sistema y su entorno, en el idioma del "
        f"negocio.")


def test_la_decision_sobre_la_tableta_cuadra_con_el_dibujo():
    resp = opcion("D1.2", ("externo", "parte"))
    d = _d()
    hay_tableta = any("tableta" in sin_tildes(n.etiqueta)
                      or "tablet" in sin_tildes(n.etiqueta)
                      for nid, n in d.nodos.items() if nid != "sistema")
    if resp == "parte":
        assert not hay_tableta, (
            "En D1.2 dijo que la tableta es PARTE del sistema, pero la "
            "dibujo como un elemento externo. Si es suya, la despliega usted "
            "y va adentro: aparecera en el nivel 2 como contenedor.")
    else:
        assert hay_tableta, (
            "En D1.2 dijo que la tableta es un actor EXTERNO, pero no "
            "aparece en el diagrama. Si es externa, alguien mas la programa "
            "y tiene que verse en el contexto.")


def test_d1_1_esta_respondida():
    opcion("D1.1", ("dentro", "fuera"))
