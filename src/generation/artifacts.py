import io
import json
import re
from datetime import datetime
from xml.sax.saxutils import escape

from src.retrieval.vector_store import VectorStore
from src.storage.base import StorageBackend

from .llm import LLMClient


class ArtifactError(Exception):
    """Raised with a user-friendly message when an artifact can't be generated."""


REPORT_SYSTEM = """You write clear, well-organized reports using ONLY the numbered source excerpts provided.

Rules:
- Use Markdown: a '# ' title, then '## ' section headings (e.g. Overview, Key Findings, Details, Limitations, Conclusion).
- Use short paragraphs and bullet lists where helpful.
- Cite sources inline with bracketed numbers like [1] or [2][3] after the claims they support.
- Do not use outside knowledge or invent citations. If the excerpts don't cover something, leave it out.
- Do not add a Sources section; it is added automatically."""

QUIZ_SYSTEM = """You write multiple-choice quizzes using ONLY the numbered source excerpts provided.

Return ONLY a JSON array, no prose and no code fences. Each item must be:
{"question": "...", "options": ["...", "...", "...", "..."], "answer": "B", "explanation": "...", "source": 3}

Rules:
- Exactly 4 options per question, without 'A.' / 'B.' prefixes. "answer" is one letter: A, B, C, or D.
- Vary which letter is correct. Wrong options must be plausible but clearly wrong according to the excerpts.
- "explanation" is one or two sentences based on the excerpts.
- "source" is the excerpt number that supports the answer.
- Cover different parts of the material. Do not ask about anything not in the excerpts."""


# ---------------------------------------------------------------- helpers
def _parse_json_list(raw: str) -> list:
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("no JSON array found")
    return json.loads(raw[start:end + 1])


def _validate_quiz(items: list) -> list[dict]:
    good = []
    for it in items:
        if not isinstance(it, dict):
            continue
        opts = it.get("options")
        ans = str(it.get("answer", "")).strip().upper()[:1]
        if not it.get("question") or not isinstance(opts, list) or len(opts) != 4:
            continue
        if not ans or ans not in "ABCD":
            continue
        opts = [re.sub(r"^[A-Da-d][.)]\s*", "", str(o)).strip() for o in opts]
        src = it.get("source")
        good.append({
            "question": str(it["question"]).strip(),
            "options": opts,
            "answer": ans,
            "explanation": str(it.get("explanation", "")).strip(),
            "source": src if isinstance(src, int) else None,
        })
    return good


def markdown_to_pdf(md: str) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    def clean(t: str) -> str:
        t = t.replace("\u2011", "-").replace("\u2010", "-").replace("\u2212", "-")
        return t.encode("cp1252", errors="replace").decode("cp1252")

    def fmt(t: str) -> str:
        t = escape(clean(t))
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)

    styles = getSampleStyleSheet()
    bullet_style = ParagraphStyle("bullet", parent=styles["BodyText"], leftIndent=18, bulletIndent=6)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=54, rightMargin=54,
                            topMargin=54, bottomMargin=54)
    story = []
    for line in md.splitlines():
        s = line.rstrip()
        if not s.strip():
            story.append(Spacer(1, 6))
        elif s.startswith("### "):
            story.append(Paragraph(fmt(s[4:]), styles["Heading3"]))
        elif s.startswith("## "):
            story.append(Paragraph(fmt(s[3:]), styles["Heading2"]))
        elif s.startswith("# "):
            story.append(Paragraph(fmt(s[2:]), styles["Heading1"]))
        elif re.match(r"^\s*[-*]\s+", s):
            story.append(Paragraph(fmt(re.sub(r"^\s*[-*]\s+", "", s)), bullet_style, bulletText="\u2022"))
        else:
            story.append(Paragraph(fmt(s), styles["BodyText"]))
    doc.build(story)
    return buf.getvalue()


# ---------------------------------------------------------------- service
class ArtifactService:
    def __init__(self, storage: StorageBackend, store: VectorStore, llm: LLMClient,
                 max_context_chars: int = 12000):
        self.storage = storage
        self.store = store
        self.llm = llm
        self.max_context_chars = max_context_chars   # keep modest for free-tier token limits

    # ----- context -----
    def _gather(self, notebook_id: str) -> list[dict]:
        chunks = self.store.get_all(notebook_id)
        if not chunks:
            raise ArtifactError("This notebook has no indexed sources yet. Add a file or URL first.")
        chunks.sort(key=lambda c: (c["metadata"]["source_id"], c["metadata"]["chunk_index"]))
        total = sum(len(c["text"]) for c in chunks)
        if total > self.max_context_chars:           # sample evenly across all sources
            keep = max(1, int(len(chunks) * self.max_context_chars / total))
            step = len(chunks) / keep
            chunks = [chunks[int(i * step)] for i in range(keep)]
        return chunks

    @staticmethod
    def _context_text(chunks: list[dict]) -> str:
        blocks = []
        for i, c in enumerate(chunks, start=1):
            m = c["metadata"]
            loc = f", {m['location']}" if m.get("location") else ""
            blocks.append(f"[{i}] (Source: {m['source_name']}{loc})\n{c['text']}")
        return "\n\n".join(blocks)

    @staticmethod
    def _sources_md(chunks: list[dict]) -> str:
        lines = ["## Sources", ""]
        for i, c in enumerate(chunks, start=1):
            m = c["metadata"]
            loc = f", {m['location']}" if m.get("location") else ""
            lines.append(f"- [{i}] {m['source_name']}{loc}")
        return "\n".join(lines)

    # ----- saving -----
    def _save(self, notebook_id: str, base: str, md: str) -> dict:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        md_name, pdf_name = f"{base}_{ts}.md", f"{base}_{ts}.pdf"
        self.storage.save_file(notebook_id, "artifacts", md_name, md.encode("utf-8"))
        self.storage.save_file(notebook_id, "artifacts", pdf_name, markdown_to_pdf(md))
        return {"md": md_name, "pdf": pdf_name}

    # ----- report -----
    def generate_report(self, notebook_id: str, notebook_name: str = "Notebook") -> dict:
        chunks = self._gather(notebook_id)
        prompt = (f"Source excerpts:\n\n{self._context_text(chunks)}\n\n"
                  f"Write a report summarizing this material for the notebook \"{notebook_name}\".")
        body = self.llm.complete(REPORT_SYSTEM, [{"role": "user", "content": prompt}], max_tokens=4000)
        if not body:
            raise ArtifactError("The AI returned an empty report. Please try again.")
        md = f"{body}\n\n{self._sources_md(chunks)}\n"
        return {"markdown": md, "files": self._save(notebook_id, "report", md)}

    # ----- quiz + answer key -----
    def generate_quiz(self, notebook_id: str, notebook_name: str = "Notebook",
                      num_questions: int = 8) -> dict:
        chunks = self._gather(notebook_id)
        prompt = (f"Source excerpts:\n\n{self._context_text(chunks)}\n\n"
                  f"Write {num_questions} multiple-choice questions.")
        questions = []
        for _ in range(2):                              # one retry on malformed JSON
            raw = self.llm.complete(QUIZ_SYSTEM, [{"role": "user", "content": prompt}], max_tokens=4000)
            try:
                questions = _validate_quiz(_parse_json_list(raw))
            except (ValueError, json.JSONDecodeError):
                questions = []
            if questions:
                break
        if not questions:
            raise ArtifactError("Could not generate a valid quiz. Please try again.")

        quiz_md = [f"# Quiz: {notebook_name}", ""]
        key_md = [f"# Answer Key: {notebook_name}", ""]
        for n, q in enumerate(questions, start=1):
            quiz_md.append(f"**{n}. {q['question']}**")
            quiz_md.append("")
            for letter, opt in zip("ABCD", q["options"]):
                quiz_md.append(f"- {letter}. {opt}")
            quiz_md.append("")
            cite = f" [{q['source']}]" if q["source"] else ""
            idx = "ABCD".index(q["answer"])
            key_md.append(f"**{n}. {q['answer']}. {q['options'][idx]}**")
            key_md.append(f"{q['explanation']}{cite}")
            key_md.append("")
        key_md.append(self._sources_md(chunks))

        quiz_text, key_text = "\n".join(quiz_md), "\n".join(key_md)
        return {
            "questions": questions,
            "quiz_markdown": quiz_text,
            "key_markdown": key_text,
            "quiz_files": self._save(notebook_id, "quiz", quiz_text),
            "key_files": self._save(notebook_id, "answer_key", key_text),
        }

    # ----- listing -----
    def list_artifacts(self, notebook_id: str) -> list[str]:
        return self.storage.list_files(notebook_id, "artifacts")

    def read_artifact(self, notebook_id: str, filename: str) -> bytes:
        return self.storage.read_file(notebook_id, "artifacts", filename)