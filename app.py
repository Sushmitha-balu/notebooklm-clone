import tempfile
import os
from pathlib import Path

import gradio as gr

from src.generation.artifacts import ArtifactError
from src.generation.llm import LLMError
from src.ingestion.loaders import IngestionError
from src.services import AppServices

svc = AppServices()
DOWNLOAD_DIR = Path("data/_downloads").resolve()


# ------------------------------------------------------------------ helpers
def nb_choices():
    notebooks = sorted(svc.manager.list(), key=lambda n: n.created_at)
    return [(f"{n.name}  [{n.id}]", n.id) for n in notebooks]


def source_choices(nb_id):
    if not nb_id:
        return []
    return [(s["name"], s["id"]) for s in svc.manager.get(nb_id).sources]


def render_sources(nb_id):
    if not nb_id:
        return "_No notebook selected._"
    sources = svc.manager.get(nb_id).sources
    if not sources:
        return "_No sources yet. Upload files or add a URL._"
    lines = []
    for s in sources:
        icon = "🌐" if s["type"] == "url" else "📄"
        lines.append(f"- {icon} **{s['name']}** ({s['num_chunks']} chunks)")
    return "\n".join(lines)


def render_chat(history):
    if not history:
        return "_Ask a question about your sources._"
    parts = [f"**You:** {t['question']}\n\n**Assistant:** {t['answer']}" for t in history]
    return "\n\n---\n\n".join(parts)


def render_citations(sources):
    if not sources:
        return ""
    out = ["### Sources for the latest answer"]
    for s in sources:
        loc = f", {s['location']}" if s["location"] else ""
        status = "✅ cited" if s["cited"] else "retrieved"
        excerpt = s["text"].replace("\n", " ")[:350]
        out.append(f"**[{s['number']}] {s['source_name']}{loc}** ({status}, score {s['score']:.3f})\n> {excerpt}...")
    return "\n\n".join(out)


def export_files(nb_id, names):
    """Copy artifacts to a temp folder so Gradio can serve them for download."""
    folder = DOWNLOAD_DIR / nb_id
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in names:
        path = folder / name
        path.write_bytes(svc.storage.read_file(nb_id, "artifacts", name))
        paths.append(str(path))
    return paths


def all_artifact_files(nb_id):
    if not nb_id:
        return []
    return export_files(nb_id, svc.storage.list_files(nb_id, "artifacts"))


def need_notebook(nb_id):
    if not nb_id:
        raise gr.Error("Create or select a notebook first.")


# ------------------------------------------------------------------ notebook handlers
def init_app():
    choices = nb_choices()
    return gr.Dropdown(choices=choices, value=choices[0][1] if choices else None)


def on_select(nb_id):
    if not nb_id:
        return render_sources(None), gr.Dropdown(choices=[], value=None), render_chat([]), "", []
    history = svc.chat.get_history(nb_id) if svc._chat else svc.storage.load_json(nb_id, "chats", "history.json", default=[])
    return (
        render_sources(nb_id),
        gr.Dropdown(choices=source_choices(nb_id), value=None),
        render_chat(history),
        "",
        all_artifact_files(nb_id),
    )


def create_notebook(name):
    try:
        nb = svc.manager.create(name)
    except ValueError as e:
        raise gr.Error(str(e))
    return gr.Dropdown(choices=nb_choices(), value=nb.id), "", f"✅ Created notebook **{nb.name}**."


def delete_notebook(nb_id):
    need_notebook(nb_id)
    svc.delete_notebook(nb_id)
    choices = nb_choices()
    return gr.Dropdown(choices=choices, value=choices[0][1] if choices else None), "🗑️ Notebook deleted."


# ------------------------------------------------------------------ source handlers
def add_files(nb_id, files):
    need_notebook(nb_id)
    if not files:
        raise gr.Error("Choose at least one PDF, PPTX, or TXT file first.")
    messages = []
    for f in files:
        path = Path(getattr(f, "name", f))
        try:
            s = svc.add_file(nb_id, path.name, path.read_bytes())
            messages.append(f"✅ **{path.name}**: {s['num_chunks']} chunks indexed")
        except IngestionError as e:
            messages.append(f"❌ **{path.name}**: {e}")
        except Exception as e:
            messages.append(f"❌ **{path.name}**: unexpected error ({e})")
    return "\n\n".join(messages), render_sources(nb_id), gr.Dropdown(choices=source_choices(nb_id), value=None), None


def add_url(nb_id, url):
    need_notebook(nb_id)
    if not (url or "").strip():
        raise gr.Error("Paste a URL first.")
    try:
        s = svc.add_url(nb_id, url)
        msg = f"✅ **{s['name']}**: {s['num_chunks']} chunks indexed"
    except IngestionError as e:
        msg = f"❌ {e}"
    except Exception as e:
        msg = f"❌ Unexpected error ({e})"
    return msg, render_sources(nb_id), gr.Dropdown(choices=source_choices(nb_id), value=None), ""


def remove_source(nb_id, source_id):
    need_notebook(nb_id)
    if not source_id:
        raise gr.Error("Pick a source to remove.")
    svc.remove_source(nb_id, source_id)
    return "🗑️ Source removed.", render_sources(nb_id), gr.Dropdown(choices=source_choices(nb_id), value=None)


# ------------------------------------------------------------------ chat handlers
def ask(nb_id, question, method):
    need_notebook(nb_id)
    if not (question or "").strip():
        raise gr.Error("Type a question first.")
    try:
        out = svc.chat.ask(nb_id, question, method=method)
    except (LLMError, ValueError) as e:
        raise gr.Error(str(e))
    if not out["sources"]:
        raise gr.Error(out["answer"])
    timing = (f"⏱️ {out['method']} retrieval: {out['retrieval_ms']:.0f} ms | "
              f"LLM: {out['llm_ms']:.0f} ms")
    return render_chat(svc.chat.get_history(nb_id)), render_citations(out["sources"]), "", timing


def clear_chat(nb_id):
    need_notebook(nb_id)
    svc.chat.clear_history(nb_id)
    return render_chat([]), "", ""


# ------------------------------------------------------------------ artifact handlers
def make_report(nb_id):
    need_notebook(nb_id)
    try:
        nb = svc.manager.get(nb_id)
        res = svc.artifacts.generate_report(nb_id, nb.name)
    except (LLMError, ArtifactError) as e:
        raise gr.Error(str(e))
    return res["markdown"], all_artifact_files(nb_id)


def make_quiz(nb_id, num_questions):
    need_notebook(nb_id)
    try:
        nb = svc.manager.get(nb_id)
        res = svc.artifacts.generate_quiz(nb_id, nb.name, int(num_questions))
    except (LLMError, ArtifactError) as e:
        raise gr.Error(str(e))
    return res["quiz_markdown"], res["key_markdown"], all_artifact_files(nb_id)


# ------------------------------------------------------------------ UI
with gr.Blocks(title="NotebookLM Clone") as demo:
    gr.Markdown("# 📓 NotebookLM Clone\nUpload sources, ask questions with citations, and generate reports and quizzes.")

    with gr.Row():
        # ---------------- left: notebooks + sources ----------------
        with gr.Column(scale=1):
            gr.Markdown("### Notebooks")
            nb_dd = gr.Dropdown(label="Current notebook", choices=nb_choices(), interactive=True)
            new_name = gr.Textbox(label="New notebook name", placeholder="e.g. Biology notes")
            with gr.Row():
                create_btn = gr.Button("➕ Create", variant="primary")
                delete_btn = gr.Button("🗑️ Delete notebook")

            gr.Markdown("### Add sources")
            files_in = gr.File(label="Upload PDF, PPTX, or TXT", file_count="multiple",
                               file_types=[".pdf", ".pptx", ".txt"])
            upload_btn = gr.Button("Upload & index")
            url_in = gr.Textbox(label="Or add a web page URL", placeholder="https://...")
            url_btn = gr.Button("Fetch & index URL")
            status = gr.Markdown()

            gr.Markdown("### Sources in this notebook")
            sources_md = gr.Markdown()
            rm_dd = gr.Dropdown(label="Remove a source", choices=[], interactive=True)
            rm_btn = gr.Button("Remove selected source")

        # ---------------- right: chat + artifacts ----------------
        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.Tab("💬 Chat"):
                    chat_md = gr.Markdown(render_chat([]))
                    question = gr.Textbox(label="Ask about your sources", placeholder="What does the document say about...?")
                    with gr.Row():
                        method = gr.Radio(["hybrid", "dense"], value="hybrid", label="Retrieval method")
                        ask_btn = gr.Button("Ask", variant="primary")
                        clear_btn = gr.Button("Clear chat")
                    timing_md = gr.Markdown()
                    citations_md = gr.Markdown()

                with gr.Tab("📝 Artifacts"):
                    with gr.Row():
                        report_btn = gr.Button("Generate report", variant="primary")
                        n_questions = gr.Slider(3, 15, value=8, step=1, label="Quiz questions")
                        quiz_btn = gr.Button("Generate quiz + answer key", variant="primary")
                    with gr.Tabs():
                        with gr.Tab("Report"):
                            report_md = gr.Markdown()
                        with gr.Tab("Quiz"):
                            quiz_md = gr.Markdown()
                        with gr.Tab("Answer key"):
                            key_md = gr.Markdown()
                    saved_files = gr.File(label="Downloads (Markdown + PDF)", file_count="multiple", interactive=False)

    # ---------------- events ----------------
    demo.load(init_app, outputs=nb_dd)
    nb_dd.change(on_select, nb_dd, [sources_md, rm_dd, chat_md, citations_md, saved_files])

    create_btn.click(create_notebook, new_name, [nb_dd, new_name, status])
    delete_btn.click(delete_notebook, nb_dd, [nb_dd, status])

    upload_btn.click(add_files, [nb_dd, files_in], [status, sources_md, rm_dd, files_in])
    url_btn.click(add_url, [nb_dd, url_in], [status, sources_md, rm_dd, url_in])
    rm_btn.click(remove_source, [nb_dd, rm_dd], [status, sources_md, rm_dd])

    ask_btn.click(ask, [nb_dd, question, method], [chat_md, citations_md, question, timing_md])
    question.submit(ask, [nb_dd, question, method], [chat_md, citations_md, question, timing_md])
    clear_btn.click(clear_chat, nb_dd, [chat_md, citations_md, timing_md])

    report_btn.click(make_report, nb_dd, [report_md, saved_files])
    quiz_btn.click(make_quiz, [nb_dd, n_questions], [quiz_md, key_md, saved_files])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        allowed_paths=[str(DOWNLOAD_DIR)],
    )