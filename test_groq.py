import os
from groq import Groq

# Create Groq client with your API key from environment variable
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("💬 Health Chatbot (type 'exit' to quit)")
print("--------------------------------------")

while True:
    user_input = input("> ")

    if user_input.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful health assistant."},
            {"role": "user", "content": user_input},
        ],
        model="llama-3.1-8b-instant",  # working Groq model
    )

    response = chat_completion.choices[0].message.content
    print("AI:", response)
