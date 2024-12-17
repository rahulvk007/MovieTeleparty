from flask import Flask, render_template, request, jsonify
import uuid
import redis
import os

app = Flask(__name__)

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/create_session", methods=["GET", "POST"])
def create_session():
    if request.method == "POST":
        stream_url = request.form.get("stream_url")
        session_code = str(uuid.uuid4())[:6]  # Generate a 6-character session code
        
        # Store session in Redis
        redis_client.hmset(session_code, {"stream_url": stream_url, "position": 0, "paused": True})
        print(f"[DEBUG] New session created: {session_code}, Stream URL: {stream_url}")
        
        return render_template("watch.html", role="admin", session_code=session_code, stream_url=stream_url)
    return render_template("create_session.html")

@app.route("/join_session", methods=["GET", "POST"])
def join_session():
    if request.method == "POST":
        session_code = request.form.get("session_code")
        if redis_client.exists(session_code):
            stream_url = redis_client.hget(session_code, "stream_url")
            print(f"[DEBUG] User joined session: {session_code}")
            return render_template("watch.html", role="friend", session_code=session_code, stream_url=stream_url)
        else:
            print("[DEBUG] Invalid session code entered")
            return "Invalid Session Code", 400
    return render_template("join_session.html")

@app.route("/sync", methods=["POST"])
def sync():
    data = request.get_json()
    session_code = data.get("session_code")
    role = data.get("role")
    
    if redis_client.exists(session_code):
        session = redis_client.hgetall(session_code)

        if role == "admin":
            # Update session state from admin
            redis_client.hmset(session_code, {"position": data.get("position"), "paused": data.get("paused")})
            print(f"[DEBUG] Admin Sync -> Position: {data.get('position'):.2f}, Paused: {data.get('paused')}")
        
        # Send sync data to friends
        print(f"[DEBUG] Friend Sync -> Position Sent: {session['position']:.2f}, Paused: {session['paused']}")
        return jsonify(session)

    return "Session not found", 404

if __name__ == "__main__":
    app.run(debug=True)
