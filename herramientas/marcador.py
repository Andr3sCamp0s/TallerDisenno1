"""Marcador del taller de arquitectura · CaféTrace.

Corre las pruebas etapa por etapa, le dice qué le falta y deja constancia
de la corrida en EVIDENCIA/registro.jsonl.

    python herramientas/marcador.py            # todas las etapas
    python herramientas/marcador.py 2          # solo la etapa 2

Cada corrida agrega una línea al registro con la fecha, la huella de su
trabajo en ese momento y un sello encadenado con la corrida anterior. Ese
registro muestra cómo fue avanzando: qué decidió primero, qué dibujó
después, cuándo se puso verde cada etapa.

Al terminar cada etapa copie el sello que imprime el marcador en la línea
**Sello:** de esa etapa, dentro de DECISIONES.md.

No edite EVIDENCIA/registro.jsonl a mano: los sellos están encadenados y
se nota.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIA = RAIZ / "EVIDENCIA"
REGISTRO = EVIDENCIA / "registro.jsonl"

ETAPAS = {
    0: "Del caso a los drivers",
    1: "Contexto · qué es sistema y qué no",
    2: "Contenedores · cómo se despliega",
    3: "Componentes y puertos",
    4: "Estilo arquitectónico",
    5: "Integración y fallas",
    6: "Registro de decisiones",
}

# Lo que cada etapa le pide entregar, además del código.
ENTREGABLES = {
    0: ("DRIVERS.md", ["D0.1", "D0.2"], None),
    1: ("diagramas/etapa1-contexto.mmd", ["D1.1", "D1.2"], 1),
    2: ("diagramas/etapa2-contenedores.mmd", ["D2.1", "D2.2", "D2.3"], 2),
    3: ("diagramas/etapa3-componentes.mmd", ["D3.1", "D3.2"], 3),
    4: (None, ["D4.1", "D4.2"], None),
    5: ("diagramas/etapa5-secuencia.mmd", ["D5.1", "D5.2"], 5),
    6: ("ADR/", ["D6.1"], None),
}

VERDE, ROJO, GRIS, AMBAR, FIN = ("\033[32m", "\033[31m", "\033[90m",
                                 "\033[33m", "\033[0m")


# ──────────────────────────────────────────────────────────────── huella
def archivos_del_estudiante() -> list[Path]:
    salida: list[Path] = []
    for carpeta in ("cafetrace", "mis_pruebas"):
        base = RAIZ / carpeta
        if base.exists():
            salida += sorted(base.rglob("*.py"))
    for carpeta in ("diagramas", "ADR"):
        base = RAIZ / carpeta
        if base.exists():
            salida += sorted(base.rglob("*.mmd")) + sorted(base.rglob("*.md"))
    for doc in ("DECISIONES.md", "DRIVERS.md", "ESTUDIANTE.txt"):
        p = RAIZ / doc
        if p.exists():
            salida.append(p)
    base = RAIZ / "BOSQUEJOS"
    if base.exists():
        salida += sorted(p for p in base.iterdir()
                         if p.is_file() and p.suffix.lower() != ".md")
    return sorted(set(salida))


def huella_del_trabajo() -> str:
    """SHA-256 de todo lo que usted escribe y dibuja."""
    h = hashlib.sha256()
    for p in archivos_del_estudiante():
        h.update(p.relative_to(RAIZ).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def leer_estudiante() -> dict:
    p = RAIZ / "ESTUDIANTE.txt"
    datos = {"nombre": "", "carne": ""}
    if p.exists():
        for linea in p.read_text(encoding="utf-8").splitlines():
            if ":" in linea:
                k, v = linea.split(":", 1)
                k = k.strip().lower().replace("é", "e")
                if k in datos:
                    datos[k] = v.strip()
    return datos


# ───────────────────────────────────────────────────────────────── etapas
def correr_etapa(n: int) -> tuple[int, int, list[str]]:
    """Devuelve (en verde, por resolver, nombres de las que fallan)."""
    base = [sys.executable, "-m", "pytest", "-o", "addopts=", "-m", f"etapa{n}",
            "-q", "--no-header", "-p", "no:cacheprovider"]

    recolecta = subprocess.run(base + ["--collect-only"], cwd=RAIZ,
                               capture_output=True, text=True)
    lineas = recolecta.stdout.splitlines()
    total = sum(1 for l in lineas if "::" in l)
    if total == 0:
        total = sum(int(m.group(1)) for m in
                    (re.search(r":\s*(\d+)\s*$", l) for l in lineas) if m)

    corrida = subprocess.run(base + ["--tb=no"], cwd=RAIZ,
                             capture_output=True, text=True)
    salida = corrida.stdout + corrida.stderr
    caidas = []
    for l in salida.splitlines():
        if l.startswith(("FAILED", "ERROR")):
            ruta = (l.split(None, 1)[1] if " " in l else l).split(" - ")[0]
            caidas.append(ruta.split("::")[-1].strip())
    return max(0, total - len(caidas)), len(caidas), caidas


# ───────────────────────────────────────────────── qué falta, en español
RE_SECCION = re.compile(r"^###\s*(D\d\.\d)\s*·?\s*(.*)$", re.M)


def decisiones_en_blanco(codigos: list[str]) -> list[str]:
    p = RAIZ / "DECISIONES.md"
    if not p.exists():
        return codigos
    texto = p.read_text(encoding="utf-8", errors="replace")
    partes = RE_SECCION.split(texto)
    vistos: dict[str, str] = {}
    for i in range(1, len(partes), 3):
        vistos[partes[i]] = re.split(r"^###\s", partes[i + 2], flags=re.M)[0]
    faltan = []
    for c in codigos:
        cuerpo = vistos.get(c, "")
        m = re.search(r"\*\*Decisi[^*]*\*\*:?(.*?)(?=\*\*[A-ZÁÉÍÓÚ]|\Z)",
                      cuerpo, re.S | re.I)
        if not (m and m.group(1).strip()):
            faltan.append(c)
    return faltan


def falta_bosquejo(etapa: int | None) -> bool:
    if etapa is None:
        return False
    base = RAIZ / "BOSQUEJOS"
    if not base.exists():
        return True
    for ext in ("jpg", "jpeg", "png", "webp", "pdf", "heic"):
        if list(base.glob(f"etapa{etapa}.{ext}")):
            return False
    return True


def pendientes(n: int) -> list[str]:
    archivo, codigos, etapa_bosquejo = ENTREGABLES[n]
    avisos = []
    if archivo and not (RAIZ / archivo).exists():
        avisos.append(f"falta {archivo}")
    sin_responder = decisiones_en_blanco(codigos)
    if sin_responder:
        avisos.append("sin responder: " + ", ".join(sin_responder))
    if falta_bosquejo(etapa_bosquejo):
        avisos.append(f"falta BOSQUEJOS/etapa{etapa_bosquejo}.jpg (la foto "
                      f"del dibujo a mano)")
    return avisos


# ───────────────────────────────────────────────────────────────── sellos
def ultimo_sello() -> str:
    if not REGISTRO.exists():
        return "genesis"
    lineas = [l for l in REGISTRO.read_text(encoding="utf-8").splitlines()
              if l.strip()]
    return json.loads(lineas[-1])["sello"] if lineas else "genesis"


def sellar(registro: dict, anterior: str) -> str:
    cuerpo = json.dumps(registro, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((anterior + cuerpo).encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────── main
def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] not in [str(n) for n in ETAPAS]:
        print(f"  Etapa «{sys.argv[1]}» no existe. Son de la 0 a la 6.")
        return 2
    etapas = [int(sys.argv[1])] if len(sys.argv) > 1 else list(ETAPAS)
    estudiante = leer_estudiante()

    print()
    print("  TALLER DE ARQUITECTURA · CaféTrace")
    print(f"  {estudiante['nombre'] or '(escriba su nombre en ESTUDIANTE.txt)'}"
          f"   carné {estudiante['carne'] or '—'}")
    print("  " + "─" * 66)

    resultados, total_p, total_f = {}, 0, 0
    for n in etapas:
        p, f, caidas = correr_etapa(n)
        resultados[f"etapa{n}"] = [p, f]
        total_p, total_f = total_p + p, total_f + f
        if f == 0 and p > 0:
            marca, color = "verde", VERDE
        elif p == 0 and f == 0:
            marca, color = "sin pruebas", GRIS
        else:
            marca, color = f"{f} por resolver", ROJO
        barra = "█" * p + "░" * f
        print(f"  {color}Etapa {n}{FIN}  {ETAPAS[n]:<34} "
              f"{color}{barra:<16}{FIN} {color}{marca}{FIN}")
        if f:
            for aviso in pendientes(n):
                print(f"           {AMBAR}· {aviso}{FIN}")
            for nombre in caidas[:4]:
                print(f"           {GRIS}· {nombre}{FIN}")
            if len(caidas) > 4:
                print(f"           {GRIS}· … y {len(caidas) - 4} más{FIN}")

    print("  " + "─" * 66)
    print(f"  {total_p} pruebas en verde · {total_f} por resolver")

    EVIDENCIA.mkdir(exist_ok=True)
    previas = (sum(1 for l in REGISTRO.read_text(encoding="utf-8").splitlines()
                   if l.strip()) if REGISTRO.exists() else 0)
    registro = {
        "n": previas + 1,
        "cuando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estudiante": estudiante["nombre"],
        "carne": estudiante["carne"],
        "etapas_corridas": etapas,
        "huella": huella_del_trabajo(),
        "resultados": resultados,
    }
    anterior = ultimo_sello()
    registro["anterior"] = anterior
    registro["sello"] = sellar(registro, anterior)
    with REGISTRO.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"  corrida #{registro['n']} registrada")
    print(f"  SELLO: {registro['sello'][:16]}")
    if len(etapas) == 1:
        print(f"  Si acaba de cerrar la etapa {etapas[0]}, pegue ese sello en "
              f"DECISIONES.md.")
    else:
        print("  Pegue el sello en la etapa que acaba de cerrar, en "
              "DECISIONES.md.")
    print()
    return 0 if total_f == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
