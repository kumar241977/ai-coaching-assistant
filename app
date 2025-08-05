from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>AI Coaching Assistant - Test Deployment</h1><p>App is working! ✅</p>"

@app.route('/api/test')
def test():
    return jsonify({"status": "working", "message": "Deployment successful!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
