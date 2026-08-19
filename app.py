import streamlit as st
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="PDF Chat Engine", page_icon="🤖")
st.title("📄 PDF Chat Engine")
st.write("Upload any PDF, ask questions, get answers grounded in the document.")

# ---------- API SETUP ----------
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []

# ---------- CHUNKING FUNCTION ----------
def chunk_text(text, chunk_size=2000, overlap=200):
    """Split text into overlapping chunks of ~2000 characters."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

# ---------- SIMPLE RELEVANCE SEARCH ----------
def find_relevant_chunk(question, chunks):
    """Find the chunk most likely to contain the answer."""
    best_chunk = ""
    best_score = 0

    for chunk in chunks:
        # Count how many question words appear in this chunk
        question_words = set(question.lower().split())
        chunk_words = set(chunk.lower().split())
        score = len(question_words & chunk_words)

        if score > best_score:
            best_score = score
            best_chunk = chunk

    # If no word overlap, return first chunk
    return best_chunk if best_chunk else chunks[0]

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    if st.session_state.chunks == []:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        st.session_state.chunks = chunk_text(text)
        st.success(f"PDF loaded! Extracted {len(text)} characters into {len(st.session_state.chunks)} chunks.")

# ---------- QUESTION INPUT ----------
if st.session_state.chunks:
    question = st.text_input("Ask a question about the document:")

    if question:
        relevant_chunk = find_relevant_chunk(question, st.session_state.chunks)

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a document assistant. Answer the user's question using ONLY the information in the document provided below. If the answer is not in the document, say 'This information is not found in the document.' Do not use outside knowledge."},
                    {"role": "user", "content": f"Document excerpt:\n\n{relevant_chunk}\n\nQuestion: {question}"}
                ]
            )

        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"question": question, "answer": answer})

# ---------- DISPLAY CHAT HISTORY ----------
if st.session_state.chat_history:
    st.write("---")
    st.write("## Conversation History")

    for chat in st.session_state.chat_history:
        st.write(f"**Q:** {chat['question']}")
        st.write(f"**A:** {chat['answer']}")
        st.write("---")