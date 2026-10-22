# Case 3 — Owen Simon

## Q1 — Embed the catalog

### 1a The data

#### Product Catalog

| Metric | Count |
|---|---:|
| Total products | 42,994 |
| Products with blank or missing `product_class` | 2,852 |

#### Queries by Split

| Split | Queries |
|---|---:|
| Development | 79 |
| Validation | 200 |
| Test | 200 |

#### Relevance Labels by Split

| Split | Exact | Partial | Irrelevant |
|---|---:|---:|---:|
| Development | 4,623 | 23,222 | 8,736 |
| Validation | 11,134 | 63,712 | 29,615 |

#### Development Query Example

Query ID: `1`  
Query: `smart coffee table`

| Label | Product ID | Product Name | Product Class |
|---|---:|---|---|
| Exact | 5235 | adoni coffee table | Coffee & Cocktail Tables |
| Irrelevant | 4033 | serving tray with handles - wood bamboo trays for food breakfast party , tea coffee table ottoman decor set of 3 | Decorative Trays |

The Adoni Coffee Table is labeled Exact because it matches the requested product type, although its missing description makes it difficult to confirm whether it includes smart functionality. In contrast, the Serving Tray with Handles is labeled Irrelevant, which seems reasonable because it is a decorative tray rather than a coffee table.

### 1b My embeddings

| Method | Model ID | Revision (first 7 characters) | Query prefix | Product vectors (rows × dimensions) | Number format | Smallest and largest vector length | Raw bytes | Encoding time and computer |
|---|---|---|---|---|---|---|---|---|
| minilm | sentence-transformers/all-MiniLM-L6-v2 | 1110a24 | None | 42,994 × 384 | float32 | 0.99999982 to 1.00000012 | 66,038,784 | 305.34 seconds; Intel Core i7-1165G7 @ 2.80 GHz (CPU) |
| bge_small | BAAI/bge-small-en-v1.5 | 5c38ec7 | Represent this sentence for searching relevant passages: | 42,994 × 384 | float32 | 0.99999988 to 1.00000012 | 66,038,784 | 629.84 seconds; Intel Core i7-1165G7 @ 2.80 GHz (CPU) |

Although MiniLM and BGE-small both produce vectors containing 384 numbers, each model represents text differently, so their vectors cannot be directly compared. Normalizing the vectors ensures that each has a length of approximately 1, allowing the dot product, which multiplies corresponding values and adds them together, to measure similarity without being influenced by differences in vector length.

### 1c Sanity check and AI use

#### Development Query 1: `smart coffee table`

| Rank | MiniLM Product ID | MiniLM Product Name | BGE-small Product ID | BGE-small Product Name |
|--:|--:|:--|--:|:--|
| 1 | 33698 | smart coffee table with storage | 33698 | smart coffee table with storage |
| 2 | 295 | buchheit coffee table | 34828 | metre solid wood coffee table |
| 3 | 294 | aalst coffee table | 34711 | coffee table with storage |
| 4 | 39692 | calmar coffee table | 5132 | solid coffee table |
| 5 | 40418 | dev coffee table | 26951 | solid coffee table |

#### Software Versions

| Package | Version |
|--|:--:|
| Python | 3.13.9 |
| torch | 2.11.0+cpu |
| sentence-transformers | 5.4.1 |
| transformers | 4.57.6 |
| NumPy | 2.4.4 |

Both models produced sensible rankings for the query "smart coffee table," with each ranking "smart coffee table with storage" first. The remaining results were also coffee tables, although their product names did not explicitly indicate smart functionality.

I used Codex to help develop the Python script that generated embeddings and ranked products using MiniLM and BGE-small. I independently ran the script, verified the ranking file's format using `score.py`, and examined the top-five products to evaluate whether the rankings appeared relevant to the search query.

## Q2 — Score it, choose, then test once

### 2a Validation table

| **Method** | **n** | **nDCG@10** | **Exact@1 (95% interval)** | **judged@10** | **nDCG@10 difference vs. keyword (paired 95% interval)** | **Queries better / worse than keyword** |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|
| keyword | 200 | 0.675 | 0.450 (0.38–0.52) | 0.891 | — | — |
| minilm | 200 | 0.736 | 0.480 (0.41–0.55) | 0.878 | +0.061 (+0.024 to +0.097) | 91 / 58 |
| bge_small | 200 | 0.739 | 0.525 (0.46–0.59) | 0.881 | +0.064 (+0.028 to +0.100) | 91 / 60 |

| Method | Recipe nDCG@10 | My nDCG@10 | Absolute Difference |
|:--|:--:|:--:|:--:|
| keyword | 0.6750 | 0.6750 | 0.0000 |
| minilm | 0.7360 | 0.7357 | 0.0003 |
| bge_small | 0.7390 | 0.7393 | 0.0003 |

Both MiniLM and BGE-small matched the recipe's expected validation nDCG@10 values within the specified tolerance of 0.003, with absolute differences of 0.0003 for each model.

### 2b One query by hand

**Validation Query:** 0  
**Preferred Method:** BGE-small

The relevance gains are assigned as follows: 

- Exact = 1
- Partial = 0.5
- Irrelevant = 0

The rank discount is calculated using:

$$
\text{Discount}_r = \frac{1}{\log_2(r+1)}
$$

| Rank | Relevance | Gain | Discount | Discounted Gain |
|:--:|:--|:--:|:--:|:--:|
| 1 | Exact | 1 | 1.0000 | 1.0000 |
| 2 | Exact | 1 | 0.6309 | 0.6309 |
| 3 | Partial | 0.5 | 0.5000 | 0.2500 |
| 4 | Partial | 0.5 | 0.4307 | 0.2153 |
| 5 | Exact | 1 | 0.3869 | 0.3869 |
| 6 | Partial | 0.5 | 0.3562 | 0.1781 |
| 7 | Partial | 0.5 | 0.3333 | 0.1667 |
| 8 | Exact | 1 | 0.3155 | 0.3155 |
| 9 | Partial | 0.5 | 0.3010 | 0.1505 |
| 10 | Partial | 0.5 | 0.2891 | 0.1445 |

#### Step 1: Calculate DCG@10

$$
DCG@10 = \sum_{r=1}^{10} \frac{gain_r}{\log_2(r+1)}
$$

$$
DCG@10 = 1.0000 + 0.6309 + 0.2500 + 0.2153 + 0.3869 + 0.1781 + 0.1667 + 0.3155 + 0.1505 + 0.1445
$$

$$
DCG@10 \approx 3.4384
$$

#### Step 2: Calculate ideal DCG@10

Validation query 0 has 39 products labeled Exact and 2,977 labeled Partial. Since at least ten Exact products are available, the ideal top-ten ranking consists entirely of Exact products, each with a gain of 1.

$$
IDCG@10 = \sum_{r=1}^{10} \frac{1}{\log_2(r+1)}
$$

$$
IDCG@10 = 1.000 + 0.6309 + 0.5000 + 0.4307 + 0.3869 + 0.3562 + 0.3333 + 0.3155 + 0.3010 + 0.2891
$$

$$
IDCG@10 \approx 4.5436
$$

#### Step 3: Calculate nDCG@10

$$
nDCG@10 = \frac{DCG@10}{IDCG@10}
$$

$$
nDCG@10 \approx \frac{3.4384}{4.5436} \approx 0.757
$$

**Verification:** The manually calculated nDCG@10 of approximately **0.757** matches the BGE-small result for validation query 0 in `outputs/validation_per_query.csv`, allowing for rounding.

### 2c My choice

```
{
  "method": "bge_small",
  "reason": "BGE-small achieved the highest validation nDCG@10 (0.739) and Exact@1 (0.525) among the three methods. Its nDCG@10 improvement over keyword search was 0.064, with a paired 95% confidence interval of 0.028 to 0.100.",
  "saved_at_utc": "2026-10-20T20:27:22Z",
  "validation_metrics_sha256": "9506a6f8459f9b258f8dece8c8d5f0fe5dabf86c49238e61711519ecbadbd874"
}
```

I selected BGE-small based on its validation performance. Neither I nor my AI agent had viewed any test relevance labels or test evaluation results before saving `selection.json`. The selection was made using only development and validation data.

### 2d Test once

| Method | n | nDCG@10 | Exact@1 (95% interval) | judged@10 | nDCG@10 difference vs. keyword (paired 95% interval) | Queries better / worse than keyword |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|
| keyword | 200 | 0.685 | 0.425 (0.36–0.49) | 0.851 | — | — |
| bge_small | 200 | 0.710 | 0.460 (0.39–0.53) | 0.832 | +0.025 (-0.002 to +0.053) | 82 / 69 |

BGE-small continued to outperform keyword search on the test set, but the improvement in nDCG@10 decreased from 0.064 on validation to 0.025 on test. The test 95% confidence interval (-0.002 to +0.053) also includes zero, meaning there is insufficient evidence to conclude that BGE-small consistently outperforms keyword search. The smaller improvement may reflect differences between the validation and test queries, as well as the possibility that BGE-small's validation performance was partly due to random variation.

The 200 test queries give Marisol an estimate of how well BGE-small performs on new searches and how much it improves over keyword search. However, they cannot guarantee that the improvement will hold across all future queries or establish that the method is better for every type of search.

## Q3 — Read the results

### 3a Where the methods disagree

#### Largest BGE-small advantages

| Query ID | Query | BGE-small nDCG@10 | Keyword nDCG@10 | Difference |
|---:|---|---:|---:|---:|
| 168 | printers | 1.000 | 0.000 | +1.000 |
| 345 | oriental vanity | 0.927 | 0.000 | +0.927 |
| 68 | nautical platters | 0.953 | 0.110 | +0.843 |

- **Query 168, "printers":** The keyword baseline returned unrelated fallback products such as a solid wood platform bed and a slow cooker when keyword matching did not fill its top ten, while BGE-small returned printer-related products, including "printer stand" and "home office printer stand."
- **Query 345, "oriental vanity":** Keyword search focused on "oriental" and returned area rugs, while BGE-small retrieved vanity products such as "ilani vanity set with stool and mirror" and "choi vanity."
- **Query 68, "nautical platters":** Keyword search returned unrelated nautical products such as an upholstered headboard and anchor wall décor, while BGE-small retrieved serving dishes such as "boat shaped platter" and "hiltner seashell platter."

#### Largest keyword advantages

| Query ID | Query | BGE-small nDCG@10 | Keyword nDCG@10 | Difference |
|---:|---|---:|---:|---:|
| 219 | trinaic towel rod | 0.069 | 1.000 | -0.931 |
| 360 | huntsville sectional sofa | 0.305 | 1.000 | -0.695 |
| 416 | wayfair coffee table | 0.417 | 1.000 | -0.583 |

- **Query 219, "trinaic towel rod":** Keyword search returned towel bars and racks, including "single rod and multi-rod 25'' fixture mounted towel bar," while BGE-small focused on similarly spelled "Trinsic" products, many of which were unjudged.
- **Query 360, "huntsville sectional sofa":** Keyword search returned judged Partial sectional sofas, including "sectional sofa in gray linen," while BGE-small retrieved several unjudged patio sectionals, such as "alp patio sectional with cushions."
- **Query 416, "wayfair coffee table":** Keyword search returned coffee tables such as "kalmus coffee table," while BGE-small prioritized unrelated Wayfair Basics products, including a tablecloth and stackable storage drawers.

#### Failure types

The six queries reveal several types of search errors:

| Failure type | Queries | Explanation |
|---|---|---|
| Keyword fallback behavior | 168 | With few or no keyword matches, the baseline filled results using low product IDs, producing unrelated products. |
| Wrong product category | 345, 68 | Keyword search matched only part of the query and returned products outside the intended category. |
| Unusual spelling or product name | 219 | BGE-small appeared to associate "trinaic" with the similarly spelled "Trinsic" product line rather than prioritizing judged towel rods. |
| Product-category confusion | 360 | BGE-small retrieved several patio sectionals instead of prioritizing judged indoor sectional sofas. |
| Brand or keyword overemphasis | 416 | BGE-small focused on the Wayfair name and retrieved products that were not coffee tables. |

Overall, BGE-small was more successful when the query required recognizing the intended product category rather than simply matching individual words. However, its weaker results suggest that unusual names and brand-related terms can distract it from the requested product type. Several of its poorly performing results were also unjudged, which limits how confidently their relevance can be assessed.

### 3b Unjudged results

#### Validation judged@10

| Method | judged@10 |
|:--|--:|
| keyword | 0.891 |
| bge_small | 0.881 |

Keyword search had a slightly higher judged@10 rate (89.1%) than BGE-small (88.1%), indicating that a slightly larger proportion of its top-ten results had relevance labels.

#### My Relevance Judgments

The following ten products appeared at rank 1 in BGE-small's validation results but did not have relevance labels. I reviewed their names, product classes, and available descriptions to assign my own judgments.

| Query ID | Query | Product ID | Product name and class | Description beginning | My judgment | Why |
|---:|---|---:|---|---|---|---|
| 4 | chair and a half recliner | 33723 | side chair (Dining Chairs) | the sole designs dining chairs is a simple yet attractive option to use in any room of your home | Irrelevant | A dining chair is not the same as a recliner. |
| 23 | stoneford end tables white and wood | 3078 | saltford twisted teak side table (End Tables) | *(blank)* | Partial | Matches the table type and wood material, but not the specified name or color. |
| 29 | bathroom vanity knobs | 20628 | bathroom/vanity mirror (Wall & Accent Mirrors) | evoking a distressed barn wood aesthetic, this mirror shines in coastal or farmhouse ensembles | Irrelevant | A mirror is not a vanity knob. |
| 42 | toddler couch fold out | 10429 | convertible toddler bed (Kids Beds) | *(blank)* | Partial | Related to toddler furniture, but it is a bed rather than a fold-out couch. |
| 161 | accent chair recliner | 25898 | wingback chair (Accent Chairs) | this classic wing chair provides the perfect refuge for relaxation with a tall back and side panels | Partial | Matches the accent-chair category, but reclining functionality is not confirmed. |
| 219 | trinaic towel rod | 10114 | trinsic® wall mounted robe hook (Towel & Robe Hooks) | the design was inspired by the sleek elegance of modern european design | Irrelevant | A robe hook is not a towel rod. |
| 222 | small loving roomtables | 22607 | small ghost buster nightstand (End Tables\|Nightstands) | night table version of the ghost buster commode. a simple flexible object which is at home in any corner of the house | Partial | A nightstand/end table could serve a similar purpose as a small living room table. |
|  308 | led 60 | 28537 | 60w light bulb (Light Bulbs) | *(blank)* | Partial | Matches the likely wattage and product type, but LED is not specified. |
| 348 | one alium way | 15417 | alioth 1 door accent cabinet (Accent Chests / Cabinets) | perfect as a living room accent piece, hallway storage, or an entryway surface | Irrelevant | The product name resembles the query, but a match to the intended brand or collection is not established. |
| 383 | minnestrista | 18806 | kalista bed (class unavailable) | *(blank)* | Irrelevant | No clear connection between the product and the query. |

Of the ten unjudged products I examined, five appeared partially relevant, while the other five were irrelevant. This suggests that some potentially relevant products may receive a relevance score of zero simply because they lack human judgments. However, because I only examined unjudged products returned by BGE-small, I cannot determine whether missing relevance labels affect its evaluation more than keyword search.

Keyword search had a slightly higher validation judged@10 (0.891) than BGE-small (0.881), although this does not necessarily indicate better search relevance. While BGE-small achieved a higher nDCG@10 on both validation and test data, its test improvement over keyword search was smaller, with a 95% confidence interval that included zero (-0.002 to +0.053). These findings would not change my selection of BGE-small as the preferred embedding model, but they suggest that there is insufficient evidence to justify immediately replacing keyword search. I would recommend further evaluation before implementing BGE-small across BRG Direct's search system.

### 3c Where keyword still wins

| Query ID | Query | Query Type | Keyword nDCG@10 | BGE-small nDCG@10 |
|---:|---|---|---:|---:|
| 219 | trinaic towel rod | Specific or misspelled product name | 1.000 | 0.069 |
| 416 | wayfair coffee table | Brand-related product search | 1.000 | 0.417 |

For "trinaic towel rod," keyword search returned ten Partial matches, including "single rod and multi-rod 25'' fixture mounted towel bar" and "single rod wall mounted towel rack." BGE-small instead focused on similarly named "Trinsic" products, including robe hooks, towel rings, and towel bars, most of which were unjudged. Although this suggests that BGE-small may struggle with unusual or misspelled product names, the missing relevance labels make it difficult to determine whether its retrieved products were actually less relevant.

For "wayfair coffee table," keyword search returned ten Partial coffee table matches, including "kalmus coffee table" and "aalst coffee table." BGE-small returned some coffee tables but also prioritized unrelated Wayfair Basics products, including tablecloths, storage drawers, and stools. This suggests that BGE-small placed too much emphasis on the brand-related term rather than the requested product type.

These examples suggest that BRG Direct should retain keyword search for queries involving specific product names, brands, or collections, especially when matching the requested product type is important. Keyword search may also serve as a useful alternative when semantic search focuses on similar names or brand terms instead of the products customers are actually looking for.

## Q4 — One improvement, and what it would take to run

### 4a My improvement

With assistance from Codex, I tested a larger embedding model, `BAAI/bge-base-en-v1.5`, using the new method name `bge_base`. Unlike BGE-small, which produces 384-dimensional vectors, BGE-base produces 768-dimensional vectors. I expected the larger model to better represent differences in product information and search queries, potentially improving the relevance of retrieved products.

The new method used the same text processing, query prefix, normalization, and ranking approach as BGE-small. The model revision was pinned to `a5beb1e3e68b9ab74eb54cfd186867f64f240e1a`. No relevance labels or test queries were used to develop the method, and the new rankings were saved to `my_change.csv`.

#### Validation Results

| Method | nDCG@10 | judged@10 | Difference vs. BGE-small (paired 95% interval) |
|---|---:|---:|---:|
| bge_small | 0.7393 | 0.8805 | — |
| bge_base | 0.7414 | 0.8825 | +0.0021 (-0.0122 to +0.0157) |

BGE-base achieved a slightly higher validation nDCG@10 (0.7414) than BGE-small (0.7393), an improvement of 0.0021. It performed better on 77 queries and worse on 65. However, the paired 95% confidence interval includes zero, so the results do not provide strong evidence that BGE-base consistently outperforms BGE-small.

#### Computational Cost

| Measure | BGE-small | BGE-base |
|---|---:|---:|
| Vector dimensions | 384 | 768 |
| Product vectors | 42,994 | 42,994 |
| Number format | float32 | float32 |
| Raw product-vector storage | 66,038,784 bytes | 132,077,568 bytes |
| Encoding time | 629.84 seconds | 2,242.69 seconds |

BGE-base required twice as much raw product-vector storage and approximately 3.6 times as much encoding time as BGE-small. Although the larger model produced a small improvement in validation performance, the additional computational cost was substantial. Based on these results, I would favor retaining BGE-small unless further testing demonstrates a more meaningful improvement from BGE-base.

### 4b Running it for BRG Direct

Using BGE-small with 384-dimensional float32 vectors, storing embeddings for 2 million products would require approximately 3.07 GB of raw vector storage (2,000,000 × 384 × 4 bytes). Based on my measured encoding time of 629.84 seconds for 42,994 products, embedding the entire catalog would take approximately 8.14 hours on a computer like mine, assuming processing time scales proportionally. These estimates exclude indexing overhead and other storage requirements.

BRG Direct should generate embeddings whenever new products are added or existing product text used for embedding is updated. Only the affected products would need to be re-embedded. However, changing the embedding model would require re-embedding the entire catalog to ensure all product vectors are generated consistently.

Before launching a new index, I would evaluate its nDCG@10 on a held-out set of labeled search queries and compare it against the existing index to check for a decline in search relevance. After launch, I would monitor how often shoppers click on products in the search results to help determine whether the new search method is returning relevant products.

## Q5 — Memo to Marisol Vance

**To:** Marisol Vance

**From:** Owen Simon

**Subject:** Recommendation for BRG Direct's Site Search 

I recommend that BRG Direct conduct a pilot study to evaluate the benefits and drawbacks of switching from keyword matching to embedding-based search. I compared search results across three methods: keyword matching, MiniLM, and BGE-small. On the validation set, BGE-small performed best, achieving an nDCG@10 of 0.739, compared with 0.736 for MiniLM and 0.675 for keyword matching. However, on the test set, BGE-small achieved an nDCG@10 of 0.710, an improvement of only 0.025 over keyword matching (0.685). The 95% confidence interval for this difference (-0.002 to +0.053) includes zero, meaning the test results do not establish that BGE-small consistently outperforms keyword matching.

BGE-small performed better at recognizing the intended product category rather than simply matching individual words. For example, BGE-small returned more relevant products for searches such as "oriental vanity" and "nautical platters." However, keyword matching performed better for certain searches involving specific product names or brands, such as "trinaic towel rod" and "wayfair coffee table." I also found that some products returned by BGE-small did not have relevance labels, which may have affected its evaluation scores.

I also tested a larger embedding model, BGE-base, to determine whether it could improve search results. Although BGE-base achieved a slightly higher validation nDCG@10 than BGE-small, the improvement was only 0.0021, with a confidence interval that included zero (-0.0122 to +0.0157). BGE-base also required twice as much vector storage and approximately 3.6 times as much encoding time.

Based on these findings, I recommend BGE-small for a live pilot rather than the larger model. For BRG Direct's estimated catalog of 2 million products, BGE-small would require approximately 3.07 GB of raw vector storage and 8.14 hours of embedding time on a device like mine. Junho Park should oversee the implementation and operation of the search system. During the pilot, I would compare BGE-small against keyword search and use search-to-product click-through rate as the primary measure of success. I would stop the pilot if BGE-small's click-through rate is meaningfully lower than keyword search's, indicating that shoppers are less likely to interact with its results. If BGE-small improves click-through rates without introducing major relevance problems, BRG Direct could consider expanding its use.

## Code

### `embed_and_rank.py`

```python
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
```

### `embed_bge_base.py`

```python
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
```

## AI record

### AI Interaction Record

**User prompt:**

> Work only with the files in this folder. Read VD3_QUESTIONS.md, "The recipe" section, and follow it exactly. Do not open data/labels_test.csv. Write one Python script, embed_and_rank.py, that embeds data/products.csv's search_text and data/queries.csv's query with both pinned models on the CPU, normalizes the vectors, ranks products by dot product, and writes my_rankings.csv with the columns query_id, method, rank, product_id for all queries and both methods (method names minilm and bge_small). Print each model's vector shape, vector lengths, and encoding time. Then run python score.py check --rankings my_rankings.csv. I will write my own judgments and memo.

**Codex response:**

Created `embed_and_rank.py` and generated `my_rankings.csv`. The script used the pinned MiniLM and BGE-small revisions, CPU encoding, normalized float32 vectors, the required BGE query prefix, and product-ID tie-breaking. The run reported MiniLM product vectors `(42994, 384)`, vector lengths `0.99999982–1.00000012`, and encoding time `305.34s`; BGE-small product vectors `(42994, 384)`, vector lengths `0.99999988–1.00000012`, and encoding time `629.84s`. `python score.py check --rankings my_rankings.csv` reported complete development, validation, and test coverage for both methods and `Format OK.` Codex did not open `data/labels_test.csv`.

**User prompt:**

> Help me collect the factual information required for Q1a of my Case 3 assignment. Using the CSV files in the data folder: 1) Count the total number of products in products.csv, 2) Count the products with a blank or missing product_class, 3) Count the queries in each split: development, validation, and test, 4) Count the relevance labels by grade (Exact, Partial, Irrelevant), separately for development and validation. Then, select the development query with query_id = 1. Report the query text and identify one product labeled Exact and one labeled Irrelevant. Include each product's ID, name, class, and relevance label. Do not open or inspect test relevance labels. Do not modify embed_and_rank.py, my_rankings.csv, or any existing output files.

**Codex response:**

Q1a factual results: 42,994 products; 2,852 products with a blank or missing `product_class`; and 79 development, 200 validation, and 200 test queries. Development labels were 4,623 Exact, 23,222 Partial, and 8,736 Irrelevant. Validation labels were 11,134 Exact, 63,712 Partial, and 29,615 Irrelevant. Development query 1 was `smart coffee table`. The selected Exact product was ID 5235, `adoni coffee table`, class `Coffee & Cocktail Tables`; the selected Irrelevant product was ID 4033, `serving tray with handles - wood bamboo trays for food breakfast party , tea coffee table ottoman decor set of 3`, class `Decorative Trays`.

**User prompt:**

> Can you retrieve the product information from data/products.csv for product IDs 5235 and 4033. Display important product fields, including their descriptions and any features. Do not interpret their relevance labels or modify any files.

**Codex response:**

`products.csv` had the fields `product_id`, `product_name`, `product_class`, `category_hierarchy`, `product_description`, and `search_text`; it had no separate features field. Codex did not Do not interpret product relevance labels.

| Product ID | Product name | Product description | Product class |
|---:|---|---|---|
| 5235 | adoni coffee table | (blank) | Coffee & Cocktail Tables |
| 4033 | serving tray with handles - wood bamboo trays for food breakfast party , tea coffee table ottoman decor set of 3 | these surfing trays are an exceptional value . they are lightweight and well designed and balanced . the stack inside of each other so there do not take up much cabinet space . | Decorative Trays |

**User prompt:**

> Help me collect the information required for Q1c of my Case 3 assignment. Using my_rankings.csv, data/queries.csv, and data/products.csv, retrieve the top five products ranked by each embedding model (minilm and bge_small) for development query `query_id` = 1. For each model, display a table containing: 1) rank 1-5, Product ID, Product Name, Product Class, and similarity score if available. Also report the installed versions of Python, torch, sentence-transformers, transformers, and NumPy. Do not rerun the embedding models, inspect test relevance labels, or modify any files. Display the results directly in the terminal.

**Codex response:**

For query 1, `smart coffee table`, MiniLM ranked: (1) 33698, `smart coffee table with storage`, `Coffee & Cocktail Tables`; (2) 295, `buchheit coffee table`, blank class; (3) 294, `aalst coffee table`, blank class; (4) 39692, `calmar coffee table`, blank class; and (5) 40418, `dev coffee table`, `Coffee & Cocktail Tables`. BGE-small ranked: (1) 33698, `smart coffee table with storage`, `Coffee & Cocktail Tables`; (2) 34828, `metre solid wood coffee table`, blank class; (3) 34711, `coffee table with storage`, blank class; (4) 5132, `solid coffee table`, `Coffee & Cocktail Tables`; and (5) 26951, `solid coffee table`, `Coffee & Cocktail Tables`. Similarity scores were not stored in `my_rankings.csv`, so Codex did not recompute them. The installed versions were Python 3.13.9, torch 2.11.0+cpu, sentence-transformers 5.4.1, transformers 4.57.6, and NumPy 2.4.4. Codex did not rerun embeddings, inspect test labels, or modify files.

**User prompt:**

> Can you help me calculate the nDCG@10 of bge_small using: python score.py show --query-id 0 --rankings my_rankings.csv. List the ten gains, multiply each by its rank discount, and add them up (DCG). The ideal DCG comes from the query's best ten labels: show prints how many Exact and Partial products the query has, so fill the ten slots with Exact (1) first, then Partial (0.5). Compare the manually calculated result with the corresponding bge_small row in outputs/validation_per_query.csv.

**Codex response:**

For query 0, bge_small gains are:

| Rank | Gain | Discount \(1/\log_2(rank+1)\) | Contribution |
|---:|---:|---:|---:|
| 1 | 1.0 | 1.000000 | 1.000000 |
| 2 | 1.0 | 0.630930 | 0.630930 |
| 3 | 0.5 | 0.500000 | 0.250000 |
| 4 | 0.5 | 0.430677 | 0.215338 |
| 5 | 1.0 | 0.386853 | 0.386853 |
| 6 | 0.5 | 0.356207 | 0.178104 |
| 7 | 0.5 | 0.333333 | 0.166667 |
| 8 | 1.0 | 0.315465 | 0.315465 |
| 9 | 0.5 | 0.301030 | 0.150515 |
| 10 | 0.5 | 0.289065 | 0.144532 |

DCG@10 = 3.438403.

The query has 39 Exact labels, so its ideal top 10 is ten Exact products:

- IDCG@10 = 1 + 0.630930 + 0.500000 + … + 0.289065 = 4.543559

Therefore:

nDCG@10 = 3.438403 / 4.543559 = 0.756764

This exactly matches the bge_small query-0 entry in outputs/validation_per_query.csv (outputs/validation_per_query.csv:202): 0.756764.

**User prompt:**

> For validation query 0, count the total number of products labeled Exact and Partial in data/labels_validation.csv. Do not count only the top ten retrieved products. Do not modify any files or access test labels.

**Codex response:**

Validation query 0 has 39 Exact products and 2,977 Partial products in data/labels_validation.csv.

That is 3,016 relevant labeled products total (excluding 286 Irrelevant labels).

**User prompt:**

> Help me analyze Q3a using `outputs/validation_per_query.csv`. My selected method is BGE-small (`bge_small`), and I want to compare it against keyword search. Identify the three validation queries where BGE-small outperformed keyword search by the largest nDCG@10 difference and the three where keyword search outperformed BGE-small by the largest difference. For each of these six queries, run `python score.py show --query-id <ID> --rankings my_rankings.csv` and report the query text, both nDCG@10 scores, their difference, and the top ten products from each method, including product names and relevance labels. Help me understand what went right or wrong by identifying specific products that explain the differences, and suggest appropriate failure types based on the results. Present the findings in Markdown so I can review them and write my own interpretations. Do not modify any files or rerun the embedding models.

**Codex response:**

Analyzed `outputs/validation_per_query.csv` and identified the three validation queries where BGE-small outperformed keyword search by the largest nDCG@10 difference (printers, oriental vanity, and nautical platters) and the three where keyword search performed better (trinaic towel rod, huntsville sectional sofa, and wayfair coffee table). Provided the nDCG@10 scores and differences for each query, along with the top ten products returned by both methods, including product IDs, names, and relevance labels.

**User prompt:**

> Help me complete Q3b of my Case 3 assignment. Using `my_rankings.csv` and the validation relevance labels, identify ten unjudged products appearing in BGE-small's top-ten validation results, preferably selecting products from ten different queries. For each product, report the query ID, query text, product ID, product name, product class, and the beginning of its description from the product catalog. Only include products that do not have a relevance judgment for their corresponding validation query. Present the results in a Markdown table, but leave the "My judgment" and "Why" columns blank because I need to evaluate each product myself. Do not modify any files or access test labels or results.

**Codex response:**

Ten unjudged products identified from BGE-small's top-ten validation rankings, selecting one rank-1 result from each of ten different queries. Provided the query IDs, search queries, product IDs, product names, classes, and the beginning of each available description. The results included products with mismatched categories, missing requested attributes, and similar product names.

**User prompt:**

> Help me answer Q3c using the validation results from my Case 3 assignment. My selected method is BGE-small (bge_small). Using outputs/validation_per_query.csv and my_rankings.csv, examine validation queries 219 (trinaic towel rod) and 416 (wayfair coffee table), where keyword search significantly outperformed BGE-small. Run python score.py show for both queries and compare their nDCG@10 scores, retrieved products, and relevance labels. Explain what kind of search each query represents, why keyword search performed better, and what types of searches BRG Direct should continue using keyword search for. Do not modify any files, rerun the embedding models, or access test labels. I will write my own response based on your findings.

**Codex response:**

| Query | Keyword nDCG@10 | BGE-small nDCG@10 | Keyword advantage |
|---|---:|---:|---:|
| 219 — trinaic towel rod | 1.000 | 0.069 | +0.931 |
| 416 — wayfair coffee table | 1.000 | 0.417 | +0.583 |

Keyword returned ten judged Partial towel-bar/rack products, including:

- 2926 — single rod and multi-rod 25'' fixture mounted towel bar
- 2927 — single rod and multi-rod 24'' fixture mounted towel bar
- 2924 — single rod wall mounted towel rack
- 2925 — multi-rod wall mounted towel rack
- 4804 — stainless steel towel rack…single rod rack bath towel holder
- 10677 — 16 inch black single towel bar rack…

BGE-small returned mostly unjudged results associated with “trinsic,” rather than the judged generic towel-bar results:

| Rank | BGE-small product | Label |
|---:|---|---|
| 1 | 10114 — trinsic® wall mounted robe hook | Unjudged |
| 2 | 10115 — trinsic® bathroom towel ring | Unjudged |
| 3 | 27666 — triva wall mounted robe hook | Unjudged |
| 4 | 10183 — trinsic 24'' wall mounted towel bar | Unjudged |
| 5 | 10180 — trinsic® 30'' wall mounted towel bar | Unjudged |
| 6 | 26953 — peterson adjustable drapery tringle single curtain rod | Unjudged |
| 7 | 6598 — trinsic 30'' wall mounted towel bar | Unjudged |
| 8 | 2926 — single rod and multi-rod 25'' fixture mounted towel bar | Partial |
| 9 | 6599 — trinsic 18'' wall mounted towel bar | Unjudged |
| 10 | 10138 — trinsic 18'' wall mounted towel bar | Unjudged |

Keyword returned ten judged Partial coffee tables:

- 608, 20513, 22679, and 33290 — coffee table
- 19750 — a-37 coffee table in, matching coffee table
- 290 — kalmus coffee table
- 294 — aalst coffee table
- 295 — buchheit coffee table
- 296 — aalt coffee table
- 297 — aaltien coffee table

BGE-small mixed coffee tables with “Wayfair Basics” products from unrelated categories:

| Rank | BGE-small product | Label |
|---:|---|---|
| 1 | 39189 — wayfair basics® tablecloth | Unjudged |
| 2 | 36109 — raffa coffee table | Partial |
| 3 | 39160 — wayfair basics stackable storage drawers | Unjudged |
| 4 | 39169 — wayfair basics solid color round tablecloth | Unjudged |
| 5 | 39168 — wayfair basics solid color square tablecloth | Unjudged |
| 6 | 17106 — telfair sled coffee table with storage | Partial |
| 7 | 39213 — wayfair basics® industrial stool | Unjudged |
| 8 | 38258 — heflin coffee table | Partial |
| 9 | 32149 — tillar coffee table | Partial |
| 10 | 34533 — huyet coffee table | Partial |

**User prompt:**

> Help me complete Q4a by testing a larger embedding model, BAAI/bge-base-en-v1.5 (768 dimensions), against my existing BGE-small model. Review embed_and_rank.py and score.py, then implement the larger model using the same text processing, normalization, and ranking approach. Use a pinned model revision, name the new method bge_base, and save its rankings to my_change.csv without modifying my original files. Explain why the larger model might improve search results, and record its revision, encoding time, vector dimensions, vector lengths, and storage requirements. Do not use relevance labels or test queries to build or tune the method. Once finished, explain the changes and evaluate the new method on validation only using python score.py score --split validation --rankings my_rankings.csv my_change.csv --baseline bge_small --out outputs_q4. Report its nDCG@10, judged@10, and paired difference from BGE-small, including the confidence interval.

**Codex response:**

Completed the BGE-base validation experiment without changing embed_and_rank.py, my_rankings.csv, or existing outputs.

Created:

- `embed_bge_base.py`
- `my_change.csv`
- `validation_metrics.csv`

The new script uses:

- Method: bge_base
- Model: BAAI/bge-base-en-v1.5
- Pinned revision: a5beb1e3e68b9ab74eb54cfd186867f64f240e1a
- CPU, float32 vectors, normalization, BGE query prefix, dot-product ranking, and lower-product-ID tie-breaking.
- No relevance labels were used to create the rankings. Test queries were excluded from this validation-only experiment.

| Measure | BGE-base result |
|---|---:|
| Product-vector shape | 42,994 × 768 |
| Product-vector lengths | 0.99999982 to 1.00000012 |
| Query-vector shape | 279 × 768 |
| Query-vector lengths | 0.99999988 to 1.00000012 |
| Raw product-vector storage | 132,077,568 bytes (about 132.1 MB; 126 MiB) |
| Encoding time | 2,242.69 seconds (37.38 minutes) |

Validation comparison against BGE-small:

| Method | nDCG@10 | judged@10 | Difference vs. BGE-small (paired 95% CI) |
|---|---:|---:|---:|
| bge_small | 0.7393 | 0.8805 | — |
| bge_base | 0.7414 | 0.8825 | +0.0021 (−0.0122 to +0.0157) |

BGE-base beat BGE-small on 77 validation queries and lost on 65. Its small average gain is not decisive because the paired interval includes zero.

Why it might improve: BGE-base has twice the vector dimensions and a larger encoder, so it can potentially represent product-query meaning and distinctions more richly. In this validation run, that added capacity produced only a very small, statistically uncertain gain while doubling raw vector storage and taking substantially longer to encode.

**User prompt:**

> create a transcript of this converstation, including prompts and codex responses, and add it to the "## AI record" section of case3_owensimon.md

**Codex response:**

Added this transcript to the `## AI record` section of `case3_owensimon.md`.