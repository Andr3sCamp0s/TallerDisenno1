# 0001 · Persistencia local e idempotencia para operación sin red

Estado: aceptado · 2026-11-03 · sustituye a nada

## Contexto

El sistema debe operar en patios de recibo rurales con caídas de señal celular continuas de 3 a 4 horas R-3. No se puede detener la operación ni rechazar camiones en fila R-4. Además, el volumen en cosecha alta crece 40 veces llegando a 12,000 transacciones diarias R-2, lo que provocará ráfagas de reintentos acumulados cuando las tabletas recuperen la red.

## Decisión

Implementamos una estrategia de comunicacion offline con una base de datos embebida en la tableta para almacenar localmente los datos del lote como se pide en R-1. Al sincronizar, el caso de uso central valida la duplicidad de IDs para asi no afectar al dominio y con esto lograr proteger la inmutabilidad del lote ya cerrado como esta en R-5.

## Alternativas descartadas

- Validación síncrona en el servidor central: Se descarta porque al perderse la señal por horas R-3, la tableta fallaría y rechazaría entregas obligando a detener los camiones, violando por completo el R-4.
- Rechazo de transacciones duplicadas con error HTTP 400: Se descarta porque los reintentos automáticos de la tableta tras estar offline R-3 dispararían alertas falsas de fallo, asustando al recibidor e interrumpiendo el flujo normal del negocio, entre menos cosas tecnicas vea el cliente, mejor.

## Consecuencias

- + Se garantiza la continuidad total del pesaje en el patio sin importar el estado de la red R-4.
- + Se protege la integridad en el inventario de café evitando duplicaciones accidentales R-5.
- − Se introduce consistencia eventual, el tablero gerencial del R-18 experimentará retrasos de actualización de datos mientras las tabletas estén desconectadas, lo que puede generar disconcordias en el inventario momentaneas.
