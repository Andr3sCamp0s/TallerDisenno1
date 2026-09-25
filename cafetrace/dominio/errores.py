"""Errores del dominio.

ETAPA 3. Complete la jerarquia. Todos descienden de ErrorDominio: eso es lo
que le permite al borde distinguir «el usuario mando algo malo» de «se cayo
la base de datos».
"""


class ErrorDominio(Exception):
    """Raiz de todo lo que el dominio sabe rechazar."""


class ErrorDominio(Exception):
    """Raiz de todo lo que el dominio sabe rechazar."""


class EntregaInvalida(ErrorDominio):
    """Se levanta cuando los datos de una entrega no son válidos."""


class LoteYaCerrado(ErrorDominio):
    """Se levanta al intentar modificar un lote ya cerrado."""

    
# TODO etapa 4: CooperativaNoRegistrada
