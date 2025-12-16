from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pydantic import ValidationError
from models import RandomWordResponse
import os
import pronouncing
from wordfreq import zipf_frequency


load_dotenv()

app = Flask(__name__)
CORS(app)

client = InferenceClient(api_key=os.getenv('HF_TOKEN'))

@app.route('/randomword')
def get_random_word():
    difficulty = request.args.get('difficulty', '').lower()
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': "Difficulty must be 'easy', 'medium', or 'hard'."}), 400
    try:
        response = client.chat.completions.create(
        model="Qwen/Qwen3-4B-Instruct-2507",
        messages=[
            {
                "role": "system",
                "content": 
                    "You are an expert in English vocabulary. Generate one English dictionary word based on the gievn difficulty level. For example: "
                    "- Easy: many rhymes\n"
                    "- Medium: moderate rhymes\n"
                    "- Hard: few rhymes\n"
                    "Return only the word, no punctuation, no explanation. Give different word each time"
            },
            {
                "role": "user",
                "content": f"Give a random word from english dictionary with {difficulty} difficulty to rhyme with."
            }
        ],
        temperature=1.5,
        frequency_penalty=1.5,
        )
        result = RandomWordResponse(word=response.choices[0].message.content)
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
        rhymes = pronouncing.rhymes(word)
        rhyme_freq = {}
        for rhyme in rhymes:
            freq = zipf_frequency(rhyme, "en")
            rhyme_freq[rhyme] = freq
        return jsonify({'rhymes_frequencies': rhyme_freq}), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation failed.', 'details': e.errors()}), 500
    except Exception as e:
        return jsonify({'error': 'Something went wrong.', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run()