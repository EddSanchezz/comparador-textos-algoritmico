"""Extracción sencilla de datos y abstracts desde archivos PDF."""

import os


STOP_HEADINGS = (
    "keywords",
    "key words",
    "index terms",
    "introduction",
    "background",
    "related work",
    "related literature",
    "method",
    "methods",
    "methodology",
    "materials and methods",
)


def abstract_label_end(line):
    """Devuelve dónde termina la etiqueta Abstract, incluso si está espaciada."""
    text = line.lstrip()
    start = len(line) - len(text)
    label = "abstract"

    # Formas comunes: "Abstract: texto" y "Abstract texto".
    if text[: len(label)].lower() == label:
        end = len(label)
        if end == len(text) or text[end].isspace() or text[end] in ":.-–—":
            return start + end

    compact_text = "".join(character.lower() for character in text if character.isalnum())
    if compact_text.endswith(label):
        # Algunos PDF combinan la etiqueta con otro encabezado.
        return len(line)

    # Algunas revistas escriben el encabezado como "A B S T R A C T".
    position = 0
    for letter_index, letter in enumerate(label):
        if position >= len(text) or text[position].lower() != letter:
            return None
        position += 1
        if letter_index < len(label) - 1:
            while position < len(text) and text[position].isspace():
                position += 1

    end = position
    if end == len(text) or text[end].isspace() or text[end] in ":.-–—":
        return start + end

    return None


def remove_abstract_label(line):
    """Quita el encabezado y la puntuación anterior al abstract."""
    label_end = abstract_label_end(line)
    if label_end is None:
        return line.strip()

    remaining = line[label_end:].strip()
    while remaining and remaining[0] in ":.-–—":
        remaining = remaining[1:].strip()
    return remaining


def is_abstract_heading(line):
    """Comprueba si la línea contiene la etiqueta Abstract."""
    return abstract_label_end(line) is not None


def is_section_heading(line):
    """Reconoce secciones comunes, incluso si tienen número o letras espaciadas."""
    compact_line = "".join(character.lower() for character in line if character.isalnum())

    # Omite números como "1." o "2" antes del encabezado.
    while compact_line and compact_line[0].isdigit():
        compact_line = compact_line[1:]

    for heading in STOP_HEADINGS:
        compact_heading = "".join(
            character for character in heading if character.isalnum()
        )
        if compact_line == compact_heading or compact_line.startswith(compact_heading):
            return True

    return False


def is_keyword_heading(line):
    """Identifica palabras clave para omitirlas si aparecen antes del abstract."""
    compact_line = "".join(character.lower() for character in line if character.isalnum())
    return compact_line.startswith("keywords") or compact_line.startswith("indexterms")


def is_metadata_line(line):
    """Reconoce datos de autor que algunos PDF ponen antes del abstract."""
    lower_line = line.strip().lower()
    return (
        lower_line.startswith("correspondence")
        or lower_line.startswith("* correspondence")
        or lower_line.startswith("email:")
        or lower_line.startswith("department of")
        or "@" in lower_line
    )


def extract_abstract(lines):
    """Lee el abstract hasta encontrar el siguiente encabezado de sección."""
    abstract_lines = []
    found_abstract = False
    skipping_keywords = False

    for line in lines:
        cleaned_line = line.strip()
        if not found_abstract:
            if is_abstract_heading(cleaned_line):
                found_abstract = True
                first_part = remove_abstract_label(cleaned_line)
                if first_part:
                    abstract_lines.append(first_part)
            continue

        if is_keyword_heading(cleaned_line):
            if abstract_lines:
                break
            skipping_keywords = True
            continue

        if skipping_keywords:
            word_count = len(cleaned_line.split())
            has_sentence_end = any(mark in cleaned_line for mark in ".?!")
            if word_count < 8 and not has_sentence_end:
                continue
            skipping_keywords = False

        if not abstract_lines and is_metadata_line(cleaned_line):
            continue

        if not cleaned_line:
            if abstract_lines:
                abstract_lines.append("")
            continue

        if is_section_heading(cleaned_line):
            break

        abstract_lines.append(cleaned_line)

    while abstract_lines and not abstract_lines[-1]:
        abstract_lines.pop()

    return " ".join(abstract_lines).strip()


def extract_abstract_from_blocks(blocks):
    """Usa el primer bloque de texto como alternativa para PDF poco comunes."""
    found_heading = False

    for block in blocks:
        block_text = block[4].strip()
        if not block_text:
            continue

        if not found_heading:
            if is_abstract_heading(block_text):
                found_heading = True
                text_after_label = remove_abstract_label(block_text)
                if text_after_label and not is_keyword_heading(text_after_label):
                    return text_after_label
            continue

        if is_keyword_heading(block_text) or is_metadata_line(block_text):
            continue
        if is_section_heading(block_text):
            return ""

        # El primer bloque evita incluir por error el resto del artículo.
        return " ".join(block_text.split())

    return ""


def words_in_text(text):
    """Separa el texto en palabras minúsculas."""
    words = []
    current_word = []

    for character in text.lower():
        if character.isalnum():
            current_word.append(character)
        elif current_word:
            words.append("".join(current_word))
            current_word = []

    if current_word:
        words.append("".join(current_word))

    return words


def find_title_end_line(lines, title):
    """Encuentra la última línea de un título que ocupa varias líneas."""
    title_words = words_in_text(title)
    if not title_words:
        return None

    words_seen = []
    for line_index, line in enumerate(lines):
        if is_abstract_heading(line):
            break

        words_seen.extend(words_in_text(line))
        if len(words_seen) >= len(title_words):
            title_start = len(words_seen) - len(title_words)
            if words_seen[title_start:] == title_words:
                return line_index

    return None


def extract_authors_after_title(lines, title):
    """Lee los autores que aparecen entre el título y las afiliaciones."""
    title_end_line = find_title_end_line(lines, title)
    if title_end_line is None:
        return ""

    author_lines = []
    affiliation_words = (
        "department",
        "university",
        "faculty",
        "institute",
        "school",
        "college",
        "correspondence",
        "email",
        "copyright",
        "license",
        "received:",
    )

    for line in lines[title_end_line + 1 : title_end_line + 6]:
        cleaned_line = line.strip().strip("|,* ")
        lower_line = cleaned_line.lower()
        if not cleaned_line or is_abstract_heading(cleaned_line):
            break
        if any(word in lower_line for word in affiliation_words) or "@" in lower_line:
            break

        author_lines.append(cleaned_line)

    return " ".join(author_lines)


def title_from_filename(filename):
    """Usa el nombre del archivo como título si los metadatos no sirven."""
    title = os.path.splitext(os.path.basename(filename))[0]
    first_part, separator, remaining_title = title.partition(". ")
    if separator and first_part.isdigit():
        title = remaining_title
    return title


def extract_article(pdf_bytes, filename):
    """Extrae el título, los autores y el abstract del PDF."""
    import pymupdf

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        page_text = [page.get_text("text") for page in pdf]
        first_page_blocks = pdf[0].get_text("blocks", sort=True) if pdf.page_count else []
        metadata = pdf.metadata or {}

    all_text = "\n".join(page_text)
    lines = all_text.splitlines()
    title = (metadata.get("title") or "").replace("\ufeff", "").strip()
    authors = (metadata.get("author") or "").replace("\ufeff", "").strip()

    invalid_title_words = ("untitled", "unknown", "proof", "doi.org")
    if not title or any(word in title.lower() for word in invalid_title_words):
        title = title_from_filename(filename)

    if not authors or authors.lower() in ("unknown", "none") or authors.lower().startswith("and "):
        authors = extract_authors_after_title(lines, title)

    abstract = extract_abstract(lines)
    if not abstract or len(abstract.split()) > 900:
        block_abstract = extract_abstract_from_blocks(first_page_blocks)
        if block_abstract:
            abstract = block_abstract

    return {
        "filename": filename,
        "title": title,
        "authors": authors,
        "abstract": abstract,
    }
