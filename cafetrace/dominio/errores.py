"""Errores del dominio.

ETAPA 3. Complete la jerarquia. Todos descienden de ErrorDominio: eso es lo
que le permite al borde distinguir «el usuario mando algo malo» de «se cayo
la base de datos».
"""


class ErrorDominio(Exception):
    """Raiz de todo lo que el dominio sabe rechazar."""


# TODO etapa 3: EntregaInvalida, LoteYaCerrado
# TODO etapa 4: CooperativaNoRegistrada
