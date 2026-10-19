# Case 3 data: source and licence

**Source.** WANDS, the Wayfair ANnotation Dataset, from
<https://github.com/wayfair/WANDS> at commit
`3b74dcf4ba29ab8ff3e6a50b5b09fc627cb882b5` (January 18, 2022). Checked
October 4, 2026.

**Citation.** Yan Chen, Shujian Liu, Zheng Liu, Weiyi Sun, Linas Baltrunas,
and Benjamin Schroeder. "WANDS: Dataset for Product Search Relevance
Assessment." *Advances in Information Retrieval (ECIR 2022)*.

**Licence.** WANDS is released under the MIT License, "Copyright (c) 2021
ecir2022." The full licence text is in `data/WANDS_LICENSE.txt` and travels
with these files. You may use, copy, and modify the data; keep the licence
with any copy.

**What the course changed.** Nothing in the judgments themselves. From
WANDS's three files we:

- kept each product's ID, name, class, category hierarchy, and description,
  and dropped its feature list and rating counts;
- added `search_text`, the product name and class joined by a vertical bar
  (the name alone when the class is blank);
- replaced the stray two-character escape sequences (a backslash followed by
  t, n, or r) in a few product names and descriptions with spaces;
- dropped each query's annotated class, because a search engine doesn't know
  it when a shopper types;
- kept the higher grade where one query-product pair was judged twice (1,467
  pairs, 14 of which disagreed);
- left out the one query whose judged products were all irrelevant
  ("drudge report");
- split the remaining 479 queries at random (seed 6620) into 79
  development, 200 validation, and 200 test queries;
- ranked the top 10 products for every query with BM25 over `search_text`,
  as the shared keyword baseline.

`VD3_build_data.py` in the instructor's folder does all of this from the
pinned commit, and `data/data_manifest.json` records every setting and file
fingerprint.

**Fiction.** Bonneville Retail Group, BRG Direct, Marisol Vance, and Junho
Park are fictional. The products, queries, and judgments are Wayfair's, so
findings describe Wayfair's catalog and annotators, not any BRG data.
