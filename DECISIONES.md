# Decisiones de arquitectura · CaféTrace

Este es el archivo principal del taller. Cada etapa le hace preguntas de
diseño; usted decide y justifica. **La justificación es lo que se califica,
no la decisión**: casi todas las preguntas tienen más de una respuesta
defendible, y ninguna se defiende sola.

Reglas del archivo:

- No borre ni renombre los encabezados `## Dx.y`: el marcador los busca.
- En **Decisión** escriba una sola línea, corta y sin rodeos.
- En **Justificación** escriba de tres a seis líneas y **cite al menos un
  requisito por su número** (`R-7`, `R-16`…) o un driver suyo (`QA-2`).
  Una justificación que no señala un requisito es una opinión.
- El **sello** lo imprime `python herramientas/marcador.py` al cerrar cada
  etapa. Péguelo tal cual.

---

## Etapa 0 · Del caso a los drivers

### D0.1 · ¿Cuál es el driver dominante de CaféTrace?

Escoja **un** requisito de los dieciocho. El dominante es el que, si se
incumple, vuelve inútil el resto del sistema.

**Decisión:**
El requisito 3 R-3 operar sin señal celular de tres a cuatro horas continuas.

**Justificación:**
La obligación de operar de forma continua bajo la restricción de infraestructura del R-3 y el atributo de calidad del R-4 donde la tableta no puede rechazar entregas por falta de red obliga a un diseño arquitectónico que sirva fuera de linea. Si no se diseña la persistencia local de la tableta para soportar estas horas sin señal, se detiene la recepción del camión en el patio y el envio de los lotes, haciendo inútil cualquier funcionalidad central del sistema.

### D0.2 · ¿Cuáles dos requisitos se contradicen, y cuál cede?

Nombre los dos por número, explique en qué se chocan, y diga cuál de los dos
va a ceder en su diseño y qué se pierde con eso.

**Decisión:**
El requisito 4 se contradice directamente con el requisito 5.

**Justificación:**
El requisito 4 exige máxima disponibilidad local en las tabletas o sea no rechazar ninguna entrega por falta de red, mientras que el requisito 5 exige integridad inmediata estricta lo que significa que un lote no puede cambiar de peso tras el cierre para no perder la certificación. En este diseño se prioriza la operación de campo del negocio y cede la consistencia inmediata global, se sacrifica la validación en tiempo real en favor de una consistencia. Con esto se gana continuidad en los patios pero se renuncia a la certeza inmediata del cierre en el sistema central.

**Sello:** 7b1ae19fd47f62e5

---

## Etapa 1 · Contexto

### D1.1 · El servicio de precio internacional, ¿queda dentro o fuera del sistema?

Responda exactamente `dentro` o `fuera`.

**Decisión:**
fuera

**Justificación:**
El servicio que publica el precio del quintal de café es un sistema externo mantenido por un tercero, según lo describe el R-14. CaféTrace no gobierna su infraestructura ni su ciclo de vida, por lo que actúa únicamente como un cliente que consume este dato externo mediante un puerto una vez que es publicado diariamente a las 3 p. mpor cada cooperativa.

### D1.2 · La tableta del recibidor, ¿es un actor externo o una parte del sistema?

Responda exactamente `externo` o `parte`. Piense quién la programa y quién la
despliega.

**Decisión:**
parte

**Justificación:**
La tableta del recibidor ejecuta una aplicación móvil diseñada por nosotros, capturar de forma estricta los datos obligatorios del R-1 es la idea principal. Al tener que asegurar la continuidad del negocio mediante almacenamiento local durante las caídas de red recurrentes en las fincas como nos dicen R-3 y R-4, la lógica de este cliente móvil en las tabletas opera como una pieza integrada que forma parte del despliegue del sistema y no como una interfaz externa a este.

**Sello:** b8575cfd2edfc56a

---

## Etapa 2 · Contenedores

### D2.1 · ¿Cómo se despliega CaféTrace?

Responda exactamente una de estas tres: `monolito modular`, `servicios`,
`híbrido`.

Antes de contestar lea otra vez el requisito 2 y el requisito 16. Los dos son
ciertos al mismo tiempo.

**Decisión:**
monolito modular

**Justificación:**
Aunque el R-2 exige alta escalabilidad para procesar 12,000 entregas al día durante la cosecha alta, la restricción operativa del R-16 es bastante firme, el sistema es mantenido por un solo desarrollador a medio tiempo sin equipo de operaciones. Diseñar una arquitectura de microservicios añadiría una sobrecarga operativa inmanejable para una sola persona, en cambio un monolito modular implementado de forma limpia en la nube permite un despliegue y monitoreo simple que cumple el R-16.

### D2.2 · ¿En cuál contenedor se calcula la liquidación al productor?

Escriba el nombre exacto del contenedor, tal como lo llamó en su diagrama.

**Decisión:**
Servidor Central (FastAPI)

**Justificación:**
El cálculo de la liquidación se ejecuta de forma centralizada en el contenedor del servidor debido a las reglas de negocio que cambian por cooperativa expresadas en el R-8. Dado que las tabletas operan de forma desconectada durante horas como se ve en el R-3 y poseen hardware limitado de 2 GB de RAM como se ve en el R-12, no es viable manejar en ellas algoritmos complejos ni almacenamiento de fórmulas en constante cambio. Centralizar este proceso en el monolito asegura consistencia de datos, auditoría inmediata según el R-10 y facilita que el desarrollador de medio tiempo actualice las reglas en un único espacio del codigo.

### D2.3 · ¿La tableta guarda datos por su cuenta? (`sí` / `no`)

**Decisión:**
sí

**Justificación:**
Para cumplir estrictamente con el R-4, que prohíbe rechazar camiones en el patio por falta de señal, la tableta debe ser completamente independiente. Bajo las condiciones del R-3, donde la señal celular se pierde de tres a cuatro horas consecutivas, el cliente móvil necesita almacenar localmente la totalidad de los datos del lote segun como viene en R-1, para luego encolar las transacciones para su posterior sincronización cuando la red vuelva.

**Sello:** 8e75499475f9606f

---

## Etapa 3 · Componentes y puertos

### D3.1 · ¿Con qué tipo representa el peso del café?

Responda exactamente una: `float`, `Decimal`, `tipo propio`.

**Decisión:**
tipo propio

**Justificación:**
Se selecciona un tipo propio implementado en la clase Peso para encapsular un valor de tipo Decimal y asegurar el cumplimiento del R-5. Esto previene errores de redondeo de los punto flotante y restringe a valores estrictamente mayores a cero, impidiendo que cambios o alteraciones externas afecten los pesos asociados a los lotes.

### D3.2 · ¿Quién decide que un lote quedó cerrado?

El dominio, la aplicación o la infraestructura. Responda con una de esas tres
palabras y diga qué pasaría si viviera en otra capa.

**Decisión:**
dominio

**Justificación:**
La condición de cierre es una regla de negocio que se valora en la certificación del R-5. Si este flujo residiera en la infraestructura, la lógica dependería directamente de las tecnologías de persistencia de datos o de las propias bases de datos, invalidando la operación sin internet requerida por el R-3 y el R-4. Al ubicarse en el dominio como un estado del objeto congelado, se garantiza la proteccion e independencia del entorno.

**Sello:** bacc5fe020e69c90

---

## Etapa 4 · Estilo arquitectónico

### D4.1 · ¿Qué estilo escogió, y qué cobra?

Nombre el estilo y complete la frase, literalmente:
«Este estilo **compra** ____ y lo **paga** con ____».

**Decisión:**
Este estilo compra modificaciones mas sencillas y lo paga con complejidad inicial.

**Justificación:**
Se utiliza una arquitectura basada en la inyección de dependencias como los puertos y adaptadores para cumplir el R-8. Este estilo compra la capacidad de añadir o alterar las fórmulas de cálculo de liquidación sin modificar un solo archivo del núcleo de la aplicación. Sin embargo, lo paga con la necesidad de crear una lista centralizada que el sistema consulta en tiempo real para saber qué componente debe encargarse de procesar cada tarea.

### D4.2 · Entra la cooperativa número seis. ¿Cuáles archivos hay que tocar?

Liste las rutas. Si en la lista aparece un archivo del paquete `dominio`, su
diseño todavía no cumple el requisito 8.

**Decisión:**
cafetrace/infraestructura/reglas_cooperativas.py y el punto de entrada de la aplicación main.py.

**Justificación:**
Al emplear el patrón de inyectar desde el exterior, la llegada de una nueva organización según el R-9 se trata como una extensión técnica solo en la capa de infraestructura. Solo es requerido crear una nueva clase que vea la firma adecuada en el archivo de reglas y ponerla en el listado del inicializador central, por otra parte, el paquete dominio permanece intacto, protegido ante cambios externos.

**Sello:** 7721321f67632d0b

---

## Etapa 5 · Integración y fallas

### D5.1 · Estilo de integración con cada contraparte

Tres respuestas, una por línea, cada una con una de estas palabras:
`archivo`, `rpc`, `mensajería`, `evento`.

```
ICAFE: archivo
Aduana: rpc
Tabletas: mensajería
```

**Decisión:**
Se seleccionan estilos heterogéneos como archivo para ICAFE, rpc para Aduana y mensajería para Tabletas.

**Justificación:**
El R-6 obliga al uso de un archivo plano mensual para el ICAFE por carecer de interfaces modernas. Para la Aduana se opta por rpc mediante llamadas directas HTTP debido a que es un servicio externo requerido durante los despachos en puerto caldera R-11, evitando que sus cambios repentinos R-7 afecten el resto del sistema usando una capa intermedia. Por último, para las Tabletas se implementa un modelo de mensajería asincronico para cumplir estrictamente el R-3 y R-4, garantizando el encolado local de los datos de los lotes para su retransmisión cuando vuelva la conexion a red.

### D5.2 · La tableta reenvía una entrega que ya había llegado. ¿Qué pasa?

Describa el comportamiento que usted implementó, no el que le gustaría.

**Decisión:**
El sistema ejecuta una respuesta duplicada devolviendo el mismo comprobante original peeeero con la bandera de duplicado activa, asi funciona sin alterar los lotes.

**Justificación:**
Bajo las condiciones de caídas de red recurrentes R-3, las tabletas retransmitirán transacciones de forma tardía en los tiempos de alta cosecha R-2. Para cumplir con la inmutabilidad exigida por la certificación en R-5, el caso de uso intercepta el reenvío a través del método entrega_registrada, omitiendo la inserción en el dominio para evitar cobrar doble al productor, pero retornando un éxito con la bandera de duplicado=True para que la tableta limpie su cola de manera local.

**Sello:** f821abd2f54c73a0

---

## Etapa 6 · Registro de decisiones

### D6.1 · La prueba del cambio

Para cada cambio, cuántos archivos suyos hay que tocar y cuáles:

```
a) Cambia la fórmula de liquidación de Palmares:
b) El ICAFE pasa de archivo de posiciones fijas a un CSV:
c) Hay que soportar un segundo idioma en el comprobante:
```

**Decisión:**

**Justificación:**

**Sello:**

---

## Cierre · Los dos conflictos

Durante el taller dos principios o dos atributos de calidad le pidieron cosas
distintas. Escriba ambos casos: qué pedía cada lado, cuál cedió y por qué.

**Conflicto 1:**

**Conflicto 2:**
