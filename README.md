# Structured-Questionnaire-Answering-Tool

## Overview

This project is an AI-powered structured questionnaire answering system built as part of the GTM Engineering Internship assignment.

The tool automates the workflow of answering structured questionnaires (e.g., security reviews, compliance forms, vendor assessments) using uploaded internal reference documents as the source of truth.

The system ensures answers are grounded in reference data and provides citations, confidence scores, and evidence snippets for transparency.

---

## Industry & Context Setup

**Industry Chosen:** B2B SaaS (Security & Compliance)

**Fictional Company:** SecureFlow AI

SecureFlow AI is a B2B SaaS company providing workflow automation solutions for financial institutions. The platform prioritizes data security, compliance, and operational transparency while managing sensitive financial data.

The system demonstrates how such a company could automatically respond to structured security questionnaires using internal policy documents.

---

## What I Built

A full end-to-end web application that allows users to:

- Register and log in
- Upload a questionnaire (PDF or TXT)
- Upload reference documents (PDF or TXT)
- Automatically generate answers grounded in references
- Review and edit answers
- Export the completed questionnaire
- View citations, confidence scores, and evidence snippets
- View a coverage summary of answered vs unanswered questions

---

## Architecture & Workflow

### 1. Authentication
- Simple user authentication using SQLite.
- Credentials stored persistently.

### 2. Document Upload
- Supports PDF and TXT formats.
- PDFs are parsed using `pypdf`.

### 3. Question Parsing
- Questionnaire is split into structured questions.
- Only numbered questions are extracted to avoid parsing noise.

### 4. Retrieval-Augmented Generation (RAG)

The system uses a simplified RAG architecture:

- Reference documents are chunked into smaller text segments.
- Each chunk is converted into embeddings using OpenAI’s `text-embedding-3-small`.
- When a question is asked:
  - The question is embedded.
  - Cosine similarity is used to retrieve the top relevant chunks.
  - Retrieved chunks are passed to the LLM as grounded context.
- The model generates an answer strictly from the provided context.

If the similarity score is too low, the system returns:
> "Not found in references."

---

## AI & Grounding Strategy

To ensure transparency and reliability:

- Each answer includes:
  - Citation (source file name)
  - Confidence score (based on cosine similarity)
  - Evidence snippets (retrieved text segments)
- The model is explicitly instructed to avoid hallucination.
- If no supporting evidence exists, the answer is rejected.

This approach reduces hallucination and keeps outputs grounded in source data.

---

## Database

SQLite is used for:
- User authentication storage
- Persistent system state

For this assignment, document storage is handled in-memory after upload to keep the implementation simple and focused.

---

## Trade-offs Made

- Used in-memory embedding computation instead of a vector database for simplicity.
- Chunking is character-based rather than semantic chunking.
- Export formatting is simple text instead of fully structured PDF reconstruction.
- Embeddings are recomputed per run instead of being cached.

These trade-offs were made to prioritize clarity, functionality, and simplicity within assignment scope.

---

## Assumptions

- Questionnaires are structured and numbered.
- Reference documents are reliable sources of truth.
- Uploaded documents are reasonably formatted for text extraction.

---

## Improvements With More Time

If extended further, I would:

- Add a vector database (e.g., FAISS) for persistent embeddings.
- Implement smarter semantic chunking.
- Cache embeddings to reduce repeated API calls.
- Improve PDF export formatting to match original structure exactly.
- Add version history to compare multiple answer generations.
- Add partial regeneration for selected questions.

---

## Tech Stack

- Python
- Streamlit (Frontend + UI)
- SQLite (Persistence)
- OpenAI API (Embeddings + LLM)
- Scikit-learn (Cosine Similarity)
- pypdf (PDF parsing)
- python-dotenv (Secure API key handling)

---

## Key Design Focus

The primary goal was not UI polish but:

- Clear system structure
- Grounded AI outputs
- Transparency in answer generation
- Logical workflow from upload to export
- Practical, applied RAG implementation

---

## Running the Application

1. Install dependencies:
pip install -r requirements.txt

2. Add your OpenAI API key in a `.env` file:
OPENAI_API_KEY=your_key_here

4. Run the app:
streamlit run app.py


---

## Final Note

This project focuses on demonstrating structured problem-solving, applied AI integration, and clarity of reasoning rather than production-scale infrastructure.

The goal was to build a smaller, complete system that works end-to-end and clearly shows the design decisions involved in building AI-assisted workflows.
