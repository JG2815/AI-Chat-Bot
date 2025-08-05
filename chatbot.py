import requests
import json

# LM Studio endpoint
API_URL = "http://127.0.0.1:1234/v1/chat/completions"

def change_persona(new_persona):
    """Initialize a new chat history with the new persona"""
    return [{
        "role": "user",
        "content": f"From now on, respond as a chatbot with the following personality: {new_persona}"
    }]

# Initial persona setup
persona = input("Describe the person you want to talk to:\n")
chat_history = change_persona(persona)

while True:
    user_input = input("You: ")
    
    # Handle special commands
    if user_input.lower() in ["exit", "quit"]:
        break
    elif user_input.lower().startswith("/change"):
        # Extract new persona from command (e.g., "/change Albert Einstein")
        new_persona = user_input[7:].strip()
        if new_persona:
            persona = new_persona
            chat_history = change_persona(persona)
            print(f"Character changed to: {persona}")
            continue
        else:
            print("Please specify a character (e.g., /change Albert Einstein)")
            continue

    chat_history.append({"role": "user", "content": user_input})

    payload = {
        "messages": chat_history,
        "temperature": 0.7,
        "max_tokens": 300,
        "stop": None,
        "stream": False,
        "model": "mistral"
    }

    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()
        
        # Get response from assistant
        bot_response = data["choices"][0]["message"]["content"]
        print("Bot:", bot_response)
        chat_history.append({"role": "assistant", "content": bot_response})
        
    except Exception as e:
        print(f"Error: {str(e)}")

print("Goodbye!")
