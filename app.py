#!/usr/bin/env python

from flask import Flask, request, jsonify, render_template, Response, stream_with_context, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session  # Import Session
import openai
import os, sys, re
import logging
from sqlalchemy.exc import IntegrityError
import json

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Required for session management
app.config['SESSION_TYPE'] = 'filesystem'  # Specifies that the session will be stored in the filesystem
Session(app)  # Initialize the session

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
    session['chat_history'] = []  # Initialize chat history in the session
    return render_template('chat.html')

@app.route('/chat', methods=['POST', 'GET'])
def chat():
    if request.method == 'POST':
        user_input = request.json['question']
        session['chat_history'].append({'role': 'user', 'content': user_input})  # Add user input to chat history
        response = process_post(user_input)
        session['chat_history'].append({'role': 'assistant', 'content': response['answer']})  # Add response to chat history
        return jsonify(response)
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
    if 'chat_history' not in session:
        session['chat_history'] = []

    messages = session['chat_history']  # Retrieve existing chat history from session
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=generate_prompt(messages + [{'role': 'user', 'content': user_input}]),
        max_tokens=1500,
        stop=None
    )
    answer = response.choices[0].text.strip()
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
    # This part is similar and does not require modification for context management
    pass

def generate_prompt(messages):
    prompt = ""
    for message in messages:
        if message['role'] == 'user':
            prompt += f"User: {message['content']}\n"
        elif message['role'] == 'assistant':
            prompt += f"Assistant: {message['content']}\n"
    return prompt

def format_response(text):
    # Formatting code here
    return text

if __name__ == '__main__':
    context = ('/etc/letsencrypt/live/vauva.ampiainen.net/fullchain.pem', '/etc/letsencrypt/live/vauva.ampiainen.net/privkey.pem')
    app.run(debug=True, host='0.0.0.0', port=5005, ssl_context=context)
