NotebookLM Clone

An AI-powered research assistant inspired by Google NotebookLM. This application allows users to upload documents, ask questions about their sources, generate AI-powered summaries, and create useful artifacts using Retrieval-Augmented Generation (RAG).

Live Application: https://notebooklm-clone-yck6.onrender.com
GitHub Repository: https://github.com/Sushmitha-balu/notebooklm-clone

1. Project Overview

The NotebookLM Clone is a web-based AI research assistant that helps users understand and interact with their documents. Instead of manually reading large documents, users can upload their sources and ask questions in natural language.

The system retrieves relevant information from the uploaded documents and uses a language model to generate context-aware responses.

The project demonstrates the integration of document processing, embeddings, vector-based retrieval, large language models (LLMs), and a user-friendly interface.

2. Key Features

Document Management

* Upload and manage research documents.
* Organize sources within notebooks.
* Process uploaded documents for retrieval and question answering.

AI-Powered Question Answering

* Ask questions about uploaded documents.
* Retrieve relevant information using semantic search.
* Generate answers grounded in the available source material.

Retrieval-Augmented Generation (RAG)

* Split documents into smaller chunks.
* Generate embeddings for document chunks.
* Retrieve relevant chunks based on user questions.
* Provide retrieved context to the language model to generate answers.

Summarization and Artifact Generation

* Generate summaries of source material.
* Create useful AI-generated content from uploaded documents.
* Support research and information extraction workflows.

Web-Based Interface

* Interact with the application through a web interface.
* Manage notebooks and their associated sources.
* Ask questions and view generated responses.

Deployment and Continuous Integration

* Deploy the application as a web application.
* Use GitHub for source code management.
* Use GitHub Actions for automated checks and CI/CD workflows.

3. System Architecture

The application follows a modular architecture that connects the user interface, document ingestion, retrieval pipeline, and language model.

High-Level Architecture

                +-------------------------+
                |         User            |
                +------------+------------+
                             |
                             v
                +-------------------------+
                |      Web Interface      |
                |  Notebooks, Sources,    |
                |  Questions, Responses   |
                +------------+------------+
                             |
                             v
                +-------------------------+
                |     Application Layer   |
                | Request Processing and  |
                | Workflow Coordination   |
                +------------+------------+
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
      +-------------------+   +----------------------+
      | Document Ingestion|   | Question Answering   |
      | and Processing    |   | Pipeline             |
      +---------+---------+   +----------+-----------+
                |                        |
                v                        v
      +-------------------+   +----------------------+
      | Text Extraction   |   | Query Embedding      |
      | and Chunking      |   | and Retrieval        |
      +---------+---------+   +----------+-----------+
                |                        |
                v                        v
      +-------------------+   +----------------------+
      | Embeddings and    |<->| Relevant Document    |
      | Vector Storage    |   | Chunks                |
      +-------------------+   +----------+-----------+
                                         |
                                         v
                              +----------------------+
                              | LLM Response         |
                              | Generation           |
                              +----------+-----------+
                                         |
                                         v
                              +----------------------+
                              | Answer to User       |
                              +----------------------+
The diagram represents the logical architecture of the system. The exact implementation details depend on the components and services configured in the codebase.

For the detailed architecture, component interactions, and RAG data flow, see docs/ARCHITECTURE.md⁠￼.

4. How the RAG Pipeline Works

The Retrieval-Augmented Generation pipeline connects document retrieval with language-model-based answer generation.

Step 1: Document Ingestion

The user uploads a document to the application. The system processes the uploaded source and extracts its text.

Step 2: Text Chunking

The extracted text is divided into smaller chunks. Chunking allows the system to retrieve relevant portions of a document rather than processing the entire document for every question.

Step 3: Embedding Generation

The system converts document chunks into numerical vector representations called embeddings. These embeddings capture semantic information that helps identify relevant content.

Step 4: Storage and Indexing

The document chunks and their embeddings are stored or indexed using the application’s configured storage and retrieval components.

Step 5: Query Processing

When the user asks a question, the system processes the query and uses the retrieval mechanism to find relevant document chunks.

Step 6: Context Retrieval

The most relevant retrieved chunks are selected and provided as context for response generation.

Step 7: Answer Generation

The language model uses the question and retrieved context to generate a response grounded in the available sources.

Step 8: Response Display

The generated response is returned to the web interface and displayed to the user.

RAG workflow:
Uploaded Documents
        |
        v
   Text Extraction
        |
        v
    Text Chunking
        |
        v
 Embedding Generation
        |
        v
 Storage / Indexing
        |
        v
   User Question
        |
        v
 Query Processing
        |
        v
 Relevant Chunk Retrieval
        |
        v
 Context + User Question
        |
        v
  LLM Answer Generation
        |
        v
    Final Response

5. Technologies Used

The project integrates technologies for application development, document processing, information retrieval, language-model interaction, and deployment.

The exact versions and dependencies should be verified in the project’s configuration files.
Component

Purpose

Web frontend

Provides the user interface

Application backend

Handles application logic and requests

Large Language Model (LLM)

Generates answers and summaries

Embedding model

Converts text into vector representations

Vector retrieval or search component

Finds relevant document chunks

Document processing

Extracts and prepares source content

GitHub

Source code management and collaboration

GitHub Actions

Automated workflows and CI/CD

Render

Hosts the deployed application

Refer to the project’s dependency and configuration files for the exact frameworks, libraries, models, and storage technologies used.

6. Supported Sources

The application is designed to work with uploaded source material.

The exact supported formats depend on the document-processing implementation. Refer to the application’s upload interface and source code to verify which file types are currently supported.

7. Installation and Setup

Follow these steps to run the project locally.

Prerequisites

* Git
* The runtime required by the project
* The package manager used by the project
* Required API keys or environment variables, if applicable

Step 1: Clone the Repository

git clone https://github.com/Sushmitha-balu/notebooklm-clone.git

Step 2: Navigate to the Project
cd notebooklm-clone

Step 3: Install Dependencies

Use the package manager appropriate for the project’s configuration files.

For an npm-based project:
npm install

Step 4: Configure Environment Variables

If the application requires API keys or other environment variables, configure them according to the project’s existing environment configuration and deployment settings.

Do not commit secret keys, passwords, or private credentials to GitHub.

Step 5: Start the Application

For an npm-based project, the development command is commonly:
npm run dev

Check package.json for the actual scripts supported by the project.

Step 6: Open the Application

Open the local address displayed in the terminal after the development server starts.

8. Running Tests

Run the tests configured in the project.

For an npm-based project, the test command may be:
npm test

Check package.json to confirm the available test scripts.

Testing helps identify errors in application behavior and ensures that changes do not break existing functionality.

9. RAG Evaluation

The quality of the RAG pipeline should be evaluated using representative questions and the documents available to the system.

The evaluation should record the following information:
Evaluation Metric

Description

Test Question

The question submitted to the application

Retrieved Chunks

The document chunks retrieved for the question

Response Time

The time required to produce the answer

Answer Quality

Whether the answer correctly addresses the question

Grounding

Whether the answer is supported by the retrieved context

Observations

Errors, missing information, or retrieval issues
Evaluation Procedure

1. Prepare a set of questions based on the uploaded documents.
2. Submit each question to the application.
3. Record the retrieved chunks, when accessible.
4. Measure the response time.
5. Compare the generated answer with the information in the source documents.
6. Identify incorrect answers, missing context, or retrieval problems.
7. Summarize the results and identify possible improvements.

Evaluation Results


Evaluation Conclusion
Write the conclusion after completing the experiments. Discuss whether the system retrieves relevant document content, generates grounded answers, and responds within an acceptable time.

Deployment

The application is deployed on Render.

Live application: https://notebooklm-clone-yck6.onrender.com

Deployment allows users to access the application through a web browser without running the project locally.

For deployment, verify the configured build command, start command, environment variables, and deployment settings in the hosting dashboard.

11. Continuous Integration and Continuous Deployment (CI/CD)

The project uses GitHub for version control and GitHub Actions for configured automated workflows.

A typical CI/CD workflow includes:

1. A developer pushes changes to the GitHub repository.
2. GitHub Actions runs the checks configured in the workflow.
3. The workflow reports whether the checks succeed or fail.
4. If deployment is configured to run on the relevant event, the hosting service builds and deploys the application.
5. The deployed application is checked to confirm that it works correctly.

The exact triggers and deployment behavior depend on the workflow configuration and Render integration.

Workflow configuration files are located in:
.github/
└── workflows/

12. Project Structure

The project structure depends on the implementation. A typical organization may include the following components:
notebooklm-clone/
│
├── README.md
├── docs/
│   └── ARCHITECTURE.md
├── .github/
│   └── workflows/
├── src/
├── tests/
├── package.json
└── configuration files

13. Current Limitations

The following are potential limitations to investigate and document based on actual testing:

* Generated answers may be incomplete if relevant information is not retrieved.
* Answer quality depends on the source documents and retrieval process.
* Document extraction may vary depending on the file format.
* Large documents may require careful chunking and retrieval configuration.
* Language-model responses may occasionally contain incorrect information.
* Application performance may depend on model response time and hosting resources.

Only list limitations that are relevant to the current implementation or have been observed during testing.

14. Future Improvements

Potential improvements include:

* Improving chunking strategies and retrieval relevance.
* Adding source citations to generated answers.
* Expanding supported document formats.
* Improving evaluation with a larger set of test questions.
* Adding more robust error handling.
* Improving response-time monitoring.
* Enhancing notebook organization and source management.
* Adding automated tests for ingestion, retrieval, and answer generation.

15. Project Deliverables

The project deliverables include:

* A working web application.
* Source code maintained in GitHub.
* A documented system architecture.
* A functional document ingestion and RAG pipeline.
* RAG evaluation results based on actual experiments.
* Deployment through a publicly accessible application.
* CI/CD workflow evidence.
* A short screen recording demonstrating the deployed application and successful CI/CD deployment.

16. Conclusion

The NotebookLM Clone demonstrates how document ingestion, semantic retrieval, and large language models can be combined to build an AI-powered research assistant.

The application allows users to interact with uploaded documents through natural-language questions and generated responses. The project also provides an opportunity to evaluate retrieval quality, answer grounding, response time, and the reliability of the complete RAG pipeline.

The deployed application, source code, architecture documentation, and evaluation results together demonstrate the design and implementation of the system.