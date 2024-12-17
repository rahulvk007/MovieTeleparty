from flask import Flask, render_template, request, jsonify
import uuid
import redis
import os

app = Flask(__name__)

# Redis configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# Initialize Redis connection
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/create_session", methods=["GET", "POST"])
def create_session():
    if request.method == "POST":
        stream_url = request.form.get("stream_url")
        session_code = str(uuid.uuid4())[:6]
        session_data = {
            "stream_url": stream_url,
            "position": 0,
            "paused": "True"  # Convert boolean to string "True"
        }
        # Store session data in Redis
        redis_client.hset(f"session:{session_code}", mapping=session_data)
        print(f"[DEBUG] New session created: {session_code}, Stream URL: {stream_url}")
        return render_template("watch.html", role="admin", session_code=session_code, stream_url=stream_url)
    return render_template("create_session.html")

@app.route("/join_session", methods=["GET", "POST"])
def join_session():
    if request.method == "POST":
        session_code = request.form.get("session_code")
        # Retrieve session data from Redis
        session_data = redis_client.hgetall(f"session:{session_code}")
        if session_data:
            stream_url = session_data["stream_url"]
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
    session_key = f"session:{session_code}"

    try:
        if redis_client.exists(session_key):
            if role == "admin":
                # Validate position
                position = data.get("position")
                if not isinstance(position, (int, float)):
                    try:
                        position = float(position)  # Try converting to a float
                    except (TypeError, ValueError):
                        return jsonify({"error": "Invalid position value"}), 400

                # Update session state from admin in Redis
                session_data = {
                    "position": position,
                    "paused": str(data.get("paused"))  # Convert boolean to string
                }
                redis_client.hset(session_key, mapping=session_data)
                print(f"[DEBUG] Admin Sync -> Position: {position:.2f}, Paused: {data.get('paused')}")

            # Retrieve updated session data from Redis
            session_data = redis_client.hgetall(session_key)

            # Convert 'paused' back to boolean for the client
            session_data["paused"] = session_data["paused"] == "True"

            # Convert position to float for formatting
            try:
                position = float(session_data['position'])
            except (KeyError, ValueError):
                position = 0.0  # Default value if conversion fails

            print(f"[DEBUG] Friend/Admin Sync -> Position Sent: {position:.2f}, Paused: {session_data['paused']}")
            return jsonify(session_data)
        else:
            return jsonify({"error": "Session not found"}), 404

    except redis.exceptions.RedisError as e:
        print(f"[ERROR] Redis error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)