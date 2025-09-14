import requests
from bs4 import BeautifulSoup
from groq import Groq
import re

# Initialize Groq client
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Available models (updated with current Groq models)
MODELS = {
    'Gemma2 💎': 'gemma2-9b-it',
    'Llama3.1 🦙': 'llama-3.1-8b-instant',
    'Mixtral New 🚀': 'mixtral-8x7b-32768'
}

# Default model
SELECTED_MODEL = MODELS['Llama3.1 🦙']

def clean_text(text):
    """Clean and format text by removing extra whitespace and special characters"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:]', '', text)
    return text.strip()

def scrape_website(url):
    """
    Scrape text content from a website.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text from paragraphs and headings
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        text_content = " ".join([element.get_text() for element in text_elements])
        
        # Clean the text
        text_content = clean_text(text_content)
        
        # Limit text length to avoid token limits
        if len(text_content) > 10000:
            text_content = text_content[:10000] + "... [text truncated]"
            
        return text_content if text_content else "No text content found on the page."
    except Exception as e:
        return f"Error scraping website: {str(e)}"

def summarize_text(text, model=SELECTED_MODEL):
    """
    Summarize text using the selected Groq model.
    """
    try:
        if text.startswith("Error scraping website"):
            return "Cannot summarize due to scraping error."
            
        # Truncate text if too long for the model
        if len(text) > 8000:
            text = text[:8000] + "... [text truncated for summarization]"
            
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries of web content."},
                {"role": "user", "content": f"Please provide a clear and concise summary of the following text:\n\n{text}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def chat_with_llm(message, context="", model=SELECTED_MODEL):
    """
    Generate a response using the selected Groq model.
    """
    try:
        # Prepare the prompt with context if available
        if context and not context.startswith("Error"):
            prompt = f"Context from scraped webpage:\n{context}\n\nUser question: {message}\n\nPlease answer based on the context when possible:"
        else:
            prompt = f"User question: {message}\n\nPlease answer helpfully:"
            
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context when available."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

def select_model(model_name):
    """
    Select the model for summarization and chatbot.
    """
    global SELECTED_MODEL
    if model_name in MODELS:
        SELECTED_MODEL = MODELS[model_name]
        return f"Model changed to {model_name}"
    else:
        return "Invalid model selected"