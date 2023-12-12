import requests
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session


# Your OpenAI API key
api_key = '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'  # Replace with your actual OpenAI API key

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'ingenicows'  # Replace with your own secret key

# Flask-Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Function to interact with OpenAI's API
def get_gpt4_response(conversation_history):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo", ## This is where you can change the models
        "messages": conversation_history,
        "max_tokens": 300,
        "temperature": 0.4,
    }
    response = requests.post(url, headers=headers, json=data)
    print('Status Code:', response.status_code)
    if response.status_code == 200:
        message = response.json()['choices'][0]['message']
        return message['content']
    else:
        return f"Error: {response.status_code}"
        print('Error Response:', response.text)  # Additional debugging line
        return f"Error: {response.status_code}"

@app.route('/', methods=['GET', 'POST'])


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data sent with the POST request
        user_input = data['user_input']
        conversation_history = session.get('conversation_history', [])
        conversation_history.append({"role": "user", "content": user_input})

        # Call OpenAI API for a response
        bot_response = get_gpt4_response(conversation_history)
        if not bot_response.startswith("Error:"):
            # Add the bot response to the conversation history
            conversation_history.append({"role": "assistant", "content": bot_response})
            session['conversation_history'] = conversation_history

            # Return just the bot's response text for the AJAX call to use
            return jsonify({'message': bot_response})
        else:
            return jsonify({'error': bot_response}), 500

    # For a GET request, just render the chat page
    return render_template('index.html', conversation_history=session.get('conversation_history', []))
@app.route('/clear_session', methods=['POST'])
def clear_session():
    session.clear()  # This clears the session
    return jsonify(success=True)


# Run the app
if __name__ == '__main__':
    app.run()