from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# In-memory storage for the latest detected event
data_store = {
    "event": "Waiting for shot...",
    "timestamp": 0.0
}

# Simple and clean UI dashboard to visualize shot data
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Basketball Shooting Detector</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #080808; color: #ffffff; font-family: sans-serif; text-align: center; padding-top: 50px; }
        h1 { color: #ffffff; font-size: 3rem; font-weight: bold; }
        .card { background-color: #121212; border: 2px solid #ff8c00; border-radius: 20px; padding: 40px; display: inline-block; }
        h3 { color: #ffffff; }
        h2 { color: #ffffff; }
        .highlight { color: #ff8c00; font-weight: bold; font-size: 3rem; }
    </style>
    <meta http-equiv="refresh" content="1"> 
</head>
<body>
    <h1> Basketball Shooting Detector</h1>
    <div class="card">
        <h3>Latest Event:</h3>
        <div class="highlight">{{ data.event }}</div>
        <h2>At: {{ data.timestamp }}s</h2>
    </div>
</body>
</html>
"""

@app.route('/event', methods=['GET', 'POST'])
def handle_event():
    """
    Handles both incoming shot events (POST) and dashboard viewing (GET).
    """
    global data_store
    
    if request.method == 'POST':
        # Process data sent from the main detection script
        incoming = request.json
        data_store["event"] = incoming.get("event", "none").upper()
        data_store["timestamp"] = incoming.get("timestamp", 0.0)
        
        # Return success to the client
        return jsonify({"status": "success"}), 200
    
    # Display the dashboard UI
    return render_template_string(HTML_TEMPLATE, data=data_store)

if __name__ == '__main__':
    # Run the server on port 5000, accessible locally
    app.run(port=5000, host='0.0.0.0')