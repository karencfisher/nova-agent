import os
from dotenv import load_dotenv
import traceback
import json
from threading import Thread
from queue import Queue, Empty
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from agents.main_agent import MainAgent
from repositories.conversations import Conversations


app = Flask(__name__)
CORS(app)

message_queue = Queue()
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
agent = MainAgent(message_queue, api_key)

@app.route('/')
def home():
    return '<b>Here me are!</b>'

@app.route('/setup')
def setup():
    pass

@app.route('/message', methods=['POST'])
def message():
    try:
        data = request.get_json()
        message = data.get('message')
        msg_thread = Thread(target=agent.agent_step, args=(message,))
        msg_thread.start()
        return jsonify({"success": "OK"})
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
        return jsonify({"error": str(err)}), 500
    
@app.route('/get_conversations')
def get_conversations():
    try:
        result = Conversations.get_conversations()
        if result['error'] is not None:
            raise SystemError(result['error']) 
        return jsonify(result['data'])
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
        return jsonify({"error": str(err)}), 500
    
@app.route('/get_messages')
def get_messages():
    try:
        data = agent.chat_memory.get_chat_memory()
        print(f'Retrieved {len(data)} messages')
        messages = [
            message for message in data if 
            message['role'] in ['user', 'assistant'] and 
            message['content'] is not None
        ]
        return jsonify(messages)
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
        return jsonify([{"error": str(err)}]), 500
    
@app.route('/stream')
def stream():
    def event_stream():
        while True:
            try:
                msg = message_queue.get(timeout=10)
            except Empty:
                msg = ""
            else:
                msg = json.dumps(msg)
            yield f'data: {msg}\n\n'
    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
