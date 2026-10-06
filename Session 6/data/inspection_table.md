# Saved data inspection

| Item | Result |
|---|---|
| Policy passages | 30 rows; 30 unique `doc_id` values |
| Policy status | 24 current; 6 archived |
| Questions | 24 rows; 24 unique `query_id` values |
| Question splits | 8 dev; 8 validation; 8 final |
| Labels | 24 rows; 24 unique query IDs; all 24 answerable |
| Sample development pair | `CLASS-1-01` (Alta, current, Returns) -> `CLASS-dev-01`; intended relevant ID: `CLASS-1-01` |

| Saved bundle | Documents array | Queries array |
|---|---|---|
| `bge_m3` | `(30, 1024)`, `float32` | `(24, 1024)`, `float32` |
| `bge_small` | `(30, 384)`, `float32` | `(24, 384)`, `float32` |
| `minilm` | `(30, 384)`, `float32` | `(24, 384)`, `float32` |
| `qwen3` | `(30, 1024)`, `float32` | `(24, 1024)`, `float32` |
| `qwen3_256` | `(30, 256)`, `float32` | `(24, 256)`, `float32` |

For every two-dimensional vector array, axis 0 indexes the saved records (documents or queries) and axis 1 indexes embedding dimensions.
