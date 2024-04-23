#!/usr/bin/env python3

from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
import openai
import os, sys, re
import logging
from sqlalchemy.exc import IntegrityError
import json

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Database connection info from environment variables
hostname = os.getenv('DB_HOST', 'localhost')
databasename = os.getenv('DB_NAME', 'chatdb')
username = os.getenv('DB_USER', 'chatuser')
password = os.getenv('DB_PASS', 'yourpassword')
port = os.getenv('DB_PORT', '5432')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{hostname}:{port}/{databasename}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# OpenAI API settings
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database models
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    feedback = db.Column(db.Boolean)

class KnowledgeBase(db.Model):
    __tablename__ = 'KnowledgeBase'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(450), unique=True, nullable=False)
    answer = db.Column(db.String, nullable=False)

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST', 'GET'])
def chat():
    if request.method == 'POST':
        user_input = request.json['question']
        return jsonify(process_post(user_input))
    elif request.method == 'GET':
        user_input = request.args.get('question')
        return Response(stream_with_context(stream_response(user_input)), mimetype='text/event-stream')
    else:
        return jsonify({'error': 'Method not allowed'}), 405

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    chat_id = data.get('chat_id')
    if not chat_id:
        return jsonify({'message': 'Chat ID is missing!'}), 400

    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({'message': 'Chat not found!'}), 404

    chat.feedback = data.get('feedback', True)
    if data.get('correct_answer'):
        chat.answer = data['correct_answer']
        db.session.commit()
        return jsonify({'message': 'Feedback received and chat updated!'})

    db.session.commit()
    return jsonify({'message': 'Feedback received!'})

def process_post(user_input):
    knowledge = KnowledgeBase.query.filter_by(question=user_input).first()
    if knowledge:
        return {'answer': knowledge.answer, 'chat_id': knowledge.id}

    response = openai.chat.completions.create(
        model="gpt-4",
        max_tokens=1500,
        messages=[
            {"role": "system", "content": "You are a skillful Technology Specialist. This is your blog called auroranrunner. Your name is Tapio Vaattanen."},
            {"role": "user", "content": user_input}
        ]
    )
    answer = response.choices[0].message.content.strip()
    answer = format_response(answer)

    try:
        new_knowledge = KnowledgeBase(question=user_input, answer=answer)
        db.session.add(new_knowledge)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        new_knowledge = KnowledgeBase.query.filter_by(question=user_input).first()
        answer = new_knowledge.answer  # Use existing answer if question was a duplicate

    new_chat = Chat(question=user_input, answer=answer, feedback=None)
    db.session.add(new_chat)
    db.session.commit()
    return {'answer': answer, 'chat_id': new_chat.id}

def stream_response(user_input):
    with app.app_context():
        yield "data: Checking for cached answers...\n\n"
        knowledge = KnowledgeBase.query.filter_by(question=user_input).first()
        if knowledge:
            yield f"data: {json.dumps({'answer': knowledge.answer, 'chat_id': knowledge.id})}\n\n"
        else:
            response = openai.chat.completions.create(
                engine="gpt-4",
                max_tokens=1500,
                messages=[
                    {"role": "system", "content": "You are a skillful Technology Specialist. This is your blog called auroranrunner. Your name is Tapio Vaattanen."},
                    {"role": "user", "content": user_input}
                ]
            )
            answer = response.choices[0].message.content.strip()
            answer = format_response(answer)

            new_knowledge = KnowledgeBase(question=user_input, answer=answer)
            db.session.add(new_knowledge)
            db.session.commit()

            new_chat = Chat(question=user_input, answer=answer, feedback=None)
            db.session.add(new_chat)
            db.session.commit()

            yield f"data: {json.dumps({'answer': answer, 'chat_id': new_chat.id})}\n\n"

def format_response(text):
    """
    Formats text by handling bold within numbered list items correctly,
    applying general text formatting, managing code blocks, and styling comments with # retained.
    """
    formatted_text = ""
    in_code_block = False  # Flag to check if inside a code block
    buffer = ""  # Buffer to store text for code blocks

    lines = text.split('\n')
    for line in lines:
        if line.strip().startswith("```"):  # Check for code block toggle
            in_code_block = not in_code_block
            if not in_code_block:
                formatted_text += f"<pre><code>{buffer}</code></pre>"
                buffer = ""
            continue

        if in_code_block:
            buffer += line + '\n'
            continue

        # Handling comments in the code specifically
        if line.strip().startswith("#"):
            formatted_text += f"<p><strong>{line.strip()}</strong></p>"
        else:
            # Handling bold within numbered list items
            search_result = re.search(r'^(\d+)\.\s+\*\*(.*?)\*\*:\s*(.*)$', line)
            if search_result:
                number, bold_text, the_rest = search_result.groups()
                formatted_text += f"<p>{number}. <strong>{bold_text}</strong>: {the_rest}</p>"
            else:
                # Apply bold text formatting for other lines
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                formatted_text += f"<p>{line}</p>"

    # Ensure closing code block if text ends within one
    if in_code_block:
        formatted_text += f"<pre><code>{buffer}</code></pre>"

    return formatted_text

@app.after_request
def apply_cors(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://www.auroranrunner.com'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
<<<<<<< HEAD

if __name__ == '__main__':
    context = ('/etc/letsencrypt/live/vauva.ampiainen.net/fullchain.pem', '/etc/letsencrypt/live/vauva.ampiainen.net/privkey.pem')
    app.run(debug=True, host='0.0.0.0', port=5004, ssl_context=context)
=======
>>>>>>> fe453444bdb1634afc6f5162d437598a79ca5101
