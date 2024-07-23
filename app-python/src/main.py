import os
from flask import Flask, jsonify, url_for, redirect

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    api_methods= {
        "Get metrics": "GET /metrics"
    }
    return jsonify(api_methods)

@app.route('/metrics', methods=['GET'])
def get_metrics():
    return jsonify({"data": "hola"})

if __name__ == '__main__':
    port = int(os.environ.get('APP_PORT', 2113))
    debug= bool(os.environ.get('APP_DEBUG',True))
    app.run(debug=True, port=port)
