import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyA7rTi4C3wSb5Uu4NXtQk-BbMvuXEwCYnM")

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="tunedModels/copy-of-finalefinal-mm6hnii9n2pp",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)