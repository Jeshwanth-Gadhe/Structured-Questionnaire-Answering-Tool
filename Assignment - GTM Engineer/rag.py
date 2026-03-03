# rag.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------- TEXT CHUNKING ---------------- #

def chunk_text(text, chunk_size=500):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks


# ---------------- EMBEDDINGS ---------------- #

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


# ---------------- RETRIEVAL ---------------- #

def retrieve_relevant_chunks(question, documents, top_k=3):
    all_chunks = []
    sources = []

    for doc_name, content in documents:
        chunks = chunk_text(content)
        for chunk in chunks:
            all_chunks.append(chunk)
            sources.append(doc_name)

    if not all_chunks:
        return []

    chunk_embeddings = [get_embedding(chunk) for chunk in all_chunks]
    question_embedding = get_embedding(question)

    similarities = cosine_similarity(
        [question_embedding],
        chunk_embeddings
    )[0]

    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            "chunk": all_chunks[idx],
            "source": sources[idx],
            "score": similarities[idx]
        })

    return results


# ---------------- ANSWER GENERATION ---------------- #

def generate_answer(question, retrieved_chunks, threshold=0.25):
    if not retrieved_chunks:
        return "Not found in references.", [], 0.0, []

    best_score = retrieved_chunks[0]["score"]

    context = "\n\n".join([item["chunk"] for item in retrieved_chunks])

    prompt = f"""
You are a compliance assistant.

Answer the question strictly using the provided context.
If the answer cannot be found in the context, respond exactly with:
Not found in references.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content.strip()

    if best_score < threshold:
        return "Not found in references.", [], best_score, []

    citations = list(set([item["source"] for item in retrieved_chunks]))
    evidence_snippets = [item["chunk"][:300] for item in retrieved_chunks]

    return answer, citations, best_score, evidence_snippets