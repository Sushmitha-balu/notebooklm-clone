# RAG Evaluation: Conclusions

See `results.md` for the full questions, retrieved chunks, timings, and answers.

## Setup
Both retrievers ran on the same notebook: a Wikipedia article on RAG plus a PowerPoint on
flood diffusion (33 chunks total), with k=5 and six test questions (factual, keyword,
conceptual, multi-part, and one out-of-scope).

## Results summary
| Method | Avg retrieval (ms) | Retrieval hit | Relevance | Groundedness | Completeness |
|---|---|---|---|---|---|
| dense | 11.46 | 5/5 | 5.00 | 4.67 | 4.83 |
| hybrid | 13.84 | 5/5 | 5.00 | 5.00 | 4.83 |

## Findings
**Retrieval quality.** Both methods had a hit rate of 5/5, with the matching chunk at rank 1
every time, including the keyword question about the slide deck's datasets (HumanML3D, BABEL).
They retrieved nearly identical chunk sets, differing mainly in order.

**Speed.** Hybrid cost about 2.4 ms more per query (13.84 vs 11.46 ms) for the BM25 step and
rank fusion. LLM time (about 6 s) was dominated by API rate-limit waits and does not reflect
the retrieval method.

**Answer quality.** Hybrid scored higher on groundedness (5.00 vs 4.67). The gap comes from
one question: on Q4, dense's answer included claims (a medical example, the Bard case) that
were not in the retrieved excerpts. Completeness was equal. The judge was lenient (mostly 5s),
so this difference is suggestive, not conclusive.

**Per-question observations.** On Q2, dense returned five slide chunks while hybrid's fifth
result was an unrelated Wikipedia chunk, so BM25 added some noise on a short query even though
both answers were identical. On Q1, dense ranked a bibliography entry first, which shows that
reference-list chunks pollute retrieval.

**Out-of-scope handling.** Both methods correctly declined to answer the World Cup question.

## Limitations
Small corpus, six questions, one LLM judge, and a single run. Wikipedia reference-list chunks
appeared in some results. Filtering the References section during ingestion would help.

## Conclusion
On this small notebook, dense and hybrid retrieval are equivalent in retrieval quality, and
hybrid costs a few milliseconds more. Hybrid is the better default: it matched dense on hits,
scored slightly higher on groundedness, and keyword matching protects against exact-term
queries (names, acronyms, numbers) that embeddings can miss on larger corpora. Dense alone is
sufficient when queries are conceptual and the corpus is small.