import streamlit as st
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="PDF Chat Engine", page_icon="🤖")
st.title("📄 PDF Chat Engine")
st.write("Upload a PDF, ask questions, get answers grounded in the document.")

# ---------- API SETUP ----------
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------- SESSION STATE SETUP ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    # Extract text only once
    if st.session_state.pdf_text == "":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages[:3]:
            text += page.extract_text()
        st.session_state.pdf_text = text
        st.success(f"PDF loaded! Extracted {len(text)} characters.")

# ---------- QUESTION INPUT ----------
if st.session_state.pdf_text:
    question = st.text_input("Ask a question about the document:")

    if question:
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a document assistant. Answer the user's question using ONLY the information in the document provided below. If the answer is not in the document, say 'This information is not found in the document.' Do not use outside knowledge."},
                    {"role": "user", "content": f"Document:\n\n{st.session_state.pdf_text}\n\nQuestion: {question}"}
                ]
            )

        answer = response.choices[0].message.content

        # Add to chat history
        st.session_state.chat_history.append({"question": question, "answer": answer})

# ---------- DISPLAY CHAT HISTORY ----------
if st.session_state.chat_history:
    st.write("---")
    st.write("## Conversation History")

    for chat in st.session_state.chat_history:
        st.write(f"**Q:** {chat['question']}")
        st.write(f"**A:** {chat['answer']}")
        st.write("---")