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

**Justificación:**

### D0.2 · ¿Cuáles dos requisitos se contradicen, y cuál cede?

Nombre los dos por número, explique en qué se chocan, y diga cuál de los dos
va a ceder en su diseño y qué se pierde con eso.

**Decisión:**

**Justificación:**

**Sello:**

---

## Etapa 1 · Contexto

### D1.1 · El servicio de precio internacional, ¿queda dentro o fuera del sistema?

Responda exactamente `dentro` o `fuera`.

**Decisión:**

**Justificación:**

### D1.2 · La tableta del recibidor, ¿es un actor externo o una parte del sistema?

Responda exactamente `externo` o `parte`. Piense quién la programa y quién la
despliega.

**Decisión:**

**Justificación:**

**Sello:**

---

## Etapa 2 · Contenedores

### D2.1 · ¿Cómo se despliega CaféTrace?

Responda exactamente una de estas tres: `monolito modular`, `servicios`,
`híbrido`.

Antes de contestar lea otra vez el requisito 2 y el requisito 16. Los dos son
ciertos al mismo tiempo.

**Decisión:**

**Justificación:**

### D2.2 · ¿En cuál contenedor se calcula la liquidación al productor?

Escriba el nombre exacto del contenedor, tal como lo llamó en su diagrama.

**Decisión:**

**Justificación:**

### D2.3 · ¿La tableta guarda datos por su cuenta? (`sí` / `no`)

**Decisión:**

**Justificación:**

**Sello:**

---

## Etapa 3 · Componentes y puertos

### D3.1 · ¿Con qué tipo representa el peso del café?

Responda exactamente una: `float`, `Decimal`, `tipo propio`.

**Decisión:**

**Justificación:**

### D3.2 · ¿Quién decide que un lote quedó cerrado?

El dominio, la aplicación o la infraestructura. Responda con una de esas tres
palabras y diga qué pasaría si viviera en otra capa.

**Decisión:**

**Justificación:**

**Sello:**

---

## Etapa 4 · Estilo arquitectónico

### D4.1 · ¿Qué estilo escogió, y qué cobra?

Nombre el estilo y complete la frase, literalmente:
«Este estilo **compra** ____ y lo **paga** con ____».

**Decisión:**

**Justificación:**

### D4.2 · Entra la cooperativa número seis. ¿Cuáles archivos hay que tocar?

Liste las rutas. Si en la lista aparece un archivo del paquete `dominio`, su
diseño todavía no cumple el requisito 8.

**Decisión:**

**Justificación:**

**Sello:**

---

## Etapa 5 · Integración y fallas

### D5.1 · Estilo de integración con cada contraparte

Tres respuestas, una por línea, cada una con una de estas palabras:
`archivo`, `rpc`, `mensajería`, `evento`.

```
ICAFE:
Aduana:
Tabletas:
```

**Decisión:**

**Justificación:**

### D5.2 · La tableta reenvía una entrega que ya había llegado. ¿Qué pasa?

Describa el comportamiento que usted implementó, no el que le gustaría.

**Decisión:**

**Justificación:**

**Sello:**

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
