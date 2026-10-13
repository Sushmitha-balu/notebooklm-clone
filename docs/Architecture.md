NotebookLM Clone — Architecture Documentation

1. Overview

The NotebookLM Clone is a full-stack application that uses Retrieval-Augmented Generation (RAG) to answer questions from user-provided documents.

The application allows users to create multiple notebooks, upload documents, add web page URLs, ask questions, and generate reports, quizzes, and answer keys.

The system is divided into separate modules for the user interface, application services, document ingestion, retrieval, answer generation, and storage.

2. System Architecture

The application follows a modular architecture. Each module has a specific responsibility, which makes the code easier to maintain and extend.

The main components are:

* User Interface: Gradio provides the interface for notebook management, document uploads, chat, and artifact generation.
* Service Layer: Connects the user interface to the underlying modules.
* Notebook Manager: Creates, lists, renames, and deletes notebooks and manages their sources.
* Ingestion Pipeline: Extracts text from PDF, PPTX, TXT, and web page sources and divides the text into chunks.
* Retrieval System: Uses dense retrieval or hybrid retrieval to find relevant chunks.
* Generation Module: Uses an LLM to answer questions with citations and generate reports, quizzes, and answer keys.
* Storage Layer: Stores uploaded documents, extracted text, notebook information, chat history, and generated artifacts.
* Vector Database: ChromaDB stores document embeddings and metadata for retrieval.

3. Data Flow

The application follows these steps when answering a question.

1. The user creates a notebook and uploads a document or adds a web page.
2. The ingestion pipeline extracts the text and divides it into smaller chunks.
3. The application generates embeddings for the chunks and stores them in ChromaDB.
4. The user asks a question through the Gradio interface.
5. The retrieval module searches for relevant chunks using dense or hybrid retrieval.
6. The generation module sends the question and retrieved chunks to the configured LLM.
7. The LLM generates an answer based on the provided context.
8. The application displays the answer with citations and source information.
9. The conversation is saved in the notebook’s chat history.

The artifact generation module uses notebook content to generate reports, quizzes, and answer keys.

4. Retrieval Methods

The application supports two retrieval approaches.

Dense Retrieval

Dense retrieval converts the question and document chunks into embeddings. It compares the vectors using cosine similarity and returns the most relevant chunks.

Hybrid Retrieval

Hybrid retrieval combines dense retrieval with BM25 keyword search. Reciprocal Rank Fusion combines the two sets of results into a single ranked list.

Both approaches use the same general pipeline for generating answers. This makes it possible to compare their retrieval performance and answer quality.

5. Storage Design

Each notebook has its own storage directory containing:

* Notebook metadata
* Original uploaded documents
* Extracted text and chunks
* ChromaDB vector data
* Chat history
* Generated artifacts

The storage modules use a StorageBackend interface. The current implementation uses local filesystem storage.

This abstraction allows a cloud storage backend to be added in the future without requiring major changes to the other modules.

6. LLM Integration

The application supports Groq, Anthropic, and Gemini through a common LLM client.

The generation module provides the question, relevant document chunks, and instructions to answer using the retrieved sources.

The model is instructed to include citations and indicate when the available sources do not contain the requested information.

7. Deployment and CI/CD

The application is hosted on Render.

GitHub Actions runs a Python syntax check when changes are pushed to the main branch. If the check passes, the workflow triggers deployment through the Render deploy hook.

The deployment configuration and API credentials are managed through environment variables and GitHub secrets.

The deployed application uses FastEmbed with ONNX to reduce memory usage.

8. Design Decisions

The project uses a modular design to separate the interface, business logic, ingestion, retrieval, generation, and storage.

ChromaDB provides vector storage, while BM25 adds keyword-based retrieval for the hybrid search option.

A common LLM client makes it possible to switch between supported providers without rewriting the generation modules.

The storage abstraction separates file operations from the rest of the application, making future storage changes easier.

9. Limitations

The current deployment uses the free Render tier, so service startup can be delayed after inactivity. Local filesystem storage is not persistent across all service restarts or redeployments.

The application does not currently support OCR for scanned PDFs, website crawling, or user authentication.

The retrieval evaluation also uses a relatively small dataset, so additional experiments are needed to compare the retrieval methods more reliably.