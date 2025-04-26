import traceback
import json
from threading import Thread
from queue import Queue, Empty
from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
from agent import Agent
from utils.timer import timer

app = Flask(__name__)
message_queue = Queue()
agent = Agent(message_queue)
CORS(app)

@app.route('/')
def home():
    return render_template('chatbot.html')

@app.route('/message', methods=['POST'])
def message():
    try:
        data = request.get_json()
        message = data.get('message')
        img = data.get('img')
        msg_thread = Thread(target=agent.agent_step, args=(message, img))
        msg_thread.start()
        return jsonify({"success": "OK"})
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
        return jsonify({"error": str(err)}), 500
    
@app.route('/get_messages')
def get_messages():
    try:
        data = agent.chat_memory.get_chat_memory()
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
    app.run(debug=True, host='0.0.0.0', port=5000)
