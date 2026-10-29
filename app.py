"""Aplicación local para revisar abstracts de artículos científicos."""

from hashlib import sha256
from pathlib import Path

import streamlit as st

from pdf_reader import extract_article


st.set_page_config(page_title="Análisis bibliométrico", page_icon="📚", layout="wide")
st.title("Análisis de abstracts científicos")
st.write(
    "Carga los artículos PDF y revisa el título, los autores y el abstract "
    "extraídos de cada archivo."
)


def pdf_sort_key(pdf_path):
    """Ordena los archivos del corpus por su número de artículo."""
    number_text = pdf_path.stem.partition(".")[0]
    if number_text.isdigit():
        return 0, int(number_text), pdf_path.name.lower()
    return 1, 0, pdf_path.name.lower()


if "articles" not in st.session_state:
    st.session_state.articles = []
if "upload_signature" not in st.session_state:
    st.session_state.upload_signature = ""


uploaded_files = st.file_uploader(
    "Carga otros artículos PDF (opcional)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Si no cargas archivos aquí, se usarán automáticamente los PDFs de la carpeta pdfs.",
)

if uploaded_files:
    file_data = [(uploaded_file.name, uploaded_file.getvalue()) for uploaded_file in uploaded_files]
else:
    pdf_folder = Path(__file__).parent / "pdfs"
    file_data = [
        (pdf_path.name, pdf_path.read_bytes())
        for pdf_path in sorted(pdf_folder.glob("*.pdf"), key=pdf_sort_key)
    ]

if file_data:
    signature_source = "".join(
        f"{filename}:{sha256(contents).hexdigest()}" for filename, contents in file_data
    )
    signature = sha256(signature_source.encode("utf-8")).hexdigest()

    if signature != st.session_state.upload_signature:
        articles = []
        for file_index, (filename, contents) in enumerate(file_data):
            try:
                article = extract_article(contents, filename)
            except Exception as error:
                article = {
                    "filename": filename,
                    "title": filename,
                    "authors": "",
                    "abstract": "",
                    "read_error": str(error),
                }
            unique_source = f"{file_index}:{filename}:".encode("utf-8") + contents
            article["id"] = sha256(unique_source).hexdigest()[:12]
            articles.append(article)

        st.session_state.articles = articles
        st.session_state.upload_signature = signature
else:
    st.session_state.articles = []
    st.session_state.upload_signature = ""

articles = st.session_state.articles

if not articles:
    st.info("Carga los PDFs para comenzar. Actualmente no hay artículos cargados.")
    st.stop()

st.success(f"Artículos cargados: {len(articles)}")

with st.expander("Revisar artículos y abstracts", expanded=False):
    for article in articles:
        st.markdown(f"**Archivo:** {article['filename']}")
        if article.get("read_error"):
            st.warning(
                "No se pudo leer este PDF. Puedes pegar el abstract manualmente abajo. "
                f"Detalle: {article['read_error']}"
            )

        title_key = f"title_{article['id']}"
        if title_key not in st.session_state:
            st.session_state[title_key] = article["title"]
        article["title"] = st.text_input("Título", key=title_key)

        authors_key = f"authors_{article['id']}"
        if authors_key not in st.session_state:
            st.session_state[authors_key] = article["authors"]
        article["authors"] = st.text_input("Autores", key=authors_key)

        abstract_key = f"abstract_{article['id']}"
        if abstract_key not in st.session_state:
            st.session_state[abstract_key] = article["abstract"]

        article["abstract"] = st.text_area(
            "Abstract (puedes corregirlo si el PDF se leyó mal)",
            key=abstract_key,
            height=140,
        )

usable_articles = [article for article in articles if article["abstract"].strip()]

if not usable_articles:
    st.warning("No se encontraron abstracts. Revisa los PDFs o pega los abstracts en los campos.")
