# CaféTrace

## Qué hay que resolver

La **Unión de Cooperativas Cafetaleras del Valle Occidental** agrupa hoy cinco
cooperativas. Necesita trazar cada lote de café desde que el productor entrega
la fruta en el patio de recibo hasta que el contenedor sale del puerto de
Caldera.

Hoy eso se lleva en cuadernos y en tres hojas de cálculo que no cuadran entre
sí. Cuando llega la auditoría de certificación, dos personas se pasan una
semana reconstruyendo de dónde salió cada saco.

Usted va a diseñar la arquitectura. No la va a programar completa: va a tomar
las decisiones, dibujarlas, justificarlas y escribir en Python las piezas donde
la decisión se vuelve verificable.

## Cómo funciona el negocio, en cinco líneas

1. El productor llega en camión al **patio de recibo** y entrega fruta. El
   recibidor pesa, mide humedad y emite un comprobante.
2. Varias entregas forman un **lote**. El lote se beneficia (se seca y se
   pila) y puede **dividirse** en sublotes de distinta calidad.
3. Cada cooperativa **liquida** al productor con su propia fórmula.
4. Los sublotes se **consolidan** en contenedores y se exportan.
5. Todo el recorrido tiene que poder **reconstruirse** años después.

## Los dieciocho requisitos, tal como salieron de las entrevistas

Están desordenados a propósito, y mezclan funcionalidad, atributos de calidad
y restricciones. Separarlos es la primera parte de su trabajo.

| # | Lo que dijeron |
|---|---|
| 1 | «El recibidor registra la entrega del productor en el patio: peso en kilos, humedad y cédula del productor.» |
| 2 | «En cosecha alta recibimos cuarenta veces más entregas que el resto del año: pasamos de 300 a 12 000 por día, de noviembre a febrero.» |
| 3 | «Los patios están en zona rural. Hay días en que no hay señal celular durante tres o cuatro horas seguidas.» |
| 4 | «La tableta no puede rechazar una entrega porque no hay red. El productor está ahí, con el camión y con la fila atrás.» |
| 5 | «Un lote no puede cambiar de peso después de cerrado. La certificación lo prohíbe y es causal de perder el sello.» |
| 6 | «El ICAFE exige un archivo mensual con formato de posiciones fijas, definido en 1998. No tienen API y no la van a tener.» |
| 7 | «La aduana expone una API REST que ya cambió tres veces en dos años, sin avisar y sin versionar.» |
| 8 | «Cada cooperativa liquida distinto: Naranjo paga por calidad, Palmares por peso, Zarcero descuenta adelantos. Y cada una cambia su fórmula cuando quiere.» |
| 9 | «Hoy somos cinco cooperativas. En tres años esperamos ser diez.» |
| 10 | «La auditoría puede pedir la trazabilidad completa de cualquier lote de los últimos cinco años, y hay que entregarla en el momento.» |
| 11 | «El exportador consulta el estado de sus contenedores desde el celular, parado en el puerto, con una barra de señal.» |
| 12 | «Las tabletas de los recibidores ya están compradas: Android de gama baja, 2 GB de RAM.» |
| 13 | «Durante la cosecha el sistema tiene que estar arriba el 99,5 % del tiempo. Fuera de cosecha, con 95 % nos damos por servidos.» |
| 14 | «El precio internacional del quintal lo publica un servicio externo, y cambia todos los días a las 3 p. m.» |
| 15 | «Un lote se arma con varias entregas, y al beneficiar se puede partir en sublotes de distinta calidad.» |
| 16 | «No tenemos equipo de operaciones. Un solo desarrollador mantiene todo, y es medio tiempo.» |
| 17 | «La cédula y el nombre del productor son datos personales. Aplica la Ley 8968.» |
| 18 | «El gerente quiere un tablero con el avance de la cosecha, actualizado durante el día.» |

## Lo que ya está decidido y usted no negocia

- El sistema se despliega en la nube, en la región más cercana (Virginia).
- El lenguaje es Python. La base de datos es PostgreSQL.
- El presupuesto de infraestructura es de 300 dólares al mes. No hay más.

## Una advertencia sobre este caso

Dos de los dieciocho requisitos se contradicen entre sí, y otros dos empujan
hacia soluciones opuestas. Esa tensión no es un error del enunciado: es el
caso. Su trabajo no es hacerlos felices a todos, es decidir cuál cede y dejar
escrito por qué.
