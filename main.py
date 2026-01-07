import requests
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Naya data store karne ke liye
latest_data = {"issue": "Loading..", "prediction": "WAITING", "status": "Connecting.."}

def run_bot():
    global latest_data
    while True:
        try:
            # Seedha aapke Netherlands server se data fetch
            res = requests.get('http://194.5.159.86:5000/get_data', timeout=10).json()
            if res and 'data' in res:
                item = res['data']['list'][0]
                issue = item['issueNumber']
                num = int(item['number'])
                pred = "BIG" if num >= 5 else "SMALL"
                latest_data = {"issue": issue, "prediction": pred, "status": "🟢 AI LIVE"}
        except Exception as e:
            latest_data["status"] = "Syncing.."
        time.sleep(2)

@app.route('/get_prediction')
def get_p():
    return jsonify(latest_data)

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
