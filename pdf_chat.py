import os
from dotenv import load_dotenv

load_dotenv()
from pypdf import PdfReader
from openai import OpenAI

# ---------- STEP 1: EXTRACT TEXT FROM PDF ----------
reader = PdfReader("diabetes.pdf")

text = ""
for page in reader.pages[:3]:
    text += page.extract_text()

print("PDF loaded successfully.")
print(f"Extracted {len(text)} characters from the document.\n")

# ---------- STEP 2: CONNECT TO GROQ ----------
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------- STEP 3: ASK A QUESTION ----------
question =input( "Ask the question?")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a document assistant. Answer the user's question using ONLY the information in the document provided below. If the answer is not in the document, say 'This information is not found in the document.' Do not use outside knowledge."},
        {"role": "user", "content": f"Document:\n\n{text}\n\nQuestion: {question}"}
    ]
)

# ---------- STEP 4: PRINT THE ANSWER ----------
answer = response.choices[0].message.content
print("QUESTION:", question)
print("\nANSWER:", answer)
