from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Use environment variable for API URL with fallback
API_URL = os.getenv('API_URL', 'http://localhost:1234/v1/chat/completions')

# Initialize chat histories for different sessions
chat_sessions = {}

@app.route('/')
def index():
    return render_template('index.html', welcome_message="Who would you like to talk to? (e.g., 'William Shakespeare', 'Marie Curie', 'Sherlock Holmes')")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    session_id = data.get('session_id', 'default')
    
    # Clear existing session if requested
    if session_id not in chat_sessions or data.get('new_chat', False):
        persona = data.get('persona', 'a helpful assistant')
        chat_sessions[session_id] = [
            {
                "role": "user",
                "content": f"From now on, you are roleplaying as {persona}. Stay in character at all times. Never break character or acknowledge that you are an AI. Please respond as {persona} would."
            }
        ]

    # Add user message to chat history
    chat_sessions[session_id].append({"role": "user", "content": user_message})

    payload = {
        "messages": chat_sessions[session_id],
        "temperature": 0.9,  # Increased for more creative responses
        "max_tokens": 300,
        "stop": None,
        "stream": False,
        "model": "mistral"
    }

    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()
        
        # Print response for debugging
        print("API Response:", data)
        
        if 'choices' not in data:
            return jsonify({"error": f"Unexpected API response format: {data}"})
            
        if not data['choices'] or not isinstance(data['choices'], list):
            return jsonify({"error": "No choices in response"})
            
        bot_message = data['choices'][0]['message']['content']

        # Add bot response to chat history
        chat_sessions[session_id].append({"role": "assistant", "content": bot_message})

        return jsonify({"response": bot_message})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"})
    except KeyError as e:
        return jsonify({"error": f"Missing key in response: {str(e)}"})
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
