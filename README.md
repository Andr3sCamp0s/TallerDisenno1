# Taller de arquitectura · CaféTrace

**IC-6821 Diseño de Software · Tema 4 · individual y asíncrono**

Este taller no le pide programar un sistema. Le pide **decidir** uno, y dejar
las decisiones escritas, dibujadas y —donde se puede— verificadas por una
prueba.

Son siete etapas. Cada una le hace preguntas de diseño que usted contesta en
`DECISIONES.md`, le pide un dibujo, y en varias le pide código. El marcador
revisa las tres cosas **y que digan lo mismo entre sí**: si usted escribe
«monolito modular» y dibuja cuatro servidores, el marcador se lo dice.

> Casi ninguna pregunta tiene una sola respuesta correcta. Lo que se califica
> es la justificación: qué requisito la sostiene y qué se pierde con ella.

---

## Antes de empezar

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS o Linux

pip install -r requirements.txt
python herramientas/marcador.py
```

Debería ver siete etapas en rojo. Eso está bien: es el punto de partida.

Escriba su nombre y su carné en `ESTUDIANTE.txt` antes de la primera corrida.

### Cómo se trabaja

1. Lea `CASO.md` completo. Los dieciocho requisitos están desordenados a
   propósito.
2. Abra la etapa que le toca: `python herramientas/marcador.py 0`.
3. Lea el **docstring** del archivo de pruebas de esa etapa
   (`pruebas/test_etapa0_drivers.py`). Ahí está el concepto y un pequeño
   experimento: casi siempre le pide **predecir** algo antes de hacerlo. Haga
   la predicción. El taller sirve el doble si la hace.
4. Conteste, dibuje, programe. Corra el marcador hasta que la etapa quede en
   verde.
5. Copie el sello que imprime el marcador en la línea `**Sello:**` de esa
   etapa, en `DECISIONES.md`.
6. Siga a la etapa siguiente.

No salte etapas. La 4 se apoya en el código de la 3, y la 5 en el de la 4.

---

## Los dibujos: primero a mano, después en Mermaid

Cada dibujo se entrega **dos veces**, y no es redundancia.

**A mano, en papel, con foto en `BOSQUEJOS/etapaN.jpg`.** Dibujar a mano es
lo que le obliga a decidir: dónde poner la caja, qué dejar afuera, qué flecha
sobra. Se borra, se vuelve a empezar, se tacha. Eso es diseñar.

**En Mermaid, en `diagramas/etapaN-*.mmd`.** Transcribir el dibujo a texto es
lo que lo vuelve revisable: el marcador puede contar sus flechas y ver hacia
dónde apuntan. Eso es lo que permite que una prueba le diga «del dominio le
está saliendo una flecha».

La foto tiene que **leerse**: nombres de cajas legibles, no una servilleta a
contraluz. El marcador rechaza imágenes de menos de 15 KB.

Para ver cómo le va quedando un `.mmd`, pegue el contenido en
<https://mermaid.live>. En los archivos `.mmd` las líneas que empiezan con
`%%` son comentarios: ahí están las reglas que revisa el marcador. **Esas
líneas se quedan**; lo que se borra es el ejemplo y la línea que dice
`PLANTILLA-SIN-RESOLVER`.

---

## Las siete etapas

| # | De qué se trata | Qué entrega |
|---|-----------------|-------------|
| 0 | Del caso a los drivers | `DRIVERS.md` · D0.1, D0.2 |
| 1 | Contexto: qué es el sistema y qué no | bosquejo + `etapa1-contexto.mmd` · D1.1, D1.2 |
| 2 | Contenedores: cómo se despliega | bosquejo + `etapa2-contenedores.mmd` · D2.1, D2.2, D2.3 |
| 3 | Componentes y puertos | bosquejo + `etapa3-componentes.mmd` · código del dominio · D3.1, D3.2 |
| 4 | Estilo arquitectónico | código de liquidación y registro · D4.1, D4.2 |
| 5 | Integración y fallas | bosquejo + `etapa5-secuencia.mmd` · código del borde y del caso de uso · sus dos pruebas · D5.1, D5.2 |
| 6 | Registro de decisiones | dos ADR en `ADR/` · D6.1 · el cierre de `DECISIONES.md` |

---

## Qué se revisa, y qué no

El marcador **no** revisa si su arquitectura es la que yo habría hecho.
Revisa cuatro cosas:

1. **Que haya decidido.** Una decisión en blanco es cero, aunque el resto esté
   perfecto.
2. **Que la justificación se apoye en el caso.** Toda justificación tiene que
   citar al menos un requisito por su número (`R-7`, `requisito 16`) o un
   driver suyo (`QA-2`). Una justificación sin número es una opinión.
3. **Que el documento, el dibujo y el código digan lo mismo.** Ahí es donde
   fallan casi todos los diseños reales.
4. **Que el código cumpla el contrato** que está escrito en el docstring de
   cada archivo de `cafetrace/`. Léalos: son el enunciado.

---

## Reglas

- **No modifique** `pruebas/`, `herramientas/` ni `pytest.ini`. El marcador
  guarda una huella de su trabajo y se nota.
- Sus propias pruebas van en `mis_pruebas/`, y cuentan para la etapa 5.
- Todo en español, incluidos los nombres de clases y funciones que agregue.
  Los nombres que las pruebas esperan ya están dados.
- Se entrega la carpeta completa, incluida `EVIDENCIA/registro.jsonl`.
- Si algo del enunciado le parece contradictorio, probablemente lo sea: el
  caso tiene contradicciones a propósito. No pregunte cuál es la buena;
  decida y escriba por qué.

## Qué se entrega

Un `.zip` con toda la carpeta, con este nombre:

```
carne-apellido-taller-arquitectura.zip
```

Antes de comprimir, corra `python herramientas/marcador.py` una última vez y
revise que `DECISIONES.md` tenga los siete sellos.
