"""Aplicación local para analizar abstracts de artículos científicos."""

from hashlib import sha256
from itertools import combinations
from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt
import streamlit as st

from algorithms.clustering.average_linkage import average_linkage
from algorithms.clustering.complete_linkage import complete_linkage
from algorithms.clustering.hierarchical import pairwise_cosine_distances
from algorithms.clustering.silhouette import best_silhouette_cut
from algorithms.clustering.single_linkage import single_linkage
from algorithms.dendrogram import draw_dendrogram
from algorithms.search.boyer_moore import boyer_moore_search
from algorithms.search.kmp import kmp_search
from algorithms.search.rabin_karp import rabin_karp_search
from algorithms.similarity.embedding_cosine import embedding_cosine_similarity
from algorithms.similarity.embedding_euclidean import embedding_euclidean_similarity
from algorithms.similarity.jaccard import jaccard_similarity
from algorithms.similarity.levenshtein import levenshtein_similarity
from algorithms.similarity.tfidf_cosine import cosine_similarity
from algorithms.similarity.tfidf_euclidean import euclidean_similarity
from algorithms.similarity.tfidf import create_tfidf_vectors
from pdf_reader import extract_article


st.set_page_config(page_title="Análisis bibliométrico", page_icon="📚", layout="wide")
st.title("Análisis de abstracts científicos")
st.write(
    "Carga los artículos PDF, revisa sus abstracts y ejecuta los algoritmos "
    "de similitud, agrupamiento y búsqueda."
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
        st.session_state.pop("clustering_results", None)
        st.session_state.pop("clustering_names", None)
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
corpus_content = "".join(
    f"{article['id']}:{article['title']}:{article['abstract']}"
    for article in usable_articles
)
clustering_input_signature = sha256(corpus_content.encode("utf-8")).hexdigest()

if (
    "clustering_results" in st.session_state
    and st.session_state.get("clustering_input_signature") != clustering_input_signature
):
    st.session_state.pop("clustering_results", None)
    st.session_state.pop("clustering_names", None)

if not usable_articles:
    st.warning("No se encontraron abstracts. Revisa los PDFs o pega los abstracts en los campos.")
    st.stop()

tabs = st.tabs(["Similitud", "Agrupamiento", "Búsqueda de patrones"])

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
        classic_results = []

        for first_article, second_article in combinations(selected_articles, 2):
            first_text = first_article["abstract"]
            second_text = second_article["abstract"]
            first_vector = vector_by_id[first_article["id"]]
            second_vector = vector_by_id[second_article["id"]]
            classic_results.append(
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
        st.dataframe(classic_results, width="stretch", hide_index=True)
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

with tabs[1]:
    st.subheader("Agrupamiento jerárquico de abstracts")
    st.write(
        "Se calcula la distancia coseno entre los vectores TF-IDF y se implementan "
        "Single, Complete y Average Linkage desde cero."
    )

    if len(usable_articles) < 2:
        st.info("Se necesitan por lo menos dos abstracts para agrupar artículos.")
    elif st.button("Ejecutar los tres agrupamientos", key="run_clustering"):
        article_vectors = create_tfidf_vectors(
            [article["abstract"] for article in usable_articles]
        )
        distance_matrix = pairwise_cosine_distances(article_vectors)
        clustering_results = {}

        with st.spinner("Construyendo los tres árboles jerárquicos..."):
            clustering_methods = (
                ("single", single_linkage),
                ("complete", complete_linkage),
                ("average", average_linkage),
            )
            for linkage_name, clustering_method in clustering_methods:
                merges = clustering_method(distance_matrix)
                cluster_count, score = best_silhouette_cut(distance_matrix, merges)
                clustering_results[linkage_name] = {
                    "merges": merges,
                    "cluster_count": cluster_count,
                    "score": score,
                }

        st.session_state.clustering_results = clustering_results
        st.session_state.clustering_names = [article["title"] for article in usable_articles]
        st.session_state.clustering_input_signature = clustering_input_signature

    if "clustering_results" in st.session_state:
        results = st.session_state.clustering_results
        names = st.session_state.clustering_names
        score_rows = [
            {
                "Método": linkage.title(),
                "Número de grupos elegido": result["cluster_count"],
                "Silhouette": result["score"],
            }
            for linkage, result in results.items()
        ]
        st.markdown("**Comparación de coherencia (mayor Silhouette es mejor)**")
        st.dataframe(score_rows, width="stretch", hide_index=True)

        for linkage, result in results.items():
            st.markdown(f"**{linkage.title()} Linkage**")
            figure = draw_dendrogram(
                names,
                result["merges"],
                f"Dendrograma — {linkage.title()} Linkage",
            )
            st.pyplot(figure)
            plt.close(figure)
            st.caption(
                f"Corte sugerido por Silhouette: {result['cluster_count']} grupos. "
                f"Coeficiente: {result['score']:.3f}."
            )

    with st.expander("Cómo funciona el agrupamiento"):
        st.write(
            "Cada artículo empieza en su propio grupo. En cada paso se unen los dos grupos "
            "más cercanos: Single usa la menor distancia entre sus miembros, Complete la "
            "mayor y Average el promedio. El dendrograma dibuja cada unión. Para comparar "
            "los cortes se calcula Silhouette, que contrasta la distancia dentro del grupo "
            "con la distancia al grupo vecino. Esta implementación sencilla tarda "
            "aproximadamente O(n³), adecuada para el corpus de 20 artículos."
        )

with tabs[2]:
    st.subheader("Coincidencia exacta de cadenas")
    pattern = st.text_input(
        "Patrón de búsqueda",
        placeholder="Por ejemplo: generative AI",
        key="search_pattern",
    )
    ignore_case = st.checkbox("Ignorar mayúsculas y minúsculas", value=True)
    search_signature_text = f"{pattern}:{ignore_case}:" + "".join(
        f"{article['id']}:{article['abstract']}" for article in usable_articles
    )
    search_signature = sha256(search_signature_text.encode("utf-8")).hexdigest()

    if st.button("Buscar en todos los abstracts", key="run_search"):
        if not pattern:
            st.warning("Escribe un patrón no vacío.")
            st.session_state.pop("search_results", None)
            st.session_state.pop("search_signature", None)
        else:
            search_pattern = pattern.lower() if ignore_case else pattern
            search_results = []

            for article in usable_articles:
                search_text = article["abstract"]
                if ignore_case:
                    search_text = search_text.lower()

                algorithms_to_run = (
                    ("KMP", kmp_search),
                    ("Boyer-Moore", boyer_moore_search),
                    ("Rabin-Karp", rabin_karp_search),
                )

                for algorithm_name, search_function in algorithms_to_run:
                    start_time = perf_counter()
                    positions = search_function(search_text, search_pattern)
                    elapsed_time = perf_counter() - start_time
                    search_results.append(
                        {
                            "Artículo": article["title"],
                            "Algoritmo": algorithm_name,
                            "Ocurrencias": len(positions),
                            "Posiciones (desde 1)": [position + 1 for position in positions],
                            "Tiempo (ms)": elapsed_time * 1000,
                        }
                    )

            st.session_state.search_results = search_results
            st.session_state.search_signature = search_signature

    if st.session_state.get("search_signature") == search_signature:
        st.dataframe(
            st.session_state.search_results,
            width="stretch",
            hide_index=True,
        )

    with st.expander("Cómo funcionan los algoritmos de búsqueda"):
        st.write(
            "**KMP** calcula prefijos que también son sufijos para evitar repetir "
            "comparaciones. **Boyer-Moore** compara desde el final del patrón y desplaza "
            "según el último lugar del carácter que no coincidió. **Rabin-Karp** calcula "
            "un hash que se actualiza al mover la ventana; verifica los caracteres si los "
            "hashes coinciden para evitar falsos resultados por colisión. Los tiempos "
            "mostrados son solo de búsqueda, sin incluir la carga de PDFs. En teoría, "
            "KMP cuesta O(n + m); Rabin-Karp cuesta O(n + m) en promedio y O(n·m) en el "
            "peor caso; Boyer-Moore con la regla implementada puede llegar a O(n·m). "
            "Aquí n es el largo del texto y m el del patrón."
        )
