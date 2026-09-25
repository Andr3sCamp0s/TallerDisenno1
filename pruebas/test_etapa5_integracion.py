"""ETAPA 5 · Integracion y lo que se rompe.

EL CONCEPTO
El requisito 3 dice que los patios se quedan sin senial. El 4 dice que la
tableta no puede rechazar la entrega. Los dos juntos significan una sola
cosa: la tableta va a guardar y reintentar, y usted va a recibir la misma
entrega mas de una vez.

Eso no se arregla pidiendole a la tableta que no reintente. Se arregla
haciendo que repetir la operacion no cambie el resultado. Se llama
idempotencia, y es el patron del que dependen todos los demas.

EL EXPERIMENTO
Antes de programar, escriba en D5.2 que deberia pasar cuando llega la misma
entrega dos veces. Hay tres respuestas posibles: un error, un duplicado, o el
mismo comprobante. Solo una deja dormir al recibidor.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import pytest

from .apoyo import bosquejo, diagrama, exige, modulo, sin_tildes

pytestmark = pytest.mark.etapa5
ARCHIVO = "etapa5-secuencia.mmd"
ESTILOS = ("archivo", "rpc", "mensajeria", "evento")


class RepositorioFalso:
    def __init__(self):
        self.lotes, self.entregas = {}, set()

    def guardar(self, lote):
        self.lotes[lote.id_lote] = lote
        self.entregas |= {e.id_entrega for e in lote.entregas}

    def por_id(self, id_lote):
        return self.lotes.get(id_lote)

    def entrega_registrada(self, id_entrega):
        return id_entrega in self.entregas


class RelojFijo:
    def __init__(self, cuando):
        self._cuando = cuando

    def ahora(self):
        return self._cuando


class BitacoraFalsa:
    def __init__(self):
        self.eventos = []

    def registrar(self, evento, **datos):
        self.eventos.append((evento, datos))


def _caso():
    b = modulo("cafetrace.aplicacion.borde")
    r = modulo("cafetrace.aplicacion.recibo")
    repo, reloj, bit = (RepositorioFalso(),
                        RelojFijo(datetime(2026, 11, 3, 8, 0)),
                        BitacoraFalsa())
    caso = r.RegistrarEntrega(repositorio=repo, reloj=reloj, bitacora=bit)
    sol = b.SolicitudEntrega(id_entrega="E-1", cedula_productor="102340567",
                             kilos=Decimal("120.5"), humedad=Decimal("11"))
    return caso, sol, repo, bit


def test_hay_bosquejo_a_mano():
    assert (bosquejo(5) is not None
            and bosquejo(5).stat().st_size > 15000), (
        "Falta BOSQUEJOS/etapa5.jpg legible.")


def test_el_borde_rechaza_lo_que_no_deberia_entrar():
    b = modulo("cafetrace.aplicacion.borde")
    from pydantic import ValidationError
    casos = [
        dict(id_entrega="", cedula_productor="102340567",
             kilos=Decimal("10"), humedad=Decimal("11")),
        dict(id_entrega="E-2", cedula_productor="12",
             kilos=Decimal("10"), humedad=Decimal("11")),
        dict(id_entrega="E-3", cedula_productor="102340567",
             kilos=Decimal("0"), humedad=Decimal("11")),
        dict(id_entrega="E-4", cedula_productor="102340567",
             kilos=Decimal("10"), humedad=Decimal("40")),
    ]
    for datos in casos:
        with pytest.raises(ValidationError):
            b.SolicitudEntrega(**datos)
    with pytest.raises(ValidationError):
        b.SolicitudEntrega(id_entrega="E-5", cedula_productor="102340567",
                           kilos=Decimal("10"), humedad=Decimal("11"),
                           sobra="esto no deberia pasar")


def test_la_misma_entrega_dos_veces_no_duplica_nada():
    caso, sol, repo, bit = _caso()
    primero = caso.ejecutar(sol, id_lote="L-1")
    segundo = caso.ejecutar(sol, id_lote="L-1")
    assert primero.duplicado is False, (
        "El primer comprobante viene marcado como duplicado.")
    assert segundo.duplicado is True, (
        "La segunda vez que llega la misma entrega, el comprobante debe "
        "venir con duplicado=True. No es un error: es el reintento normal de "
        "una tableta que estuvo sin red.")
    assert segundo.id_lote == primero.id_lote, (
        "El segundo comprobante apunta a otro lote. Reintentar no puede "
        "mover la entrega de lugar.")
    lote = repo.por_id("L-1")
    assert len(lote.entregas) == 1, (
        f"El lote quedo con {len(lote.entregas)} entregas despues de recibir "
        f"la misma dos veces. Eso es cafe cobrado dos veces al mismo "
        f"productor: el requisito 5 lo vuelve irreversible.")


def test_los_dos_intentos_dejan_rastro():
    caso, sol, repo, bit = _caso()
    caso.ejecutar(sol, id_lote="L-1")
    caso.ejecutar(sol, id_lote="L-1")
    assert len(bit.eventos) >= 2, (
        "Solo hay un evento en la bitacora despues de dos intentos. El "
        "reintento tambien se registra: sin eso, nadie puede explicar "
        "despues por que un comprobante salio dos veces.")


def test_la_fecha_del_comprobante_sale_del_reloj_inyectado():
    caso, sol, repo, bit = _caso()
    c = caso.ejecutar(sol, id_lote="L-1")
    assert c.emitido_en == datetime(2026, 11, 3, 8, 0), (
        "El comprobante no uso el reloj que se le inyecto. Si adentro se "
        "llama a datetime.now(), esta prueba deja de ser reproducible y "
        "usted no puede probar el comportamiento de una fecha concreta.")


def test_el_diagrama_de_secuencia_muestra_las_dos_ramas():
    d = diagrama(ARCHIVO)
    assert d.tipo == "sequenceDiagram", (
        "diagramas/etapa5-secuencia.mmd tiene que ser un sequenceDiagram.")
    assert len(d.participantes) >= 3, (
        f"Solo hay {len(d.participantes)} participantes y se piden tres.")
    etiquetas = sin_tildes(" ".join(d.participantes.values()))
    assert "tableta" in etiquetas, "Falta la tableta entre los participantes."
    assert len(d.mensajes) >= 4, (
        f"Solo hay {len(d.mensajes)} mensajes. Una ida y una vuelta no "
        f"cuentan la historia: falta la consulta y la rama del duplicado.")
    assert d.bloques & {"alt", "opt"}, (
        "El diagrama no tiene ningun bloque alt ni opt. La rama de «esta "
        "entrega ya habia llegado» es justamente lo que hay que dibujar: sin "
        "ella el diagrama cuenta el dia bueno, que es el que no da problemas.")


def test_d5_1_escoge_un_estilo_por_contraparte():
    d = exige("D5.1", minimo=220)
    bajo = sin_tildes(d["decision"] + " " + d["crudo"])
    for quien in ("icafe", "aduana", "tableta"):
        assert quien in bajo, f"D5.1 no dice nada sobre {quien}."
    hallados = [e for e in ESTILOS if e in bajo]
    assert len(hallados) >= 2, (
        f"D5.1 usa {hallados} y se esperan al menos dos estilos distintos "
        f"entre archivo, rpc, mensajeria y evento. Tres contrapartes tan "
        f"diferentes no se integran igual: el ICAFE no tiene API (requisito "
        f"6) y la aduana cambia sin avisar (requisito 7).")


def test_d5_2_describe_lo_que_de_verdad_implemento():
    exige("D5.2")


def test_escribio_sus_dos_pruebas():
    """Las suyas, no las mías. Una prueba que usted no escribió no le enseñó
    nada."""
    import ast

    from .apoyo import RAIZ

    archivos = [p for p in (RAIZ / "mis_pruebas").glob("*.py")
                if p.name != "conftest.py"]
    funciones, texto = [], ""
    for p in archivos:
        texto += p.read_text(encoding="utf-8", errors="replace")
        try:
            arbol = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:
            pytest.fail(f"mis_pruebas/{p.name} línea {e.lineno}: {e.msg}")
        funciones += [n.name for n in ast.walk(arbol)
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and n.name.startswith("test_")]
    assert len(funciones) >= 2, (
        f"Hay {len(funciones)} prueba(s) suya(s) en mis_pruebas/ y se piden "
        f"dos: la del reenvío que no duplica, y la del lote cerrado que no "
        f"acepta más entregas.")
    bajo = sin_tildes(texto)
    assert "loteyacerrado" in bajo, (
        "Ninguna de sus pruebas menciona LoteYaCerrado. La segunda prueba es "
        "esa: agregar una entrega a un lote cerrado tiene que levantar ese "
        "error, y es el requisito 5 hecho ejecutable.")
    assert "duplicado" in bajo or "dos veces" in bajo or "reintent" in bajo, (
        "Ninguna de sus pruebas parece ser la del reenvío. Registre la misma "
        "entrega dos veces y verifique que el lote queda con una sola.")
    assert "datetime.now" not in bajo, (
        "Alguna de sus pruebas llama a datetime.now(). Use un reloj doble: "
        "una prueba que depende de la hora real falla sola algún día.")
