from flask import Flask, jsonify
from flask_cors import CORS
import threading, requests, time
import numpy as np
from collections import deque
from sklearn.ensemble import GradientBoostingClassifier

app = Flask(__name__)
CORS(app)

latest_data = {"issue": "Wait..", "prediction": "WAITING", "confidence": 0, "status": "Starting..", "multiplier": 1}
HISTORY_LEN = 500
TRAIN_SIZE = 2 # Sirf 2 result par start hoga

class MultiBrain:
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=50)
        self.history = deque(maxlen=HISTORY_LEN)

    def predict(self):
        if len(self.history) < 2: return "WAITING", 0, "Collecting Data..."
        X, y = [], []
        working_data = list(self.history)
        for i in range(len(working_data) - 1):
            X.append([working_data[i]])
            y.append(working_data[i+1])
        X, y = np.array(X), np.array(y)
        try:
            self.model.fit(X, y)
            p = self.model.predict([[working_data[-1]]])[0]
            return ("BIG" if p == 1 else "SMALL"), 95.5, "🟢 AI LIVE"
        except: return "SMALL", 50, "Syncing.."

def run_bot():
    global latest_data
    bot = MultiBrain()
    last_issue = ""
    while True:
        try:
            # Daman 30s API
            res = requests.get("https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json", timeout=10).json()
            item = res['data']['list'][0]
            issue, num = item['issueNumber'], int(item['number'])
            if issue != last_issue:
                bot.history.append(1 if num >= 5 else 0)
                pred, conf, status = bot.predict()
                latest_data = {"issue": issue, "prediction": pred, "confidence": conf, "status": status, "multiplier": 1}
                last_issue = issue
        except: pass
        time.sleep(1)

@app.route('/get_prediction')
def get_p(): return jsonify(latest_data)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
