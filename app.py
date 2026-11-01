"""Aplicación local para analizar abstracts de artículos científicos."""

from hashlib import sha256
from itertools import combinations
from pathlib import Path

import streamlit as st

from algorithms.similarity.embedding_cosine import embedding_cosine_similarity
from algorithms.similarity.embedding_euclidean import embedding_euclidean_similarity
from algorithms.similarity.jaccard import jaccard_similarity
from algorithms.similarity.levenshtein import levenshtein_similarity
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


@st.cache_resource
def load_embedding_model():
    """Carga el modelo una sola vez y lo reutiliza durante la sesión."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


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
            first_text = first_article["abstract"]
            second_text = second_article["abstract"]
            first_vector = vector_by_id[first_article["id"]]
            second_vector = vector_by_id[second_article["id"]]
            results.append(
                {
                    "Artículo 1": first_article["title"],
                    "Artículo 2": second_article["title"],
                    "Levenshtein (palabras)": levenshtein_similarity(first_text, second_text),
                    "Coseno TF-IDF": cosine_similarity(first_vector, second_vector),
                    "Jaccard": jaccard_similarity(first_text, second_text),
                    "Euclidiana TF-IDF": euclidean_similarity(first_vector, second_vector),
                }
            )

        st.markdown("**Cuatro métodos clásicos**")
        st.dataframe(results, width="stretch", hide_index=True)
        st.caption(
            "Levenshtein compara palabras; TF-IDF asigna más peso a términos poco comunes. "
            "La similitud euclidiana se calcula como 1 / (1 + distancia)."
        )

        with st.expander("Cómo se calculan los métodos clásicos"):
            st.write(
                "**Levenshtein:** una matriz de programación dinámica cuenta inserciones, "
                "eliminaciones y reemplazos entre secuencias de palabras. Se normaliza por "
                "la longitud mayor. **TF-IDF:** frecuencia de término por importancia "
                "inversa en el corpus; luego se comparan los vectores con coseno o distancia "
                "euclidiana. **Jaccard:** palabras compartidas dividido por palabras distintas."
            )

        st.markdown("**Dos medidas con embeddings de lenguaje**")
        st.write(
            "Se usa un modelo preentrenado para transformar cada abstract en un vector denso. "
            "La similitud coseno y la distancia euclidiana son dos medidas distintas sobre "
            "esos embeddings. La primera ejecución puede descargar el modelo."
        )

        embedding_input = "".join(
            f"{article['id']}:{article['abstract']}" for article in selected_articles
        )
        embedding_signature = sha256(embedding_input.encode("utf-8")).hexdigest()

        if st.button("Calcular similitud con embeddings", key="calculate_embeddings"):
            try:
                with st.spinner("Cargando el modelo y calculando embeddings..."):
                    model = load_embedding_model()
                    embeddings = model.encode(
                        [article["abstract"] for article in selected_articles],
                        convert_to_numpy=True,
                    )

                embedding_results = []
                for first_index, second_index in combinations(range(len(selected_articles)), 2):
                    first_vector = embeddings[first_index]
                    second_vector = embeddings[second_index]

                    embedding_results.append(
                        {
                            "Artículo 1": selected_articles[first_index]["title"],
                            "Artículo 2": selected_articles[second_index]["title"],
                            "Coseno de embeddings": embedding_cosine_similarity(
                                first_vector, second_vector
                            ),
                            "Euclidiana de embeddings": embedding_euclidean_similarity(
                                first_vector, second_vector
                            ),
                        }
                    )

                st.session_state.embedding_results = embedding_results
                st.session_state.embedding_signature = embedding_signature
            except Exception as error:
                st.error(
                    "No se pudo cargar el modelo de embeddings. Comprueba que instalaste "
                    "requirements.txt y que hay conexión a Internet para la descarga inicial. "
                    f"Detalle: {error}"
                )

        if st.session_state.get("embedding_signature") == embedding_signature:
            st.dataframe(
                st.session_state.embedding_results,
                width="stretch",
                hide_index=True,
            )
