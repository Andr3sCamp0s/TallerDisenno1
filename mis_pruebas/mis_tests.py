from datetime import datetime
from decimal import Decimal
import pytest
from cafetrace.dominio.modelos import Lote, Entrega, Peso
from cafetrace.dominio.errores import LoteYaCerrado
from cafetrace.aplicacion.borde import SolicitudEntrega
from cafetrace.aplicacion.recibo import RegistrarEntrega

class ReporteFalso:
    def __init__(self, lote):
        self.lote = lote
        self.entregas = set()
    def guardar(self, lote): self.lote = lote
    def por_id(self, id_lote): return self.lote
    def entrega_registrada(self, id_entrega): return id_entrega in self.entregas

class RelojFijo:
    def ahora(self): return datetime(2026, 11, 3, 8, 0)

class BitacoraFalsa:
    def registrar(self, evento, **datos): pass


#Primera prueba: reenvio de la misma entrega
def test_reenvio_dos_veces_no_duplica():
    lote = Lote(id_lote="L-1", cooperativa="Palmares")
    repo = ReporteFalso(lote)
    caso = RegistrarEntrega(repo, RelojFijo(), BitacoraFalsa())
    sol = SolicitudEntrega(id_entrega="E-1", cedula_productor="102340567", kilos=Decimal("100"), humedad=Decimal("11"))
    
    caso.ejecutar(sol, id_lote="L-1")
    repo.entregas.add("E-1")
    comp = caso.ejecutar(sol, id_lote="L-1")
    
    assert comp.duplicado is True
    assert len(repo.lote.entregas) == 1


#Prueba 2: mandar lote cerrado
def test_lote_cerrado_levanta_loteyacerrado():
    lote = Lote(id_lote="L-2", cooperativa="Naranjo").cerrar()
    entrega = Entrega("E-2", "102340567", Peso(Decimal("50")), Decimal("12"), datetime(2026, 11, 3, 8, 0))
    with pytest.raises(LoteYaCerrado):
        lote.agregar(entrega)
