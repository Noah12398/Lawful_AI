import uuid
from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import json
import google.generativeai as genai
from gtts import gTTS
from flask_cors import CORS
import pygame
from flask import render_template
from dotenv import load_dotenv
import io  # Add this at the top

# Initialize Flask app and CORS
app = Flask(__name__, static_folder="static")

CORS(app)  # Allow all origins, adjust for security if needed
load_dotenv()

# Configure API Key for Generative AI
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# Ensure the static folder exists
if not os.path.exists("static"):
    os.makedirs("static")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat.html')
def chat():
    return render_template('chat.html')

# Function to generate chatbot response using the fine-tuned model
def chatbot_response(user_input, language):
    try:
        # Use the GenerativeModel class to generate the response
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        model = genai.GenerativeModel(
            model_name="tunedModels/copy-of-finalefinal-mm6hnii9n2pp",
            generation_config=generation_config,
        )

        # Send the user input directly to the model
        response = model.generate_content(f"Act as a lawyer and provide advice on {user_input}")
        
        # Replace sensitive symbols and adjust formatting
        return response.text.replace("**", "").replace("*", "").replace(".",".<br>")
    except Exception as e:
        return f"Error generating response: {str(e)}"

last_response_text = ""

@app.route('/process', methods=['POST'])
def process_input():
    global last_response_text
    data = request.get_json()
    user_message = data.get('text', '')
    tts_enabled = data.get('tts', False)
    selected_language = data.get('language', 'en')  # Capture the selected language, default to English

    if not user_message:
        return jsonify({"response": "No input provided"}), 400

    bot_response = chatbot_response(user_message, selected_language)  # Pass selected language to response generation
    last_response_text = bot_response  # Store response text

    if tts_enabled:
        try:
            # Check if the selected language is supported by gTTS
            tts = gTTS(text=bot_response, lang=selected_language)
            audio_io = io.BytesIO()
            tts.write_to_fp(audio_io)  # Correct way to save to BytesIO
            audio_io.seek(0)  # Rewind BytesIO before sending
            return send_file(audio_io, mimetype="audio/mpeg", as_attachment=False)
        except Exception as e:
            print(f"Error occurred during TTS: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"response": bot_response})

@app.route('/last_response', methods=['GET'])
def get_last_response():
    return jsonify({"response": last_response_text})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Default to 5000 if no PORT is set in .env
    app.run(host="0.0.0.0", port=port)
