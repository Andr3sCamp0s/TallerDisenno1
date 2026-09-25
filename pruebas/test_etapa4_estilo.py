"""ETAPA 4 · Estilo arquitectonico y extensibilidad.

EL CONCEPTO
Un estilo arquitectonico no es una receta: es un vocabulario mas un conjunto
de restricciones. Lo que lo hace util no es lo que permite, es lo que
prohibe.

Aqui la prohibicion es concreta: el nucleo no puede saber como se llaman las
cooperativas. El requisito 8 dice que cada una liquida distinto y cambia su
formula cuando quiere; el 9 dice que van a ser el doble. Si el nombre de una
cooperativa aparece en el dominio, cada cooperativa nueva le toca el corazon
del sistema.

EL EXPERIMENTO
Esta prueba registra una SEXTA cooperativa que usted nunca escribio, desde
afuera, y le pide liquidar con ella. Prediga que va a pasar. Si su disenio
esta bien, funciona sin que usted toque una linea. Si queda un condicional,
falla.
"""
from decimal import Decimal

import pytest

from .apoyo import exige, fuente_del_paquete, modulo, sin_tildes

pytestmark = pytest.mark.etapa4
COOPERATIVAS = ("naranjo", "palmares", "zarcero")


def _lote(coop="Palmares", kilos="460", humedad="10"):
    m = modulo("cafetrace.dominio.modelos")
    from datetime import datetime
    e = m.Entrega(id_entrega="E-1", cedula_productor="102340567",
                  peso=m.Peso(Decimal(kilos)), humedad=Decimal(humedad),
                  recibida_en=datetime(2026, 11, 3, 8, 0))
    return m.Lote(id_lote="L-1", cooperativa=coop, entregas=(e,))


def test_el_dominio_no_sabe_como_se_llaman_las_cooperativas():
    malos = []
    for ruta, src in fuente_del_paquete("dominio").items():
        bajo = sin_tildes(src)
        for c in COOPERATIVAS:
            if c in bajo:
                malos.append(f"{ruta} menciona «{c}»")
    assert not malos, (
        "El dominio conoce cooperativas por nombre:\n  - "
        + "\n  - ".join(malos)
        + "\nEse es el condicional que el requisito 8 pide eliminar. El "
          "nucleo trabaja contra el puerto ReglaDeLiquidacion; quienes son "
          "las cooperativas de hoy es asunto de infraestructura.")


def test_las_tres_reglas_de_hoy_liquidan_distinto():
    r = modulo("cafetrace.infraestructura.reglas_cooperativas")
    reg = modulo("cafetrace.infraestructura.registro")
    l = modulo("cafetrace.dominio.liquidacion")
    reglas = [getattr(r, n)() for n in dir(r)
              if n[:1].isupper() and hasattr(getattr(r, n), "cooperativa")]
    registro = reg.construir_registro(reglas)
    faltan = [c for c in ("Naranjo", "Palmares", "Zarcero")
              if c not in registro]
    assert not faltan, f"Al registro le faltan estas cooperativas: {faltan}."
    liq = l.Liquidador(registro)
    precio = Decimal("95000")
    montos = {c: liq.liquidar(_lote(c), precio)
              for c in ("Naranjo", "Palmares", "Zarcero")}
    assert len(set(montos.values())) == 3, (
        f"Las tres cooperativas liquidan igual: {montos}. Si las formulas "
        f"dieran lo mismo, el requisito 8 no existiria y todo este disenio "
        f"sobraria. Revise: Naranjo ajusta por humedad, Zarcero descuenta "
        f"25 000.")
    for c, v in montos.items():
        assert isinstance(v, Decimal), (
            f"{c} devolvio {type(v).__name__} y el dinero es Decimal.")


def test_una_cooperativa_nueva_entra_desde_afuera():
    reg = modulo("cafetrace.infraestructura.registro")
    r = modulo("cafetrace.infraestructura.reglas_cooperativas")
    l = modulo("cafetrace.dominio.liquidacion")

    class ReglaDeLaSexta:
        """Una cooperativa que el estudiante nunca escribio."""
        cooperativa = "Sarchi"

        def liquidar(self, lote, precio_por_quintal):
            return Decimal("1")

    reglas = [getattr(r, n)() for n in dir(r)
              if n[:1].isupper() and hasattr(getattr(r, n), "cooperativa")]
    registro = reg.construir_registro([*reglas, ReglaDeLaSexta()])
    liq = l.Liquidador(registro)
    assert liq.liquidar(_lote("Sarchi"), Decimal("95000")) == Decimal("1"), (
        "La cooperativa nueva no llego a su regla. Agregar una cooperativa "
        "tiene que ser agregar un objeto al registro, sin tocar el nucleo.")


def test_una_cooperativa_desconocida_no_devuelve_none():
    reg = modulo("cafetrace.infraestructura.registro")
    l = modulo("cafetrace.dominio.liquidacion")
    e = modulo("cafetrace.dominio.errores")
    liq = l.Liquidador(reg.construir_registro([]))
    with pytest.raises(e.ErrorDominio):
        liq.liquidar(_lote("Tarrazu"), Decimal("95000"))


def test_el_registro_no_acepta_duplicados_en_silencio():
    reg = modulo("cafetrace.infraestructura.registro")
    r = modulo("cafetrace.infraestructura.reglas_cooperativas")
    reglas = [getattr(r, n)() for n in dir(r)
              if n[:1].isupper() and hasattr(getattr(r, n), "cooperativa")]
    assert reglas, "No encuentro ninguna regla de cooperativa."
    with pytest.raises(ValueError):
        reg.construir_registro([reglas[0], reglas[0]])


def test_d4_1_dice_que_compra_el_estilo_y_con_que_lo_paga():
    d = exige("D4.1")
    bajo = sin_tildes(d["decision"] + " " + d["justificacion"])
    assert "compra" in bajo and "paga" in bajo, (
        "D4.1 no completa la frase «este estilo compra ___ y lo paga con "
        "___». Todo estilo cobra algo; si no ve el costo, todavia no lo "
        "entendio.")


def test_d4_2_no_toca_el_dominio():
    d = exige("D4.2")
    bajo = sin_tildes(d["decision"])
    assert "dominio" not in bajo, (
        "En D4.2 usted mismo listo un archivo del paquete dominio entre los "
        "que hay que tocar para agregar la cooperativa seis. Si eso es "
        "cierto, el requisito 8 no se cumple; si no lo es, corrija la lista.")
