from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pydantic import ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
from models import RandomWordResponse, RhymesResponse
import os

load_dotenv()

app = Flask(__name__)

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', api_key=os.getenv('GOOGLE_API_KEY'), temperature=1.0)

prompt = PromptTemplate(
    input_variables=["difficulty"],
    template=(
        "Generate one English word based on difficulty level '{difficulty}'.\n"
        "- Easy: many rhymes (e.g., cat, day)\n"
        "- Medium: moderate rhymes (e.g., never, matter)\n"
        "- Hard: few rhymes (e.g., orange, silver)\n"
        "Return only the word, no punctuation, no explanation."
    ),
)

parser = StrOutputParser()
chain = prompt | llm | parser
@app.route('/randomword')
def get_random_word():
    difficulty = request.args.get('difficulty', '').lower()
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': "Difficulty must be 'easy', 'medium', or 'hard'."}), 400
    try:
        response = chain.invoke(difficulty)
        word = response.strip().split()[0]
        result = RandomWordResponse(word=word)
        return jsonify({'word': result.word}), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.errors()}), 500
    except Exception as e:
        return jsonify({'error': 'Something went wrong', 'details': str(e)}), 500

@app.route('/rhymes')
def get_rhymes():
    word = request.args.get('word', '').lower()
    if not word:
        return jsonify({'error': "Please provide a 'word' parameter."}), 400

    try:
        url = f'https://wordsapiv1.p.rapidapi.com/words/{word}/rhymes'
        headers = {
            'x-rapidapi-host': 'wordsapiv1.p.rapidapi.com',
            'x-rapidapi-key': os.environ['RAPID_API_KEY']
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch rhymes.', 'details': response.text}), 500
        data = response.json()
        rhymes_list = data.get('rhymes', {}).get('all', [])
        result = RhymesResponse(word=word, rhymes=rhymes_list)
        return jsonify({'word': result.word, 'rhymes': result.rhymes}), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation failed.', 'details': e.errors()}), 500
    except Exception as e:
        return jsonify({'error': 'Something went wrong.', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run()