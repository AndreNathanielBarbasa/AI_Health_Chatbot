from groq import Groq

client = Groq()

print("💬 Health Chatbot (type 'exit' to quit)")
print("--------------------------------------")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("👋 Goodbye!")
        break

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # fast, good for testing
        messages=[{"role": "user", "content": user_input}]
    )

    print("AI:", response.choices[0].message.content)
