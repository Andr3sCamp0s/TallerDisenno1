"""Piezas compartidas por las pruebas del taller. No lo modifique."""
from __future__ import annotations

import ast
import importlib
import re
import unicodedata
from pathlib import Path

import pytest

from . import mermaid

RAIZ = Path(__file__).resolve().parent.parent
PAQUETE = RAIZ / "cafetrace"

# tecnología que NO puede aparecer en el nivel 1 (contexto)
TECNOLOGIA = ["http", "https", "rest", "json", "xml", "sql", "postgres",
              "mysql", "fastapi", "django", "flask", "kafka", "rabbit",
              "redis", "grpc", "soap", "docker", "kubernetes", "s3",
              "lambda", "jwt", "oauth", "websocket", "graphql", "mqtt",
              "ftp", "sftp", "api rest"]

# medios válidos para etiquetar una flecha en el nivel 2 (contenedores)
PROTOCOLOS = ["http", "https", "rest", "json", "sql", "jdbc", "archivo",
              "ftp", "sftp", "csv", "grpc", "amqp", "mqtt", "evento",
              "eventos", "cola", "mensaje", "mensajeria", "mensajería",
              "webhook", "websocket", "lee", "escribe", "publica",
              "consume", "descarga", "sube", "consulta", "graphql", "soap",
              "correo", "smtp", "bluetooth", "usb", "sincroniza"]


def sin_tildes(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


# ─────────────────────────────────────────────────────────────── archivos
def documento(nombre: str) -> Path | None:
    p = RAIZ / nombre
    return p if p.exists() and p.stat().st_size > 0 else None


def texto_de(nombre: str) -> str:
    p = documento(nombre)
    return p.read_text(encoding="utf-8", errors="replace") if p else ""


def bosquejo(etapa: int) -> Path | None:
    for ext in ("jpg", "jpeg", "png", "webp", "pdf", "heic"):
        for p in (RAIZ / "BOSQUEJOS").glob(f"etapa{etapa}.{ext}"):
            return p
    return None


def diagrama(archivo: str) -> mermaid.Diagrama:
    p = RAIZ / "diagramas" / archivo
    if not p.exists():
        pytest.fail(f"Falta el diagrama diagramas/{archivo}.")
    if "PLANTILLA-SIN-RESOLVER" in p.read_text(encoding="utf-8",
                                               errors="replace"):
        pytest.fail(
            f"diagramas/{archivo} todavía trae la marca «PLANTILLA-SIN-"
            f"RESOLVER». Dibuje el suyo y borre esa línea. Las reglas que "
            f"revisa el marcador están en los comentarios del archivo, y "
            f"esas sí se quedan.")
    d = mermaid.cargar(p)
    if not d.tipo:
        pytest.fail(
            f"diagramas/{archivo} no empieza con «flowchart» ni con "
            f"«sequenceDiagram». Mermaid necesita esa primera línea para "
            f"saber qué está dibujando.")
    return d


# ─────────────────────────────────────────────────────────── DECISIONES.md
RE_SECCION = re.compile(r"^###\s*(D\d\.\d)\s*·?\s*(.*)$", re.M)
RE_SELLO_ETAPA = re.compile(
    r"^##\s*Etapa\s*(\d)(.*?)(?=^##\s|\Z)", re.M | re.S)


def decisiones() -> dict[str, dict[str, str]]:
    texto = texto_de("DECISIONES.md")
    if not texto:
        pytest.fail("Falta DECISIONES.md, o está vacío.")
    partes = RE_SECCION.split(texto)
    salida: dict[str, dict[str, str]] = {}
    for i in range(1, len(partes), 3):
        codigo, titulo, cuerpo = partes[i], partes[i + 1], partes[i + 2]
        cuerpo = re.split(r"^###\s", cuerpo, flags=re.M)[0]

        def campo(nombre: str) -> str:
            # el corte es el siguiente rótulo, y la comparación distingue
            # mayúsculas: dentro de una decisión puede haber **negritas**
            m = re.search(rf"\*\*{nombre}[^*]*\*\*:?(.*?)"
                          rf"(?=\*\*(?:Decisi|Justificaci|Sello|Conflicto)"
                          rf"|\Z)", cuerpo, re.S)
            return " ".join(m.group(1).split()) if m else ""
        salida[codigo] = {"titulo": titulo.strip(),
                          "decision": campo("Decisi"),
                          "justificacion": campo("Justificaci"),
                          "crudo": cuerpo}
    return salida


def sello_de_etapa(n: int) -> str:
    for m in RE_SELLO_ETAPA.finditer(texto_de("DECISIONES.md")):
        if int(m.group(1)) == n:
            s = re.search(r"\*\*Sello[^*]*\*\*:?\s*`?([0-9a-f]{16,64})`?",
                          m.group(2), re.I)
            return s.group(1) if s else ""
    return ""


def exige(codigo: str, minimo: int = 180) -> dict[str, str]:
    """Trae una decisión ya verificada: respondida y justificada."""
    d = decisiones().get(codigo)
    if d is None:
        pytest.fail(f"No encuentro la sección «### {codigo}» en "
                    f"DECISIONES.md. No borre ni renombre los encabezados.")
    if not d["decision"]:
        pytest.fail(f"{codigo} no tiene Decisión. La pregunta era: "
                    f"{d['titulo']}")
    if len(d["justificacion"]) < minimo:
        pytest.fail(
            f"{codigo} tiene {len(d['justificacion'])} caracteres de "
            f"justificación y se esperan más de {minimo}. Una decisión de "
            f"arquitectura sin razones escritas no se puede revisar ni "
            f"discutir: es justo lo que este taller evalúa.")
    if not cita_requisito(d["justificacion"]):
        pytest.fail(
            f"La justificación de {codigo} no señala ningún requisito ni "
            f"driver. Escriba «R-7», «QA-2» o «requisito 16» donde se "
            f"apoye. Una justificación que no se ancla en el caso vale lo "
            f"mismo que una opinión.")
    return d


def cita_requisito(texto: str) -> bool:
    return bool(re.search(r"\b(QA|R|FP)\s*-\s*\d+|requisito\s*#?\s*\d+|"
                          r"#\s*\d{1,2}\b", texto or "", re.I))


def opcion(codigo: str, permitidas: tuple[str, ...]) -> str:
    """La decisión, normalizada a una de las opciones permitidas."""
    d = exige(codigo)
    bruto = sin_tildes(d["decision"])
    for p in permitidas:
        if sin_tildes(p) in bruto:
            return p
    pytest.fail(
        f"{codigo} responde «{d['decision'][:60]}», y se esperaba una de "
        f"estas: {', '.join(permitidas)}. Escriba la palabra exacta en la "
        f"línea de Decisión; la explicación va en la justificación.")


# ────────────────────────────────────────────────────────────────── código
def modulo(ruta: str):
    try:
        return importlib.import_module(ruta)
    except ModuleNotFoundError as e:
        pytest.fail(f"No existe todavía el módulo {ruta} ({e}).")
    except Exception as e:                                # noqa: BLE001
        pytest.fail(f"{ruta} no se puede importar: {type(e).__name__}: {e}")


def fuente(ruta: Path) -> str:
    """El código sin docstrings ni comentarios: lo que de verdad se ejecuta."""
    try:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    except SyntaxError as e:
        pytest.fail(f"{ruta.name} tiene un error de sintaxis en la línea "
                    f"{e.lineno}: {e.msg}")
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and ast.get_docstring(nodo):
            nodo.body = nodo.body[1:]
    return ast.unparse(arbol)


def fuente_del_paquete(sub: str) -> dict[str, str]:
    base = PAQUETE / sub
    if not base.exists():
        return {}
    return {p.relative_to(RAIZ).as_posix(): fuente(p)
            for p in sorted(base.rglob("*.py"))}
