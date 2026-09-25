"""ETAPA 3 · Componentes, puertos y la direccion de las dependencias.

EL CONCEPTO
Hasta aqui todo fue dibujo. Ahora el dibujo tiene que sostenerse en codigo.

La idea central es una sola: las flechas apuntan HACIA el dominio, nunca
desde el. El dominio declara lo que necesita (los puertos) y la
infraestructura los implementa. Por eso el dominio se puede probar sin base
de datos, sin red y sin esperar a que den las tres de la tarde.

EL EXPERIMENTO
Antes de escribir nada, abra su diagrama de la etapa 3 y cuente las flechas
que salen del subgrafo «dominio». Prediga cuantas deberian ser. La respuesta
correcta es cero, y esta prueba la verifica sobre el dibujo Y sobre el
codigo.
"""
from datetime import datetime
from decimal import Decimal

import pytest

from .apoyo import (PAQUETE, bosquejo, diagrama, fuente_del_paquete, modulo,
                    opcion, sin_tildes)

pytestmark = pytest.mark.etapa3
ARCHIVO = "etapa3-componentes.mmd"
PROHIBIDO_EN_DOMINIO = ("requests", "urllib", "httpx", "psycopg", "sqlite3",
                        "sqlalchemy", "boto3", "flask", "fastapi", "redis")


def test_hay_bosquejo_a_mano():
    assert (bosquejo(3) is not None
            and bosquejo(3).stat().st_size > 15000), (
        "Falta BOSQUEJOS/etapa3.jpg legible.")


def test_el_dominio_no_conoce_el_mundo_exterior():
    malos = []
    for ruta, src in fuente_del_paquete("dominio").items():
        for mal in PROHIBIDO_EN_DOMINIO:
            if mal in src:
                malos.append(f"{ruta} usa «{mal}»")
        if "datetime.now" in src or "date.today" in src:
            malos.append(f"{ruta} llama al reloj directamente")
    assert not malos, (
        "El dominio esta tocando el mundo exterior:\n  - "
        + "\n  - ".join(malos)
        + "\nLo que necesite del exterior se lo pide a un puerto. Si el "
          "dominio importa la red, no se puede probar sin red, y el "
          "requisito 3 dice que la red se cae.")


def test_los_cuatro_puertos_existen_con_sus_operaciones():
    p = modulo("cafetrace.dominio.puertos")
    esperado = {"RepositorioDeLotes": ["guardar", "por_id",
                                       "entrega_registrada"],
                "Reloj": ["ahora"],
                "PrecioDelDia": ["por_quintal"],
                "Bitacora": ["registrar"]}
    for nombre, metodos in esperado.items():
        clase = getattr(p, nombre, None)
        assert clase is not None, (
            f"Falta el puerto {nombre} en cafetrace/dominio/puertos.py.")
        faltan = [m for m in metodos if not hasattr(clase, m)]
        assert not faltan, (
            f"Al puerto {nombre} le faltan estas operaciones: {faltan}. Los "
            f"nombres importan: son el contrato que va a implementar la "
            f"infraestructura.")


def test_el_peso_es_un_tipo_y_rechaza_lo_imposible():
    m = modulo("cafetrace.dominio.modelos")
    e = modulo("cafetrace.dominio.errores")
    Peso = getattr(m, "Peso", None)
    assert Peso is not None, "Falta el tipo Peso en dominio/modelos.py."
    assert Peso is not float, (
        "Peso es un alias de float. El requisito 5 dice que un lote no puede "
        "cambiar de peso: con un float suelto, cualquier funcion puede "
        "sumarle algo y nadie se entera.")
    p = Peso(Decimal("120.5"))
    assert hasattr(p, "kilos"), "Peso debe exponer .kilos"
    with pytest.raises(e.ErrorDominio):
        Peso(Decimal("0"))
    with pytest.raises(e.ErrorDominio):
        Peso(Decimal("-3"))


def test_un_lote_cerrado_ya_no_cambia():
    m = modulo("cafetrace.dominio.modelos")
    e = modulo("cafetrace.dominio.errores")
    entrega = m.Entrega(id_entrega="E-1", cedula_productor="102340567",
                        peso=m.Peso(Decimal("100")), humedad=Decimal("11"),
                        recibida_en=datetime(2026, 11, 3, 8, 0))
    lote = m.Lote(id_lote="L-1", cooperativa="Naranjo", entregas=())
    lote = lote.agregar(entrega)
    assert lote.peso_total.kilos == Decimal("100")
    cerrado = lote.cerrar()
    with pytest.raises(e.ErrorDominio):
        cerrado.agregar(entrega)
    assert lote.entregas == (entrega,), (
        "agregar() y cerrar() deben devolver un Lote NUEVO y dejar el "
        "anterior intacto. Eso es lo que hace verificable el requisito 5.")


def test_el_dibujo_tiene_las_tres_capas():
    d = diagrama(ARCHIVO)
    nombres = {sin_tildes(k) for k in d.subgrafos}
    faltan = [c for c in ("dominio", "aplicacion", "infraestructura")
              if c not in nombres]
    assert not faltan, f"Al diagrama le faltan los subgrafos: {faltan}."
    for capa in ("dominio", "aplicacion", "infraestructura"):
        n = len(d.nodos_de_subgrafo(capa))
        assert n >= 2, (
            f"El subgrafo «{capa}» tiene {n} componente(s). Dibuje al menos "
            f"dos por capa: con uno solo no se ve el reparto.")


def test_del_dominio_no_sale_ninguna_flecha():
    d = diagrama(ARCHIVO)
    fuera = (d.aristas_de_subgrafo_a("dominio", "infraestructura")
             + d.aristas_de_subgrafo_a("dominio", "aplicacion"))
    assert not fuera, (
        "Su dibujo tiene flechas que salen del dominio:\n  - "
        + "\n  - ".join(f"{a.de} --{a.etiqueta or ''}--> {a.a}"
                         for a in fuera)
        + "\nEsas flechas van al reves. El dominio declara puertos; la "
          "infraestructura los implementa y apunta hacia adentro. Si el "
          "dominio apunta hacia afuera, volvio a acoplarse a la tecnologia y "
          "el resto del taller se cae.")


def test_la_infraestructura_apunta_hacia_el_dominio():
    d = diagrama(ARCHIVO)
    hacia = d.aristas_de_subgrafo_a("infraestructura", "dominio")
    assert hacia, (
        "Ninguna flecha va de infraestructura hacia dominio. Si los "
        "adaptadores no implementan ningun puerto, las capas estan "
        "desconectadas: revise que los puertos aparezcan en el dibujo.")


def test_las_decisiones_de_la_etapa_estan_respondidas():
    tipo = opcion("D3.1", ("tipo propio", "decimal", "float"))
    assert tipo != "float", (
        "Escogio float para el peso. Con punto flotante 0.1 + 0.2 no da 0.3, "
        "y aqui se suman entregas para formar lotes que despues se liquidan "
        "en plata. Si de verdad quiere defender float, tendria que explicar "
        "como cumple el requisito 5.")
    opcion("D3.2", ("dominio", "aplicacion", "infraestructura"))
