"""Extraccion de titulo, autores y abstract de PDFs cientificos."""

import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import pdfplumber

X_TOLERANCE = 1.0
CONECTORES = {"and", "or", "to", "of", "y", "o", "the"}

ACENTOS = {
    "\u00b4": "\u0301", "`": "\u0300", "\u00a8": "\u0308", "\u02dc": "\u0303",
    "\u02c6": "\u0302", "\u02c7": "\u030c", "\u00b8": "\u0327", "\u02ca": "\u0301"
}

# Referencia bibliografica insertada por error dentro de un abstract.
# Es el caso del PDF 14: cita entre parentesis, anio, titulo y paginas.
REFERENCIA_INCRUSTADA = re.compile(
    r"\([A-Z][A-Za-z'\u2019-]+,\s*[A-Z]\.[^()]*?\b(?:19|20)\d{2}\)\."
    r"\s+[A-Z][^()]*?\.\s+[^()]*?,\s*\d+[^()]*?\)"
)


def limpiar(texto):
    """Normaliza Unicode, guiones tipograficos y espacios."""
    texto = texto.replace("\u2010", "-").replace("\u2011", "-")
    texto = re.sub(r"(?<=[A-Za-z])\s?([" + "".join(ACENTOS) + r"])", lambda m: ACENTOS[m.group(1)], texto)
    texto = unicodedata.normalize("NFKC", unicodedata.normalize("NFC", texto))
    texto = re.sub(r"\s+([,;.])", r"\1", texto)
    texto = re.sub(r",\s*,+", ",", texto)
    return re.sub(r"\s+", " ", texto).strip()


def leer_palabras(pagina):
    """Lee palabras y fusiona fragmentos pegados (ligaduras fi/fl, acentos)."""
    raw = pagina.extract_words(x_tolerance=X_TOLERANCE, extra_attrs=["size", "fontname"])
    out = []
    for w in sorted(raw, key=lambda w: w["x0"]):
        w = dict(w)
        destino = None
        for p in reversed(out[-300:]):
            solape = min(p["bottom"], w["bottom"]) - max(p["top"], w["top"])
            if (-1.0 < w["x0"] - p["x1"] < 0.3 and solape > 0.5 * min(p["size"], w["size"])
                    and min(p["size"], w["size"]) / max(p["size"], w["size"]) > 0.85):
                destino = p
                break
        if destino:
            destino["text"] += w["text"]
            destino["x1"] = max(destino["x1"], w["x1"])
            destino["top"] = min(destino["top"], w["top"])
            destino["bottom"] = max(destino["bottom"], w["bottom"])
        else:
            out.append(w)
    return out


def lineas(palabras):
    """Agrupa palabras en lineas basandose en posicion vertical."""
    palabras = sorted(palabras, key=lambda p: (p["top"] + p["bottom"]) / 2)
    res, centro = [], None
    for p in palabras:
        c = (p["top"] + p["bottom"]) / 2
        if centro is None or abs(c - centro) > 0.4 * p["size"]:
            res.append([])
            centro = c
        res[-1].append(p)
    return [sorted(l, key=lambda w: w["x0"]) for l in res]


def ordenar(palabras):
    """Ordena palabras por posicion visual (lineas y luego horizontal)."""
    return [p for l in lineas(palabras) for p in l]


def unir(palabras, vocab=None):
    """Une lineas y decide si un guion de fin de linea se conserva."""
    vocab = vocab or set()
    texto = ""
    for l in lineas(palabras):
        linea = " ".join(w["text"] for w in l)
        if texto.endswith("-") and len(texto) > 1 and texto[-2].isalpha() and linea[:1].islower():
            pre = texto.split()[-1][:-1]
            sig = linea.split()[0]
            if sig.lower() in CONECTORES:
                texto += " " + linea
            else:
                # Si la forma con guion existe en el documento, es un compuesto
                # real (AI-driven, instance-based). Si no, es un corte de linea.
                con_guion = re.sub(r"[^\w-]", "", pre + "-" + sig).lower()
                if con_guion in vocab:
                    texto += linea
                else:
                    texto = texto[:-1] + linea
        else:
            texto += (" " if texto else "") + linea
    return limpiar(texto)


def build_document_vocabulary(pdf):
    """Construye el vocabulario de todo el PDF para decidir guiones."""
    text = " ".join((page.extract_text() or "") for page in pdf.pages)
    text = text.replace("\u2010", "-").replace("\u2011", "-").replace("\u2019", "'")
    return {word.lower() for word in re.findall(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", text)}


def tamano_dominante(palabras):
    """Retorna el tamano de fuente mas comun."""
    return Counter(round(p["size"] * 2) / 2 for p in palabras).most_common(1)[0][0]


def encontrar_abstract(palabras):
    """Encuentra la posicion del encabezado Abstract."""
    ordenadas = ordenar(palabras)
    letras = "ABSTRACT"
    cands = []
    for i, p in enumerate(ordenadas):
        if re.match(r"(abstract|resumen|summary)\b", p["text"], re.I) and \
                (p["size"] > tamano_dominante(palabras) * 0.95 or p["text"].isupper() or p["text"].endswith((":", "."))):
            cands.append((i, p, p))
            break
    for i in range(len(ordenadas) - len(letras) + 1):
        v = ordenadas[i:i + len(letras)]
        if all(len(w["text"]) == 1 for w in v) and "".join(w["text"] for w in v).upper() == letras:
            cands.append((i, v[0], v[-1]))
            break
    if not cands:
        return None, None
    _, a, b = min(cands, key=lambda c: c[0])
    return a, b


def bloques(palabras):
    """Agrupa palabras en bloques verticales."""
    res, ultimo = [], None
    for p in ordenar(palabras):
        c = (p["top"] + p["bottom"]) / 2
        if ultimo is None or c - ultimo > 1.8 * p["size"]:
            res.append([])
        res[-1].append(p)
        ultimo = c
    return res


def extraer_titulo(palabras, vocab, titulo_meta=None):
    """Extrae el titulo del articulo."""
    ini, _ = encontrar_abstract(palabras)
    arriba = [p for p in palabras if ini is None or p["top"] < ini["top"]]
    cuerpo = tamano_dominante(palabras)
    cuenta = Counter(round(p["size"] * 2) / 2 for p in arriba)
    cands = []
    for t in sorted((tt for tt in cuenta if tt > cuerpo * 1.15), reverse=True):
        grupo = [p for p in arriba if abs(p["size"] - t) < 0.5]
        for b in bloques(grupo):
            if len(b) >= 3:
                area = sum(len(p["text"]) for p in b) * t
                simb = sum(1 for p in b if not re.search(r"\w", p["text"]))
                cands.append((unir(b, vocab), max(p["bottom"] for p in b), t, area, simb))
    if not cands:
        grupo = [p for p in palabras if p["size"] == max(w["size"] for w in palabras)]
        return unir(grupo, vocab), max(p["bottom"] for p in grupo)
    if titulo_meta and len(titulo_meta) > 15:
        par = lambda c: SequenceMatcher(None, c[0].lower(), titulo_meta.lower()).ratio()
        mejor = max(cands, key=par)
        if par(mejor) >= 0.6:
            return mejor[0], mejor[1]
    validos = [c for c in cands if c[4] < 2] or cands
    mejor = max(validos, key=lambda c: c[3])
    return mejor[0], mejor[1]


MARCA = re.compile(r"^[a-z\d*∗†‡§¶#]{1,2},?$")


def extraer_autores(palabras, fin_titulo, vocab):
    """Extrae los autores del articulo."""
    ini, _ = encontrar_abstract(palabras)
    cortes = [p["top"] for p in palabras if p["top"] > fin_titulo and p["text"].startswith("Correspondence")]
    if ini is not None and ini["top"] > fin_titulo:
        cortes.append(ini["top"])
    limite = min(cortes, default=fin_titulo + 60)
    zona = [dict(p) for p in ordenar(palabras)
            if fin_titulo < p["top"] < limite - 2 and "italic" not in p["fontname"].lower()]
    if not zona:
        return ""
    ref = max(p["size"] for p in zona if not MARCA.match(p["text"]) or len(p["text"]) > 2) if zona else 0
    grande = [p for p in zona if abs(p["size"] - ref) <= 0.6]
    limpio = []
    for p in grande:
        t = p["text"]
        if t in ("*", "∗") or t.isdigit():
            continue
        if t == ",":
            if limpio and not limpio[-1]["text"].endswith(","):
                limpio[-1]["text"] += ","
            continue
        if MARCA.match(t) and len(t.rstrip(",")) <= 2 and (t.rstrip(",").isdigit() or t.rstrip(",") in "abcdefgh" or t.rstrip(",") in ("*", "∗")):
            if t.endswith(",") and limpio and not limpio[-1]["text"].endswith(","):
                limpio[-1]["text"] += ","
            continue
        limpio.append(p)
    return unir(limpio, vocab).strip(" ,")


FIN = re.compile(r"^(keywords?|key\s*words?|index|palabras|introduction|introducci[oó]n|1\.?)\W*$", re.I)


def extraer_abstract(palabras, vocab):
    """Extrae el abstract del articulo."""
    ini, fin_enc = encontrar_abstract(palabras)
    if ini is None:
        return None
    x_min = ini["x0"] - 3
    todas = lineas([p for p in palabras if p["x0"] >= x_min and p["top"] > ini["top"] + 2])
    fin_top = None
    for l in todas:
        w0 = l[0]
        sig = l[1]["text"] if len(l) > 1 else ""
        if FIN.match(w0["text"]) and (w0["text"] not in ("1", "1.") or re.match(r"introduction|introducci", sig, re.I)):
            fin_top = w0["top"]
            break
        if re.match(r"(keywords?|key words|index terms)\b", w0["text"] + " " + sig, re.I) and w0["text"].lower().startswith(("key", "index")):
            fin_top = w0["top"]
            break
    zona_l = []
    for l in todas:
        if fin_top is not None and l[0]["top"] >= fin_top:
            break
        c = sum((w["top"] + w["bottom"]) / 2 for w in l) / len(l)
        zona_l.append((c, l))
    if fin_top is None and len(zona_l) > 3:
        difs = [b[0] - a[0] for a, b in zip(zona_l, zona_l[1:]) if b[0] - a[0] > 3]
        med = sorted(difs)[len(difs) // 2] if difs else 10
        s0 = zona_l[0][1][0]["size"]
        nuevo = [zona_l[0]]
        for a, b in zip(zona_l, zona_l[1:]):
            if b[0] - a[0] > 2.2 * med or abs(b[1][0]["size"] - s0) > 0.6:
                break
            nuevo.append(b)
        zona_l = nuevo
    zona = [w for _, l in zona_l for w in l]
    zona += [p for p in palabras if p["x0"] > fin_enc["x1"] and abs(p["top"] - ini["top"]) <= 2]
    if not zona:
        return None
    ref = tamano_dominante(zona)
    zona = [p for p in zona if abs(p["size"] - ref) <= 0.5]
    txt = unir(zona, vocab)
    return re.sub(r"^(abstract|resumen|summary)\W*", "", txt, flags=re.I)


def remove_embedded_references(texto):
    """Elimina referencias bibliograficas insertadas dentro del abstract."""
    return REFERENCIA_INCRUSTADA.sub("", texto)


def normalize_abstract(text: str) -> str:
    """Pasa el abstract a minusculas y conserva sus acentos."""
    return unicodedata.normalize("NFC", text.lower())


def _file_id(path):
    """Obtiene el numero inicial del nombre del archivo."""
    match = re.match(r"(\d+)", Path(path).name)
    return int(match.group(1)) if match else None


def extract_pdf(pdf_path):
    """
    Extrae titulo, autores y abstract de un PDF cientifico.

    Returns:
        dict con id, archivo, titulo, autores, abstract y advertencias.
    """
    path = Path(pdf_path)
    record = {
        "id": _file_id(path),
        "file": path.name,
        "title": None,
        "authors": None,
        "abstract": None,
        "warnings": [],
    }
    try:
        with pdfplumber.open(path) as pdf:
            if not pdf.pages:
                record["warnings"].append("PDF sin paginas")
                return record
            palabras = leer_palabras(pdf.pages[0])
            titulo_meta = (pdf.metadata or {}).get("Title")
            vocab = build_document_vocabulary(pdf)
    except Exception as exc:
        record["warnings"].append(f"no se pudo abrir el PDF: {exc}")
        return record

    if not palabras:
        record["warnings"].append("sin capa de texto (posible PDF escaneado)")
        return record

    titulo, fin_titulo = extraer_titulo(palabras, vocab, titulo_meta)
    record["title"] = titulo or None
    record["authors"] = extraer_autores(palabras, fin_titulo, vocab) or None

    abstract = extraer_abstract(palabras, vocab)
    if not abstract:
        record["warnings"].append("no se encontro el abstract")
        return record

    sin_referencias = remove_embedded_references(abstract)
    if sin_referencias != abstract:
        record["warnings"].append("se elimino una referencia bibliografica incrustada")
    record["abstract"] = normalize_abstract(limpiar(sin_referencias))
    return record


def _sort_key(path):
    """Ordena los PDFs por el numero inicial de su nombre."""
    file_id = _file_id(path)
    return (file_id is None, file_id or 0, path.name.lower())


def extract_all_from_directory(directory_path):
    """
    Extrae informacion de todos los PDFs de un directorio.

    Returns:
        Lista de diccionarios ordenada por el numero inicial del archivo.
    """
    pdf_files = sorted(Path(directory_path).glob("*.pdf"), key=_sort_key)
    records = []
    for pdf_file in pdf_files:
        try:
            records.append(extract_pdf(str(pdf_file)))
        except Exception as exc:
            records.append({
                "id": _file_id(pdf_file),
                "file": pdf_file.name,
                "title": None,
                "authors": None,
                "abstract": None,
                "warnings": [f"error inesperado: {exc}"],
            })
    return records


def validate_extraction(records, expected_count=20):
    """Devuelve los problemas detectados en la extraccion del corpus."""
    problems = []
    if len(records) != expected_count:
        problems.append(f"se esperaban {expected_count} PDFs y se encontraron {len(records)}")
    for record in records:
        label = record.get("file") or record.get("id") or "?"
        abstract = record.get("abstract")
        if not abstract:
            problems.append(f"{label}: sin abstract")
            continue
        if not 500 <= len(abstract) <= 3000:
            problems.append(f"{label}: longitud atipica ({len(abstract)} caracteres)")
        if abstract != abstract.lower():
            problems.append(f"{label}: el abstract no esta en minusculas")
        if "keywords" in abstract[-200:].lower():
            problems.append(f"{label}: posible contaminacion con keywords")
    return problems
