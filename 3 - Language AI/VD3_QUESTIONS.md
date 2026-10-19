# Case 3 — Can Embeddings Fix BRG Direct's Site Search?
## What to answer · MKTG 6620 · Fall 2026

**Released:** Thursday, October 8.
**Due:** Friday, October 23, at 11:59 p.m. Mountain Time.
Individual work, 100 points, 20% of the course grade. You hand in **one
Markdown file**.

---

## What this case is about

BRG Direct's merchandisers keep hearing the same complaint: shoppers type
"farmhouse dining table with bench" or "small loveseat for an apartment" and
the site shows them the wrong things. Junho Park, who runs BRG's search and
service tools, wants to move site search from keyword matching to
embeddings, the method you met in Session 6. Marisol Vance, BRG's Chief
Marketing Officer, asks three questions before she funds it:

1. Does embedding search find better products for real shopper queries?
2. By how much, and how sure are we?
3. What would it take to run it?

In Session 6 the vectors were made for you. This time **your coding agent
builds the embedding search itself**: it loads a real product catalog, embeds
every product and every shopper query with two small open models on your own
computer, and ranks the products. A supplied scorer then grades the rankings
against human relevance labels. You check the work, choose a method, read
what it gets wrong, try one improvement, and advise Marisol.

## Who does what

| Your agent builds | The supplied files do | You do |
|---|---|---|
| A script that embeds the 42,994 products and 479 queries with the two pinned models and writes each query's top 10 products | `score.py` checks your rankings file and scores it against the labels; `data/keyword_rankings.csv` is everyone's keyword baseline | Check that the embeddings make sense, choose a method before seeing the test set, read results, judge unlabelled products yourself, design one improvement, and write the memo |

Everyone follows the same recipe, so everyone should get nearly the same
numbers. That's expected. **Your points come from checking the work and
explaining what it means.**

## The data

The catalog, queries, and labels are **real**: WANDS, the Wayfair ANnotation
Dataset that Wayfair published for search research (Chen et al., ECIR 2022;
MIT licence, in `data/WANDS_LICENSE.txt`). Here it stands in for BRG Direct's
home-goods catalog. BRG, Marisol, and Junho are fictional, so your findings
describe Wayfair's catalog and Wayfair's annotators, not any BRG data.

Wayfair's annotators judged products for each query as **Exact** (what the
shopper asked for), **Partial** (related but not a full match, such as the right kind of
product in a different color or size), or **Irrelevant**. Most queries have a
few hundred judged products (the median is about 220), a few have only a
handful, and nobody judged all 42,994 for any query. A product nobody judged
for a query is **unjudged**.

We left out one query whose judged products were all irrelevant ("drudge
report"), so 479 of WANDS's 480 queries remain. They are split at random into
**79 development, 200 validation, and 200 test** queries.

| File | What it holds |
|---|---|
| `data/products.csv` | `product_id`, `product_name`, `product_class`, `category_hierarchy`, `product_description`, and `search_text`, the exact text to embed: the name and the class joined by a vertical bar, or the name alone when the class is blank. |
| `data/queries.csv` | `query_id`, `query` (what the shopper typed), and `split` (dev, validation, or test). |
| `data/labels_dev.csv`, `data/labels_validation.csv`, `data/labels_test.csv` | `query_id`, `product_id`, `label`: the human judgments. |
| `data/keyword_rankings.csv` | The keyword baseline's top 10 for every query (BM25, the standard keyword score, over `search_text`). When fewer than ten products share a word with the query, it fills the rest of its top 10 with the lowest product IDs (for example, for "printers"). |
| `data/data_manifest.json` | Where everything came from, the file fingerprints, and how the baseline was built. |
| `score.py`, `requirements.txt` | The scorer and the one package it needs (NumPy). |
| `SOURCE.md` | The data source, licence, and citation. |

For example, product 0's `search_text` is `solid wood platform bed | Beds`.
Product names in WANDS are lower-case with spaces around punctuation, such as
`dunston 28 '' square storage ottoman`. That is how Wayfair published them.
The CSV files are UTF-8, since some product text has accented letters and
symbols.

## The recipe (follow it exactly)

| Setting | Value |
|---|---|
| Model 1, method name `minilm` | `sentence-transformers/all-MiniLM-L6-v2`, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` |
| Model 2, method name `bge_small` | `BAAI/bge-small-en-v1.5`, revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` |
| Product text | The `search_text` column, unchanged |
| Query text | The `query` column. For BGE only, put `Represent this sentence for searching relevant passages: ` in front of each query (Session 6, section 2) |
| Vectors | Normalized to length 1 (`normalize_embeddings=True`), float32 |
| Device | The CPU (`device="cpu"`), even on a Mac with Apple silicon or a laptop with a graphics card, so your numbers match ours |
| Ranking | Dot product of the query vector with every product vector; keep the 10 highest; break a tie with the lower `product_id` |
| Output | One CSV with the columns `query_id`, `method`, `rank`, `product_id`: ten rows per query, ranks 1 to 10, for all 479 queries and both methods |

If your recipe matches ours, **validation nDCG@10 comes out within 0.003 of
0.736 for MiniLM and 0.739 for BGE-small** (keyword: 0.675). A bigger gap
means a setting differs, and finding it is part of 2a. BGE-small near 0.744
means the query prefix is missing; sentence-transformers' `encode_query()`
doesn't add it for this model. On a computer using four CPU
cores, embedding the catalog took us about 1 minute with MiniLM and 2 minutes
with BGE-small.

## Key terms

| Term | Plain meaning |
|---|---|
| Embedding, normalization, dot product | From Session 6: a model turns text into a list of numbers. Scaling each list to length 1 makes the dot product equal the cosine similarity. |
| Top 10 | The ten products a shopper would see first. |
| nDCG@10 | Normalized discounted cumulative gain of the top 10. A result earns 1 if Exact, 0.5 if Partial, and 0 if Irrelevant or unjudged. The result at rank r counts 1 ÷ log₂(r + 1), so rank 1 counts fully and rank 10 counts 0.289. The total is divided by the best total the query's labels allow, so 1.0 is a perfect top 10. |
| Exact@1 | The share of queries whose first result is labelled Exact. Some queries have no Exact product at all, so no method reaches 100%. |
| judged@10 | The share of top-10 results that have any label. Unjudged results score 0 even when they would suit the shopper. |
| Wilson 95% interval | A range for a share (such as Exact@1) that stays sensible with a few hundred queries. |
| Paired interval | `score.py` redraws the query set 2,000 times, scores both methods on the same draw each time, and keeps the middle 95% of their nDCG@10 differences. If it includes zero, the data fit "no advantage." |

The rank discounts, for working nDCG by hand:

| Rank | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 ÷ log₂(rank + 1) | 1.000 | 0.631 | 0.500 | 0.431 | 0.387 | 0.356 | 0.333 | 0.315 | 0.301 | 0.289 |

## Keep the test honest

Use the **development** queries to build and debug. Use the **validation**
queries to compare methods and choose. Save your choice with `score.py
select`, and only then score the **test** queries, once. `score.py` won't
score or show test queries until `selection.json` exists. Don't open
`data/labels_test.csv` before then. If you or your agent looked early, say so
in 2c; an honest note earns the points.

---

## Steps

**Step 1. Set up a folder.** Unzip `VD3_student_files.zip` into a new, empty
folder on your computer's own disk (not OneDrive, iCloud Drive, or Dropbox),
for example `~/mktg6620/case3`. Run every command from this folder.

**Step 2. Install.** You need Python 3.11 to 3.14. Make an environment and
install the scorer's package and the embedding packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install "torch==2.11.0" --index-url https://download.pytorch.org/whl/cpu
python -m pip install "torch==2.11.0" "sentence-transformers==5.4.1" "transformers==4.57.6"
```

Run every line, on any computer. The first torch line installs PyTorch's
CPU-only build, which on Linux avoids a 3 GB download for graphics cards.
On Windows, in PowerShell, the first two lines are `python -m venv .venv` and
`.venv\Scripts\Activate.ps1`.

In a new terminal, activate `.venv` again from the same folder. If PowerShell
says running scripts is disabled, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that window
and activate again. It affects only that window.

The last install downloads about 150 MB on a Mac and 200 MB on Windows
(about 1 GB once installed), and the first model run downloads about 220 MB
more. These versions install on Macs with Apple silicon (M1 or later) on
macOS 12 or newer, Windows x64 laptops, and Linux. **PyTorch has no
installer for Intel Macs or Windows on ARM laptops** (such as Snapdragon). On
one of those, see "If PyTorch won't install on your laptop" at the end of this
sheet.

**Step 3. Check the scorer.** This scores the keyword baseline alone on the
development queries; you should see nDCG@10 of 0.743.

```bash
python score.py score --split dev
```

**Step 4. Start your agent.** A good first prompt:

```text
Work only with the files in this folder. Read VD3_QUESTIONS.md, "The recipe"
section, and follow it exactly. Do not open data/labels_test.csv. Write one
Python script, embed_and_rank.py, that embeds data/products.csv's search_text
and data/queries.csv's query with both pinned models on the CPU, normalizes
the vectors, ranks products by dot product, and writes my_rankings.csv with
the columns query_id, method, rank, product_id for all queries and both
methods (method names minilm and bge_small). Print each model's vector shape,
vector lengths, and encoding time. Then run
python score.py check --rankings my_rankings.csv. I will write my own
judgments and memo.
```

Read the script before you run it. Check the model names, revisions, the BGE
prefix, the CPU device, and that queries and products use the same model.

**Step 5. Answer the questions below.** Most answers are two to four
sentences plus a number or a small table.

---

## Q1 — Embed the catalog (20 points)

**1a The data (5 points).** Ask your agent to count from the CSVs: the
products, the products with a blank class, the queries in each split, and the
development and validation labels by grade (Exact, Partial, Irrelevant). Then
pick one development query, quote one product labelled Exact and one labelled
Irrelevant, and say in a sentence why each label fits.

**1b Your embeddings (10 points).** Fill in one row per model:

| Method | Model ID | Revision (first 7 characters) | Query prefix | Product vectors (rows × dimensions) | Number format | Smallest and largest vector length | Raw bytes | Encoding time, and your computer |
|---|---|---|---|---|---|---|---|---|
| minilm | | | | | | | | |
| bge_small | | | | | | | | |

Raw bytes are products × dimensions × 4. Then, in two or three sentences:
why can't you compare a MiniLM vector with a BGE-small vector, even though
both have 384 numbers? And why normalize before taking dot products?

**1c Sanity check and AI use (5 points).** For one development query (query
1, "smart coffee table", is fine), list the five products each model ranks
highest. Do they look sensible? Then, in two or three sentences, say what your
agent did and what you checked yourself. Give your Python, torch,
sentence-transformers, transformers, and NumPy versions. Paste your final
`embed_and_rank.py` in the **Code** section of your file, and your prompts and
the agent's key replies in the **AI record**.

## Q2 — Score it, choose, then test once (25 points)

```bash
python score.py check --rankings my_rankings.csv
python score.py score --split validation --rankings my_rankings.csv
```

**2a Validation table (8 points).** From `outputs/validation_metrics.csv`,
fill in one row per method:

| Method | n | nDCG@10 | Exact@1 (95% interval) | judged@10 | nDCG@10 difference vs. keyword (paired 95% interval) | Queries better / worse than keyword |
|---|---|---|---|---|---|---|
| keyword | | | | | — | — |
| minilm | | | | | | |
| bge_small | | | | | | |

In the CSV, the intervals are `exact1_low` to `exact1_high` and `diff_low` to
`diff_high`, and better / worse are `beats_baseline` and `loses_to_baseline`.
Ties count as neither, so better and worse don't add up to n.

Do your MiniLM and BGE-small values match the recipe's within 0.003? If not,
find the setting that differs (ask your agent to compare its script with the
recipe table) and say what it was. Explaining a mismatch earns full credit.

**2b One query by hand (6 points).** Pick one validation query and run
`show` with its ID (query 0 here):

```bash
python score.py show --query-id 0 --rankings my_rankings.csv
```

For your preferred method, work out its nDCG@10 by hand: list the ten gains, multiply each by its rank discount, and add them up
(DCG). The ideal DCG comes from the query's best ten labels: `show` prints how
many Exact and Partial products the query has, so fill the ten slots with
Exact (1) first, then Partial (0.5). Divide, and compare your answer with the
query's row in `outputs/validation_per_query.csv`.

**2c Your choice (3 points).** Save your choice and your reason:

```bash
python score.py select --method bge_small --reason "your reason here"
```

Paste `selection.json`. Say whether you or your agent had seen any test
labels or test results before saving it. `select` won't overwrite, so your
first choice stays on record.

**2d Test once (8 points).**

```bash
python score.py score --split test --selection selection.json --rankings my_rankings.csv
```

From `outputs/test_metrics.csv`, give the same columns for keyword and your
method. Then, in a few sentences: did the difference you saw on validation
hold up on test? Does the test interval include zero, and what does that
mean? Why can the method that looked best on validation look less impressive
on fresh queries? What can 200 queries tell Marisol, and what can't they?

## Q3 — Read the results (25 points)

**3a Where the methods disagree (10 points).** From
`outputs/validation_per_query.csv`, have your agent list the three validation
queries where your method beat keyword by the most nDCG@10, and the three where
keyword beat it by the most. For each of the six, run `show` and say in one
sentence what went right or wrong, naming the products involved. Then sort
the six into failure types, in your own words. Examples include a brand or
collection name the model doesn't know, an attribute (color, material, size)
that gets ignored, the wrong kind of product, a misspelled query, and a label
you disagree with.

**3b Unjudged results (10 points).** Copy judged@10 for keyword and your
method from your 2a table. Then have your agent list ten unjudged results from
your method's validation top 10 (different queries if possible), each with the
query, the product name, class, and the start of its description. **Judge
each one yourself** as you think an annotator would have (Exact, Partial, or
Irrelevant), with a few words of reason:

| Query ID | Query | Product ID | Product name and class | My judgment | Why |
|---|---|---|---|---|---|

How many look relevant? Unjudged results score 0 in nDCG@10, so what does your
spot check suggest about the scores, and about comparing a new method with the
products annotators happened to judge? Would your Q2 conclusion change?

**3c Where keyword still wins (5 points).** Name two validation queries where
keyword clearly beat your method (they can come from 3a) and say what kind of
query each is. What kinds of searches would BRG Direct still want keyword
search for?

## Q4 — One improvement, and what it would take to run (20 points)

**4a Your improvement (12 points).** Design one change with your agent, give
it a new method name, and score it **on validation only**. Some ideas:

- Richer product text, such as adding `category_hierarchy` or the first
  sentence of `product_description` to `search_text`.
- A hybrid that merges the keyword top 10 with your method's list, for
  example by reciprocal rank fusion (each list adds 1 ÷ (60 + rank) to a
  product's score).
- A larger model, such as `BAAI/bge-base-en-v1.5` (768 dimensions; use a
  pinned revision and record it).

Don't use the labels or the test queries to build the method. Put its
rankings in a new file, such as `my_change.csv`, and compare it with your Q2 method (here `bge_small`) instead of keyword:

```bash
python score.py score --split validation --rankings my_rankings.csv my_change.csv --baseline bge_small --out outputs_q4
```

Report what you changed and why you expected it to help; its validation
nDCG@10, judged@10, and paired difference from your Q2 method; and what it
costs in encoding time and storage. A change that doesn't help earns full
credit when it's tested and explained well.

**4b Running it for BRG Direct (8 points).** Suppose BRG Direct lists 2 million
products (a planning figure for this case). Using your own timings and vector
sizes:

- How much raw vector storage would your chosen method need, and how long
  would embedding the whole catalog take on a computer like yours?
- What should trigger re-embedding? Think of new products, edited product
  text, and a model change.
- What one check would you run before shoppers see a new index, and what would
  you watch after launch?

## Q5 — Memo to Marisol Vance (10 points)

Write this as the last answer section of your file, in at most 400 words,
naming Junho Park as the person who would run the search.

- Recommend one: switch to embedding search, test it on live shoppers first,
  combine it with keyword search, or keep keyword search. Name the model.
  (2 points)
- Your strongest evidence, with numbers and their intervals. (3 points)
- The main limitation. (2 points)
- One measure of success for a live test, and one condition for stopping it.
  (3 points)

Any well-supported recommendation can earn full credit, including keeping
keyword search.

---

## What to hand in

Upload **one Markdown file**, named like `case3_yourname.md`, on Canvas. Don't
upload the rankings, vectors, data, or a ZIP. Any text editor works; save the
file with a `.md` ending, not `.md.txt`. Your agent may paste output and tables
into the file, but the judgments and explanations must be yours.

```markdown
# Case 3 — [Your name]

## Q1 — Embed the catalog
### 1a The data
### 1b My embeddings
### 1c Sanity check and AI use

## Q2 — Score it, choose, then test once
### 2a Validation table
### 2b One query by hand
### 2c My choice
### 2d Test once

## Q3 — Read the results
### 3a Where the methods disagree
### 3b Unjudged results
### 3c Where keyword still wins

## Q4 — One improvement, and what it would take to run
### 4a My improvement
### 4b Running it for BRG Direct

## Q5 — Memo to Marisol Vance
(at most 400 words)

## Code
(your final embed_and_rank.py, and your Q4 change)

## AI record
(your prompts and the key parts of the agent's replies,
including anything that went wrong)
```

## Grading

Points go to the parts listed above. Within a part, correct and explained
work earns full credit; a small gap, about three-quarters; a substantive error
with some valid reasoning, about half; a missing or unsupported part, zero. No
question is zeroed automatically. Your score doesn't depend on which method
wins, how high any metric is, whether your improvement helps, or whether your
first prompt worked.

## AI use

Your agent may write and run the code, fix errors, count and sort, and format
tables. **You write the judgments and explanations yourself:** the label
examples in 1a, the sanity check in 1c, the nDCG arithmetic in 2b, your
selection reason, the Q3 failure types and unjudged judgments, the Q4 reasons,
and the memo. Don't ask an AI to draft or rewrite them.

Plan for about 5–6 hours. A sensible pace: Q1 and Q2 by October 14, Q3 and Q4
by October 20, and the memo and upload by October 23. The final exam is
Monday, October 26.

## If PyTorch won't install on your laptop

On an Intel Mac or a Windows on ARM laptop, email me for a loaner laptop, or
run the case in a free Google Colab notebook, the browser path in the
Onboarding Note ("If your laptop is locked down by corporate IT"). In a new
notebook at colab.research.google.com, upload `VD3_student_files.zip` in the
Files panel (the folder icon), then run these lines in a code cell:

```python
!unzip -oq VD3_student_files.zip
!pip install -r requirements.txt "sentence-transformers==5.4.1" "transformers==4.57.6"
!python score.py score --split dev
```

Colab already has PyTorch; don't reinstall it there. Your agent still writes
`embed_and_rank.py` on your laptop in Step 4; tell it the script will run in
Colab. Upload the script the same way, run it with `!python embed_and_rank.py`,
and run each later command with `!python` in place of `python`. pip prints an
ERROR about dependency conflicts with other Colab packages, then "Successfully
installed", and TensorFlow prints startup messages; both are expected and don't
affect this case. If Colab offers to restart the session after the install, you
can skip it. Colab deletes your uploads and outputs when its runtime shuts down,
so download `my_rankings.csv`, and `selection.json` once you have it.
