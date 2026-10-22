"""Embed the supplied catalog and queries, then write top-10 rankings."""

import csv
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PRODUCTS_PATH = Path("data/products.csv")
QUERIES_PATH = Path("data/queries.csv")
OUTPUT_PATH = Path("my_rankings.csv")

MODELS = (
    ("minilm", "sentence-transformers/all-MiniLM-L6-v2",
     "1110a243fdf4706b3f48f1d95db1a4f5529b4d41", ""),
    ("bge_small", "BAAI/bge-small-en-v1.5",
     "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
     "Represent this sentence for searching relevant passages: "),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def top_ten(scores: np.ndarray, product_ids: np.ndarray) -> np.ndarray:
    """Return indices sorted by descending score, then ascending product ID."""
    return np.lexsort((product_ids, -scores))[:10]


def main() -> None:
    products = read_csv(PRODUCTS_PATH)
    queries = read_csv(QUERIES_PATH)
    product_ids = np.asarray([int(row["product_id"]) for row in products])
    product_texts = [row["search_text"] for row in products]
    query_ids = [row["query_id"] for row in queries]

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["query_id", "method", "rank", "product_id"]
        )
        writer.writeheader()

        for method, model_id, revision, query_prefix in MODELS:
            model = SentenceTransformer(model_id, revision=revision, device="cpu")
            started = time.perf_counter()
            product_vectors = model.encode(
                product_texts,
                batch_size=128,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=True,
            ).astype(np.float32, copy=False)
            query_vectors = model.encode(
                [query_prefix + row["query"] for row in queries],
                batch_size=128,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=True,
            ).astype(np.float32, copy=False)
            elapsed = time.perf_counter() - started

            product_lengths = np.linalg.norm(product_vectors, axis=1)
            query_lengths = np.linalg.norm(query_vectors, axis=1)
            print(f"{method} product vector shape: {product_vectors.shape}")
            print(
                f"{method} product vector lengths: "
                f"min={product_lengths.min():.8f}, max={product_lengths.max():.8f}"
            )
            print(f"{method} query vector shape: {query_vectors.shape}")
            print(
                f"{method} query vector lengths: "
                f"min={query_lengths.min():.8f}, max={query_lengths.max():.8f}"
            )
            print(f"{method} encoding time: {elapsed:.2f} seconds")

            for query_id, query_vector in zip(query_ids, query_vectors):
                scores = product_vectors @ query_vector
                for rank, index in enumerate(top_ten(scores, product_ids), start=1):
                    writer.writerow(
                        {
                            "query_id": query_id,
                            "method": method,
                            "rank": rank,
                            "product_id": product_ids[index],
                        }
                    )


if __name__ == "__main__":
    main()
