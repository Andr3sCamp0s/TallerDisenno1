"""Un lector de diagramas Mermaid, escrito para este taller.

No dibuja nada: lee el archivo .mmd y lo convierte en nodos, aristas y
subgrafos, para que las pruebas puedan preguntarle cosas al dibujo. Por
ejemplo: «¿hay alguna flecha que salga del dominio hacia infraestructura?».

Soporta lo que este taller necesita y nada más: flowchart y sequenceDiagram.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# ── delimitadores de nodo, de más largo a más corto (el orden importa)
FORMAS = [
    ("[(", ")]", "base_de_datos"),
    ("[[", "]]", "subrutina"),
    ("((", "))", "circulo"),
    ("{{", "}}", "hexagono"),
    ("([", "])", "estadio"),
    ("[", "]", "caja"),
    ("(", ")", "redondeado"),
    ("{", "}", "rombo"),
    (">", "]", "bandera"),
]

# ── flechas, de más largo a más corto
FLECHAS = [r"-\.->", r"-\.-", r"===>", r"==>", r"===", r"==",
           r"--x", r"--o", r"-->", r"----", r"---", r"--"]
RE_FLECHA = re.compile(
    r"\s*(?P<op>" + "|".join(FLECHAS) + r")"
    r"\s*(?:\|(?P<eti>[^|]*)\|)?\s*")
# los identificadores NO llevan guion: «a-->b» se confundiría con el nodo «a--»
RE_ID = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*)")

# Mermaid admite la etiqueta dentro de la flecha («-- texto -->»). Se
# normaliza a la forma con barras antes de analizar, conservando el estilo.
_INLINE = [
    (re.compile(r"-\.\s*([^.|\n]+?)\s*\.->"), r"-.->|\1|"),
    (re.compile(r"==\s+([^=|\n]+?)\s+==+>"), r"==>|\1|"),
    (re.compile(r"--\s+([^-|\n][^|\n]*?)\s+--+>"), r"-->|\1|"),
    (re.compile(r"--\s+([^-|\n][^|\n]*?)\s+--+(?![->])"), r"---|\1|"),
]


def _normalizar_flechas(s: str) -> str:
    for rx, rep in _INLINE:
        s = rx.sub(rep, s)
    return s


@dataclass
class Nodo:
    id: str
    texto: str = ""
    forma: str = "caja"
    subgrafo: str | None = None

    @property
    def etiqueta(self) -> str:
        return self.texto or self.id


@dataclass
class Arista:
    de: str
    a: str
    etiqueta: str = ""
    estilo: str = "solida"
    linea: int = 0


@dataclass
class Mensaje:
    de: str
    a: str
    texto: str = ""
    punteada: bool = False
    linea: int = 0


@dataclass
class Diagrama:
    tipo: str = ""
    ruta: str = ""
    nodos: dict[str, Nodo] = field(default_factory=dict)
    aristas: list[Arista] = field(default_factory=list)
    subgrafos: dict[str, list[str]] = field(default_factory=dict)
    participantes: dict[str, str] = field(default_factory=dict)
    mensajes: list[Mensaje] = field(default_factory=list)
    bloques: set[str] = field(default_factory=set)
    notas: list[str] = field(default_factory=list)
    crudo: str = ""

    # ── consultas que usan las pruebas
    def texto_de(self, nid: str) -> str:
        n = self.nodos.get(nid)
        return n.etiqueta if n else nid

    def subgrafo_de(self, nid: str) -> str | None:
        n = self.nodos.get(nid)
        return n.subgrafo if n else None

    def aristas_de_subgrafo_a(self, origen: str, destino: str) -> list[Arista]:
        """Flechas que salen de un subgrafo y entran en otro. El nombre se
        compara sin distinguir mayúsculas ni tildes."""
        o, d = _norm(origen), _norm(destino)
        fuera = []
        for a in self.aristas:
            so, sd = self.subgrafo_de(a.de), self.subgrafo_de(a.a)
            if so and sd and _norm(so) == o and _norm(sd) == d:
                fuera.append(a)
        return fuera

    def nodos_de_subgrafo(self, nombre: str) -> list[Nodo]:
        n = _norm(nombre)
        return [self.nodos[i] for nom, ids in self.subgrafos.items()
                if _norm(nom) == n for i in ids if i in self.nodos]

    def sin_etiqueta(self) -> list[Arista]:
        return [a for a in self.aristas if not a.etiqueta.strip()]

    def grado(self, nid: str) -> int:
        return sum(1 for a in self.aristas if a.de == nid or a.a == nid)

    def sueltos(self) -> list[str]:
        return [i for i in self.nodos if self.grado(i) == 0]


def _norm(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _leer_nodos(linea: str, dia: Diagrama, subgrafo: str | None) -> str:
    """Saca las declaraciones de nodo de la línea y devuelve la línea con
    solo los identificadores, lista para buscarle flechas."""
    salida, i = [], 0
    while i < len(linea):
        m = re.compile(r"[A-Za-z_][A-Za-z0-9_]*").match(linea, i)
        if not m:
            salida.append(linea[i])
            i += 1
            continue
        nid = m.group(0)
        j = m.end()
        for abre, cierra, forma in FORMAS:
            if linea.startswith(abre, j):
                k = linea.find(cierra, j + len(abre))
                if k == -1:
                    continue
                texto = linea[j + len(abre):k].strip().strip('"').strip("'")
                n = dia.nodos.setdefault(nid, Nodo(nid))
                if texto:
                    n.texto = texto
                n.forma = forma
                if subgrafo and n.subgrafo is None:
                    n.subgrafo = subgrafo
                    dia.subgrafos.setdefault(subgrafo, []).append(nid)
                salida.append(nid)
                i = k + len(cierra)
                break
        else:
            salida.append(nid)
            i = j
    return "".join(salida)


def _leer_aristas(limpia: str, dia: Diagrama, nlinea: int,
                  subgrafo: str | None) -> None:
    pos, anterior = 0, None
    while pos < len(limpia):
        m = RE_ID.match(limpia, pos)
        if not m:
            break
        nid = m.group(1)
        pos = m.end()
        n = dia.nodos.setdefault(nid, Nodo(nid))
        if subgrafo and n.subgrafo is None:
            n.subgrafo = subgrafo
            dia.subgrafos.setdefault(subgrafo, []).append(nid)
        if anterior is not None:
            op, eti = anterior                       # noqa: F821
            estilo = ("punteada" if "." in op else
                      "gruesa" if "=" in op else "solida")
            dia.aristas.append(Arista(prev_id, nid, (eti or "").strip(),
                                      estilo, nlinea))
        prev_id = nid
        mf = RE_FLECHA.match(limpia, pos)
        if not mf:
            break
        anterior = (mf.group("op"), mf.group("eti") or "")
        pos = mf.end()


RE_MENSAJE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*"
    r"(-->>|->>|--\)|-\)|-->|->|--x|-x)\s*"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
RE_PARTICIPANTE = re.compile(
    r"^\s*(?:participant|actor)\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s+as\s+(.+))?\s*$", re.I)


def cargar(ruta: str | Path) -> Diagrama:
    p = Path(ruta)
    if not p.exists():
        raise FileNotFoundError(f"No existe el diagrama {p}")
    texto = p.read_text(encoding="utf-8", errors="replace")
    return leer(texto, str(p))


def leer(texto: str, ruta: str = "") -> Diagrama:
    dia = Diagrama(ruta=ruta, crudo=texto)
    pila: list[str] = []
    dentro_de_bloque_md = False
    for nlinea, cruda in enumerate(texto.splitlines(), 1):
        linea = cruda.split("%%")[0].rstrip()
        if linea.strip().startswith("```"):
            dentro_de_bloque_md = not dentro_de_bloque_md
            continue
        if not linea.strip():
            continue
        bajo = linea.strip().lower()

        if not dia.tipo:
            if bajo.startswith(("flowchart", "graph")):
                dia.tipo = "flowchart"
                continue
            if bajo.startswith("sequencediagram"):
                dia.tipo = "sequenceDiagram"
                continue
            if bajo.startswith(("c4context", "c4container")):
                dia.tipo = "c4"
                continue

        if dia.tipo == "sequenceDiagram":
            mp = RE_PARTICIPANTE.match(linea)
            if mp:
                dia.participantes[mp.group(1)] = (mp.group(2)
                                                  or mp.group(1)).strip()
                continue
            mm = RE_MENSAJE.match(linea)
            if mm:
                for lado in (mm.group(1), mm.group(3)):
                    dia.participantes.setdefault(lado, lado)
                dia.mensajes.append(Mensaje(mm.group(1), mm.group(3),
                                            mm.group(4).strip(),
                                            "--" in mm.group(2), nlinea))
                continue
            for bl in ("alt", "else", "opt", "loop", "par", "critical",
                       "break", "rect"):
                if bajo == bl or bajo.startswith(bl + " "):
                    dia.bloques.add(bl)
            if bajo.startswith("note"):
                dia.notas.append(linea.split(":", 1)[-1].strip())
            continue

        # ---- flowchart
        msub = re.match(r"\s*subgraph\s+(.+?)\s*$", linea, re.I)
        if msub:
            nombre = msub.group(1)
            m2 = re.match(r'^[\w.-]+\s*\[\s*"?(.+?)"?\s*\]$', nombre)
            if m2:
                nombre = m2.group(1)
            pila.append(nombre.strip().strip('"'))
            dia.subgrafos.setdefault(pila[-1], [])
            continue
        if bajo == "end":
            if pila:
                pila.pop()
            continue
        if bajo.startswith(("style ", "classdef", "class ", "linkstyle",
                            "click ", "direction ")):
            continue
        actual = pila[-1] if pila else None
        limpia = _normalizar_flechas(_leer_nodos(linea, dia, actual))
        _leer_aristas(limpia, dia, nlinea, actual)
    return dia
