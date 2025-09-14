from flask import Flask, request, jsonify, render_template
from scraper import scrape_website, summarize_text, chat_with_llm, select_model
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_and_summarize():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Scrape the website
        scraped_text = scrape_website(url)

        # Summarize the scraped text
        summary = summarize_text(scraped_text)

        return jsonify({
            "scraped_text": scraped_text,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    context = data.get('context', '')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Generate a response using the selected model
        response = chat_with_llm(user_message, context)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/select_model', methods=['POST'])
def change_model():
    data = request.json
    model_name = data.get('model')

    if not model_name:
        return jsonify({"error": "Model name is required"}), 400

    try:
        # Change the selected model
        result = select_model(model_name)
        return jsonify({"message": result})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
