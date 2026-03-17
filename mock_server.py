from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

data_store = {
    "event": "System Ready",
    "timestamp": 0.0
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CoreSport AI - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #080808; color: #ffffff; font-family: sans-serif; text-align: center; padding-top: 50px; }
        .card { background-color: #121212; border: 2px solid #ff8c00; border-radius: 20px; padding: 40px; display: inline-block; }
        .highlight { color: #ff8c00; font-weight: bold; font-size: 3rem; }
    </style>
    <meta http-equiv="refresh" content="1"> 
</head>
<body>
    <h1>CoreSport <span style="color:#ff8c00">AI</span></h1>
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
    global data_store
    if request.method == 'POST':
        incoming = request.json
        data_store["event"] = incoming.get("event", "none").upper()
        data_store["timestamp"] = incoming.get("timestamp", 0.0)
        return jsonify({"status": "success"}), 200
    return render_template_string(HTML_TEMPLATE, data=data_store)

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')