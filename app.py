import os
import redis
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create_session', methods=['POST'])
def create_session():
    stream_url = request.form['stream_url']
    session_code = "session123"  # Replace with random unique code logic
    redis_client.hmset(session_code, {"stream_url": stream_url, "position": 0, "paused": True})
    return jsonify({"session_code": session_code})

@app.route('/join_session', methods=['POST'])
def join_session():
    session_code = request.form['session_code']
    if redis_client.exists(session_code):
        stream_url = redis_client.hget(session_code, "stream_url")
        return jsonify({"stream_url": stream_url})
    return jsonify({"error": "Invalid session"}), 400

@app.route('/sync', methods=['POST'])
def sync():
    session_code = request.form['session_code']
    if redis_client.exists(session_code):
        position = redis_client.hget(session_code, "position")
        paused = redis_client.hget(session_code, "paused")
        return jsonify({"position": position, "paused": paused})
    return jsonify({"error": "Invalid session"}), 400

@app.route('/update_sync', methods=['POST'])
def update_sync():
    session_code = request.form['session_code']
    position = request.form['position']
    paused = request.form['paused']
    if redis_client.exists(session_code):
        redis_client.hmset(session_code, {"position": position, "paused": paused})
        return jsonify({"success": True})
    return jsonify({"error": "Invalid session"}), 400

if __name__ == '__main__':
    app.run(debug=True)
