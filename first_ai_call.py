import os
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a Market surveyor and data analyst. You have expertise in analyzing market trends, consumer behavior, and competitive landscapes. Your task is to provide insights and recommendations based on the data provided."},
        {"role": "user", "content": "Tell me the chance of earning for a AI integration startup in the current market, specificaly on freelance platforms."}
    ]
)

print(response.choices[0].message.content)

