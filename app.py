"""Aplicación local para analizar abstracts de artículos científicos."""

from hashlib import sha256
from itertools import combinations
from pathlib import Path

import streamlit as st

from algorithms.similarity.tfidf import create_tfidf_vectors
from algorithms.similarity.tfidf_cosine import cosine_similarity
from algorithms.similarity.tfidf_euclidean import euclidean_similarity
from pdf_reader import extract_article


st.set_page_config(page_title="Análisis bibliométrico", page_icon="📚", layout="wide")
st.title("Análisis de abstracts científicos")
st.write(
    "Carga los artículos PDF, revisa sus abstracts y compara la similitud "
    "entre los artículos."
)


def article_label(article):
    """Crea una etiqueta legible para cada artículo."""
    return f"{article['title']} — {article['filename']}"


def pdf_sort_key(pdf_path):
    """Ordena los archivos del corpus por su número de artículo."""
    number_text = pdf_path.stem.partition(".")[0]
    if number_text.isdigit():
        return 0, int(number_text), pdf_path.name.lower()
    return 1, 0, pdf_path.name.lower()


def get_selected_articles(articles, selected_ids):
    """Devuelve los artículos en el orden elegido en la interfaz."""
    by_id = {article["id"]: article for article in articles}
    return [by_id[article_id] for article_id in selected_ids]


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
        st.session_state.pop("similarity_articles", None)
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
    st.stop()

tabs = st.tabs(["Similitud"])

with tabs[0]:
    st.subheader("Comparar abstracts")
    article_labels = {
        article["id"]: article_label(article) for article in usable_articles
    }
    selected_ids = st.multiselect(
        "Selecciona dos o más artículos",
        options=[article["id"] for article in usable_articles],
        format_func=lambda article_id: article_labels[article_id],
        key="similarity_articles",
    )

    if len(selected_ids) < 2:
        st.info("Selecciona por lo menos dos artículos para calcular similitud.")
    else:
        selected_articles = get_selected_articles(usable_articles, selected_ids)
        all_vectors = create_tfidf_vectors(
            [article["abstract"] for article in usable_articles]
        )
        vector_by_id = {
            article["id"]: all_vectors[index]
            for index, article in enumerate(usable_articles)
        }
        results = []

        for first_article, second_article in combinations(selected_articles, 2):
            first_vector = vector_by_id[first_article["id"]]
            second_vector = vector_by_id[second_article["id"]]
            results.append(
                {
                    "Artículo 1": first_article["title"],
                    "Artículo 2": second_article["title"],
                    "Coseno TF-IDF": cosine_similarity(first_vector, second_vector),
                    "Euclidiana TF-IDF": euclidean_similarity(first_vector, second_vector),
                }
            )

        st.markdown("**Medidas basadas en TF-IDF**")
        st.dataframe(results, width="stretch", hide_index=True)
        st.caption(
            "TF-IDF asigna más peso a los términos poco comunes del corpus. "
            "La similitud euclidiana se calcula como 1 / (1 + distancia)."
        )

        with st.expander("Cómo se calculan las medidas"):
            st.write(
                "**TF-IDF:** cada abstract se convierte en un vector de palabras. "
                "La frecuencia del término se multiplica por su importancia inversa "
                "en el corpus. **Coseno:** mide el ángulo entre dos vectores y vale "
                "1 cuando son idénticos. **Euclidiana:** mide la distancia entre los "
                "vectores y se transforma en similitud con 1 / (1 + distancia)."
            )
