import argparse
import json
import re
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.generation.chat import SYSTEM_PROMPT, _format_context  # noqa: E402
from src.services import AppServices  # noqa: E402

METHODS = ("dense", "hybrid")

JUDGE_SYSTEM = """You grade answers from a retrieval-augmented assistant.
Return ONLY a JSON object, no prose and no code fences:
{"relevance": 1-5, "groundedness": 1-5, "completeness": 1-5, "note": "one short sentence"}

relevance: does the answer address the question?
groundedness: is every claim supported by the excerpts, with no outside facts?
completeness: does it cover what the excerpts allow?
If the excerpts clearly contain the answer but the assistant says they don't, give completeness 1.
If the excerpts truly lack the answer, saying so is correct: grade that behavior 5 across the board."""


def judge(svc, question, context, answer):
    prompt = f"Question: {question}\n\nExcerpts:\n{context[:4000]}\n\nAnswer to grade:\n{answer}"
    try:
        raw = svc.llm.complete(JUDGE_SYSTEM, [{"role": "user", "content": prompt}], max_tokens=1000)
        data = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        return {k: int(data[k]) for k in ("relevance", "groundedness", "completeness")} | {"note": data.get("note", "")}
    except Exception as e:
        return {"relevance": None, "groundedness": None, "completeness": None, "note": f"judge failed: {e}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebook", required=True, help="notebook id (shown in brackets in the UI)")
    ap.add_argument("--questions", default="evaluation/questions.json")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between LLM calls (rate limits)")
    args = ap.parse_args()

    svc = AppServices()
    nb = svc.manager.get(args.notebook)
    questions = json.loads(Path(args.questions).read_text())
    print(f"Notebook: {nb.name} | sources: {[s['name'] for s in nb.sources]}")

    for m in METHODS:                                   # warm up models and the BM25 index
        svc.retrievers[m].retrieve(nb.id, "warmup", args.k)

    rows = []
    for q in questions:
        for method in METHODS:
            retriever = svc.retrievers[method]
            times = []
            for _ in range(3):
                res = retriever.retrieve(nb.id, q["question"], args.k)
                times.append(res.elapsed_ms)
            context = _format_context(res.chunks)

            # Objective metric: did a retrieved chunk contain an expected keyword?
            kws = [k.lower() for k in q.get("expected", [])]
            texts = [c["text"].lower() for c in res.chunks]
            rank = next((i for i, t in enumerate(texts, 1) if any(k in t for k in kws)), None) if kws else None
            hit = None if not kws else rank is not None

            start = time.perf_counter()
            answer = svc.llm.complete(
                SYSTEM_PROMPT,
                [{"role": "user", "content": f"Source excerpts:\n\n{context}\n\nQuestion: {q['question']}"}],
            )
            llm_ms = (time.perf_counter() - start) * 1000
            time.sleep(args.delay)
            scores = judge(svc, q["question"], context, answer)
            time.sleep(args.delay)

            rows.append({
                "id": q["id"], "type": q["type"], "question": q["question"], "method": method,
                "retrieval_ms": statistics.median(times), "llm_ms": llm_ms, "answer": answer,
                "hit": hit, "rank": rank,
                "chunks": [{"id": c["id"], "location": c["metadata"].get("location", ""),
                            "source": c["metadata"]["source_name"], "score": c["score"],
                            "text": c["text"]} for c in res.chunks],
                "scores": scores,
            })
            print(f"Q{q['id']} [{method}] retrieval {rows[-1]['retrieval_ms']:.1f} ms | llm {llm_ms:.0f} ms | "
                  f"hit={hit} rank={rank} | {scores}")

    out_dir = Path("evaluation")
    (out_dir / "results.json").write_text(json.dumps(rows, indent=2))
    write_markdown(rows, out_dir / "results.md", nb.name)
    print("\nWrote evaluation/results.json and evaluation/results.md")


def avg(values):
    values = [v for v in values if v is not None]
    return f"{sum(values) / len(values):.2f}" if values else "n/a"


def write_markdown(rows, path, nb_name):
    md = ["# RAG Evaluation: dense vs hybrid retrieval", "", f"Notebook: **{nb_name}**", "",
          "## Summary", "",
          "| Method | Avg retrieval (ms) | Avg LLM (ms) | Retrieval hit | Avg hit rank | Relevance | Groundedness | Completeness |",
          "|---|---|---|---|---|---|---|---|"]
    for m in METHODS:
        r = [x for x in rows if x["method"] == m]
        hits = [x["hit"] for x in r if x["hit"] is not None]
        ranks = [x["rank"] for x in r if x["rank"] is not None]
        md.append(f"| {m} | {avg([x['retrieval_ms'] for x in r])} | {avg([x['llm_ms'] for x in r])} | "
                  f"{sum(hits)}/{len(hits)} | {avg(ranks)} | "
                  f"{avg([x['scores']['relevance'] for x in r])} | {avg([x['scores']['groundedness'] for x in r])} | "
                  f"{avg([x['scores']['completeness'] for x in r])} |")
    md += ["", "Retrieval hit = a retrieved chunk contained an expected keyword (out-of-scope questions excluded). "
               "Scores are 1-5 from an LLM judge. Retrieval time is the median of 3 runs after warm-up.", ""]

    for qid in sorted({r["id"] for r in rows}):
        pair = [r for r in rows if r["id"] == qid]
        md += [f"## Q{qid} ({pair[0]['type']}): {pair[0]['question']}", ""]
        for r in pair:
            s = r["scores"]
            md += [f"### {r['method']}",
                   f"- Retrieval: {r['retrieval_ms']:.1f} ms | LLM: {r['llm_ms']:.0f} ms | "
                   f"hit: {r['hit']} (rank {r['rank']})",
                   f"- Scores: relevance {s['relevance']}, groundedness {s['groundedness']}, "
                   f"completeness {s['completeness']}. {s['note']}", "",
                   "**Retrieved chunks:**"]
            for c in r["chunks"]:
                loc = f", {c['location']}" if c["location"] else ""
                preview = c["text"].replace("\n", " ")[:160]
                md.append(f"- `{c['id']}` ({c['source']}{loc}, score {c['score']:.3f}): {preview}...")
            md += ["", "**Answer:**", "", r["answer"], ""]
    path.write_text("\n".join(md))


if __name__ == "__main__":
    main()