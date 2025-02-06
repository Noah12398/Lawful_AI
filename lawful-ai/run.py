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
def chatbot_response(user_input):
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
        
        return response.text.replace("**", "").replace("*", "").replace(".",".<br>")
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route('/process', methods=['POST'])
def process_input():
    data = request.get_json()
    user_message = data.get('text', '')
    tts_enabled = data.get('tts', False)
    
    if not user_message:
        return jsonify({"response": "No input provided"}), 400

    # Generate the chatbot response
    bot_response = chatbot_response(user_message)  # Assume this function generates the chatbot response
    
    if tts_enabled:
        try:
            # Generate unique filename for the TTS file
            filename = f"tts_output_{uuid.uuid4().hex}.mp3"
            filepath = os.path.join("static", filename)

            # Generate TTS and save the file
            tts = gTTS(text=bot_response, lang='en')
            tts.save(filepath)
            try:
                tts.save(filepath)
                print(f"Audio file saved at {filepath}")
            except Exception as e:
                print(f"Error saving TTS file: {str(e)}")

            # Return the audio URL to the client
            return jsonify({"response": bot_response, "audio_url": f"/static/{filename}"})
        
        except Exception as e:
            print(f"Error occurred during TTS: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"response": bot_response})

@app.route('/static/<path:filename>')
def serve_audio(filename):
    return send_from_directory("static", filename)

@app.route('/audio', methods=['GET'])
def get_audio():
    audio_path = 'static/output.mp3'  # Ensure this path is correct
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mpeg')
    return jsonify({"error": "Audio file not found"}), 404

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Default to 5000 if no PORT is set in .env
    app.run(host="0.0.0.0", port=port)
    
