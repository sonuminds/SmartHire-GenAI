import faiss
import numpy as np

from src.config import client, CAREER_NOTES_DIR


def load_career_notes():
    notes = []

    for file in CAREER_NOTES_DIR.glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            notes.append({
                "filename": file.name,
                "content": f.read()
            })

    return notes


def chunk_notes(notes, chunk_size=500, overlap=100):
    chunks = []

    for note in notes:
        text = note["content"]

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunks.append({
                "source": note["filename"],
                "text": text[start:end]
            })

            start += chunk_size - overlap

    return chunks


def embed_chunks(chunks):
    texts = [chunk["text"] for chunk in chunks]

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts
    )

    return [embedding.values for embedding in response.embeddings]


def build_notes_index(chunk_embeddings):
    matrix = np.array(
        chunk_embeddings,
        dtype="float32"
    )

    index = faiss.IndexFlatL2(matrix.shape[1])
    index.add(matrix)

    return index


def ask_mentor(question, chunks, notes_index, top_k=3):

    question_vector = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    ).embeddings[0].values

    question_vector = np.array(
        [question_vector],
        dtype="float32"
    )

    distances, indices = notes_index.search(
        question_vector,
        top_k
    )

    context = "\n\n".join(
        chunks[i]["text"]
        for i in indices[0]
    )

    prompt = f"""
You are SmartHire's AI Career Mentor.

Answer ONLY using the supplied context.

If the answer cannot be found in the context, reply exactly:

I don't know based on the provided career notes.

Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    return response.text