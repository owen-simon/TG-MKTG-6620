# Source and execution record

We wrote the policies, questions, intended labels, and scripted examples for
MKTG 6620 during the September 28, 2026 refresh. They describe fictional
business rules. None of them is a real company policy, a financial filing,
observed customer data, or an answer a live model produced. You may copy and
adapt these materials for coursework; please keep this origin notice.

The embedding arrays are real outputs from models run locally. Each passage
was encoded as its title, a newline, and its policy text; each question was
encoded separately. The matching JSON file for each model records the corpus
IDs, file hashes, exact model revision, input instructions, normalization,
dimensions, package versions, and a single-run encoding time. The longest
input was 44 tokens, far inside each model's limit as we ran it: 256 tokens
for MiniLM and 512 for the others, so nothing was truncated. Vectors are
float32. Qwen 256 is the first 256 dimensions of the same full Qwen encoding,
rescaled to length 1 again for both questions and passages.

BGE-small and Qwen3 are the homework comparisons. The class package also
includes MiniLM and dense BGE-M3 for inspection. Two models can produce
vectors of the same length and still not be comparable. The model weights are
not included. Model documentation:

- [BGE English v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- [BGE-M3](https://huggingface.co/BAAI/bge-m3)
- [Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)
- [MiniLM](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

We checked the model-card facts on September 28. The settings and results here
describe these model versions, not future releases. Working from the saved
vectors makes no model calls and downloads no weights. The saved vectors
cover only the questions in queries.csv. To try your own wording, you need a
working model environment with the same model and settings.

Keep live databases on a local disk. Reports, source files, saved arrays, and
finished, closed backups can be archived elsewhere. A SQLite backup covers the
catalog, not the LanceDB folder or the model weights; rebuild the vector table
from the text, the vectors, and their matching metadata. Don't copy active
database files as a backup while a program may be writing to them.

The fixture plans were written by hand and then run through a harness that
enforces scope and a call limit. A person scripted their steps; no model chose
them. The separate Case 3 answer-audit examples were also written by hand, so
judge whether each is supported rather than reporting them as a model's
performance rate.
