import os
from dotenv import load_dotenv

load_dotenv()
import streamlit as st
from pypdf import PdfReader
from openai import OpenAI

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="PDF Chat Engine", page_icon="🤖")
st.title("📄 PDF Chat Engine")
st.write("Upload a PDF, ask questions, get answers grounded in the document.")

# ---------- API SETUP ----------
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    # Extract text
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages[:3]:
        text += page.extract_text()

    st.success(f"PDF loaded! Extracted {len(text)} characters.")

    # Question input
    question = st.text_input("Ask a question about the document:")

    if question:
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a document assistant. Answer the user's question using ONLY the information in the document provided below. If the answer is not in the document, say 'This information is not found in the document.' Do not use outside knowledge."},
                    {"role": "user", "content": f"Document:\n\n{text}\n\nQuestion: {question}"}
                ]
            )

        answer = response.choices[0].message.content
        st.write("### Answer:")
        st.write(answer)
