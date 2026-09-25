# Drivers de CaféTrace

## Parte 1 · Clasificación de los dieciocho requisitos

Una fila por requisito, en orden. El **tipo** es una de estas tres letras:

- `QA` — atributo de calidad: dice *qué tan bien*, y se puede medir.
- `R` — restricción: no se negocia, se acata.
- `F` — funcional: dice *qué hace* el sistema.

En los `QA` la columna **medida** es obligatoria: un número y una unidad. Si
no puede medirlo, o no es un atributo de calidad, o le falta preguntar.

| # | Tipo | Qué exige, en sus palabras | Medida (solo QA) |
|---|------|----------------------------|------------------|
| 1 | F | El recibidor debe poder capturar peso, humedad y cédula de los productores en el patio de recibo. | |
| 2 | QA | Soportar un incremento masivo en la tasa transaccional diaria debido al pico estacional de cosecha. | 12000 entregas / día |
| 3 | R | El sistema de recolección en sitio debe operar sin dependencia de conectividad celular contínua. | |
| 4 | QA | La tableta debe procesar y almacenar localmente las entregas cuando no cuente con enlace a la red. | 0 entregas rechazadas por falta de red |
| 5 | QA | Garantizar la inmutabilidad absoluta de los datos de un lote una vez que este ha sido cerrado. | 0 cambios permitidos post-cierre |
| 6 | R | Generar reportes mensuales en formato legacy de posiciones fijas (1998) para cumplir con el ICAFE. | |
| 7 | QA | Aislar el sistema ante la inestabilidad y cambios imprevistos de la API REST externa de la aduana. | 0 fallos de acoplamiento ante cambios de API |
| 8 | QA | Permitir la incorporación y modificación dinámica de las fórmulas de liquidación específicas de cada cooperativa. | 100% de aislamiento |
| 9 | QA | Escalar la capacidad del sistema para soportar el doble de cooperativas integradas en el mediano plazo. | 10 cooperativas |
| 10 | QA | Recuperar el historial de trazabilidad completo de cualquier lote de forma inmediata para auditorías. | 5 años de antigüedad / inmediato |
| 11 | QA | Optimizar el rendimiento y consumo de datos para consultas desde redes celulares de baja señal. | 1 barra de señal celular mínima |
| 12 | R | La aplicación cliente en las tabletas debe ejecutarse en hardware de gama baja con memoria severamente limitada. | |
| 13 | QA | Mantener la disponibilidad del servicio según la estacionalidad del año (alta cosecha vs resto del año). | 99.5% de tiempo de actividad en cosecha |
| 14 | F | El sistema debe consumir diariamente el precio internacional del quintal de café publicado a las 3:00 p.m. | |
| 15 | F | El sistema debe permitir agrupar entregas en lotes y dividir estos lotes en sublotes de calidades variables. | |
| 16 | R | La solución debe ser simple y requerir mínimo esfuerzo operativo (mantenida por un solo desarrollador de medio tiempo). | |
| 17 | R | Cumplir estrictamente con la Ley 8968 (Prodhab) para proteger los datos personales (cédula y nombre) del productor. | |
| 18 | QA | Suministrar un tablero de control gerencial con datos consolidados y actualizados de forma periódica en el día. | Actualización máxima cada 1 hora |

## Parte 2 · Los seis que mandan

De los que marcó `QA` y `R`, escoja seis y ordénelos. El primero es el que
más va a doblar su arquitectura.

| Orden | # | Código suyo | Por qué está entre los seis |
|-------|---|-------------|------------------------------|
| 1 | 3 | R-3 | Fuerza un diseño que sirva fuera de linea. Las tabletas deben operar aisladas por horas y manejar persistencia local y sincronización posterior. |
| 2 | 16 | R-16 | Restringe la complejidad en el despliegue. Prohíbe arquitecturas complejas de microservicios de muchos componentes, forzando un enfoque de monolito modular simple de operar. |
| 3 | 12 | R-12 | Condiciona directamente el desarrollo de software, limitando el consumo de memoria a 2 GB de RAM. |
| 4 | 4 | QA-4 | Establece que la disponibilidad local de la tableta en el patio de recibo tiene mas prioridad que la consistencia del sistema general. |
| 5 | 8 | QA-8 | Exige un diseño de software altamente suelto para aislar las modificaciones de las fórmulas de liquidación de cada cooperativa. |
| 6 | 17 | R-17 | Obliga a introducir desde el principio capas de cifrado y mecanismos de control de acceso sobre los datos personales. |

## Parte 3 · Tres escenarios de atributo de calidad

Las seis partes, rotuladas. **Al menos uno** debe ocurrir en entorno
degradado: sin red, en pico de cosecha, o con una contraparte caída. Sin eso
el escenario no obliga a decidir nada.

### Escenario 1 · Operación sin red

- **Fuente:** Recibidor en el patio de recibo rural.
- **Estímulo:** Intento de registrar una entrega de café en el camión del productor.
- **Artefacto:** Aplicación móvil en la tableta del recibidor.
- **Entorno:** Sin señal celular durante un periodo de al menos 3 horas continuas.
- **Respuesta:** El sistema procesa la transacción de manera local, emite el comprobante y manda a la cola los datos para que se sincronizen despues cuando ya haya señal.
- **Medida:** Ningun camion rechazado y la totalidad de los datos guardados localmente.

### Escenario 2 · Pico de cosecha alta

- **Fuente:** Múltiples recibidores sincronizando datos al mismo tiempo desde todas las cooperativas.
- **Estímulo:** Envío masivo de transacciones de pesaje e ingreso de fruta hacia el servidor principal.
- **Artefacto:** API Central de CaféTrace.
- **Entorno:** En pleno pico de cosecha donde las entregas diarias pasan de 300 a 12 000 por día.
- **Respuesta:** El servidor central procesa las ráfagas de datos entrantes de forma fluida sin saturar la base de datos ni quedarse pegado.
- **Medida:** Las 12 000 entregas diarias se procesan de forma exitosa y el tiempo de respuesta de la API se mantiene en menos de 2 segundos.

### Escenario 3 · API de la aduana cambiada

- **Fuente:** Sistema de exportación e integración con entidades externas.
- **Estímulo:** Intento de mandar los datos de un contenedor listo en el puerto hacia la aduana.
- **Artefacto:** Componente o adaptador de interfaz de la Aduana.
- **Entorno:** La API de la aduana cambió su formato de datos por cuarta vez en dos años, sin avisar a nadie y sin versionar.
- **Respuesta:** El adaptador le hace catch al error para que el sistema central siga funcionando normal, manda una alerta a los programadores y deja el envío listo para reintentarlo cuando se cambie el código respetando la nueva configuracion de la API de aduanas.
- **Medida:** Cero caídas en el núcleo del sistema de CaféTrace y el equipo tarda menos de 4 horas en acomodar el adaptador al nuevo formato de la API de aduanas.