# 0002 · Adopción de Monolito Modular por restricción de mantenimiento

Estado: aceptado · 2026-11-03 · sustituye a nada

## Contexto

Cada cooperativa aplica fórmulas de liquidación distintas y las cambia a su conveniencia diarimente, tal como lo explica el R-8, proyectando duplicar la cantidad de cooperativas integradas en tres años tal y como dice R-9. Al mismo tiempo, el sistema cuenta únicamente con un desarrollador de medio tiempo para dar soporte y mantener toda la plataforma operativa R-16.

## Decisión

Adoptamos un estilo de Monolito Modular aislando la lógica de negocio. Las fórmulas se inyectan como adaptadores de infraestructura sin tocar el paquete de dominio, manteniendo un único entregable de software centralizado, esto con el fin de que no sea dificil para el desaroolador aplicar los cambios ni se deban de hacer multiples modificaciones para poner una nueva cooperativa y su formula, lo que evita largos tiempos de trabajo para una sola persona.

## Alternativas descartadas

- Arquitectura de Microservicios independientes: Se descarta porque operar y monitorear múltiples contenedores distribuidos en la nube consume un esfuerzo operativo inmanejable para una sola persona, lo cual es algo que no ayudaria para nada a que se respete el R-16.
- Lógica condicional (if/else) por cooperativa dentro del núcleo: Se descarta porque añadir nuevas organizaciones como lo predice R-9 obligaría a modificar constantemente el código raíz del dominio, violando el aislamiento transaccional del que habla R-8.

## Consecuencias

- + Mantenimiento y despliegue sumamente simplificado para un desarrollador a medio tiempo R-16.
- + Extensibilidad limpia, agregar cooperativas es solo añadir un archivo inyectable de infraestructura R-9.
- − Todo el sistema comparte la misma base de datos centralizada, lo que requiere un control estricto de accesabilidad para cumplir las leyes de datos personales R-17.
