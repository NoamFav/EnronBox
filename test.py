import ollama

response = ollama.chat(
    model="mistral",
    messages=[
        {
            "role": "user",
            "content": "Why is the sky blue?",
        },
    ],
)
print(response["message"]["content"])
