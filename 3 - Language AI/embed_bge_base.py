"""Build CPU-only BGE-base rankings for the Case 3 validation experiment."""

import csv
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PRODUCTS_PATH = Path("data/products.csv")
QUERIES_PATH = Path("data/queries.csv")
OUTPUT_PATH = Path("my_change.csv")
METHOD = "bge_base"
MODEL_ID = "BAAI/bge-base-en-v1.5"
REVISION = "a5beb1e3e68b9ab74eb54cfd186867f64f240e1a"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def top_ten(scores: np.ndarray, product_ids: np.ndarray) -> np.ndarray:
    """Sort by descending similarity, breaking ties with lower product IDs."""
    return np.lexsort((product_ids, -scores))[:10]


def main() -> None:
    products = read_csv(PRODUCTS_PATH)
    # Test queries are deliberately excluded: this Q4 experiment is validation-only.
    queries = [row for row in read_csv(QUERIES_PATH) if row["split"] != "test"]
    product_ids = np.asarray([int(row["product_id"]) for row in products])

    model = SentenceTransformer(MODEL_ID, revision=REVISION, device="cpu")
    started = time.perf_counter()
    product_vectors = model.encode(
        [row["search_text"] for row in products],
        batch_size=128,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32, copy=False)
    query_vectors = model.encode(
        [QUERY_PREFIX + row["query"] for row in queries],
        batch_size=128,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32, copy=False)
    elapsed = time.perf_counter() - started

    product_lengths = np.linalg.norm(product_vectors, axis=1)
    query_lengths = np.linalg.norm(query_vectors, axis=1)
    storage_bytes = product_vectors.nbytes
    print(f"{METHOD} model revision: {REVISION}")
    print(f"{METHOD} product vector shape: {product_vectors.shape}")
    print(
        f"{METHOD} product vector lengths: "
        f"min={product_lengths.min():.8f}, max={product_lengths.max():.8f}"
    )
    print(f"{METHOD} query vector shape: {query_vectors.shape}")
    print(
        f"{METHOD} query vector lengths: "
        f"min={query_lengths.min():.8f}, max={query_lengths.max():.8f}"
    )
    print(f"{METHOD} product-vector storage: {storage_bytes:,} bytes")
    print(f"{METHOD} encoding time: {elapsed:.2f} seconds")

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["query_id", "method", "rank", "product_id"]
        )
        writer.writeheader()
        for query, vector in zip(queries, query_vectors):
            scores = product_vectors @ vector
            for rank, index in enumerate(top_ten(scores, product_ids), start=1):
                writer.writerow(
                    {
                        "query_id": query["query_id"],
                        "method": METHOD,
                        "rank": rank,
                        "product_id": product_ids[index],
                    }
                )


if __name__ == "__main__":
    main()
