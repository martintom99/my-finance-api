from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import requests

app = Flask(__name__)
CORS(app)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
})

@app.route('/api/data')
def get_data():
    try:
        # 1. 嘗試獲取真實 PE，不放任何假數字
        pe = None
        try:
            tracker = yf.Ticker("2800.HK", session=session)
            # 嘗試抓 trailingPE，如果沒有就抓 forwardPE
            info = tracker.info
            pe = info.get('trailingPE') or info.get('forwardPE')
        except Exception as e:
            print(f"PE 獲取失敗: {e}") # 這行會印在 Vercel 的後台 Logs 裡

        # 2. 獲取其他資產近一年數據
        tickers = {
            'spx': '^GSPC', 'dji': '^DJI', 'ndx': '^IXIC', 'gold': 'GC=F', 'oil': 'CL=F'
        }
        market_data = {}
        for key, symbol in tickers.items():
            try:
                t = yf.Ticker(symbol, session=session)
                hist = t.history(period="1y")
                if not hist.empty:
                    prices = [round(p, 2) for p in hist['Close'].dropna().tolist()]
                    dates = [d.strftime('%Y-%m-%d') for d in hist.index]
                    market_data[key] = {"prices": prices, "dates": dates}
            except:
                continue

        # 回傳 JSON
        return jsonify({
            "status": "success",
            "hsi_pe": round(pe, 2) if pe else "N/A", # 如果沒有真實數據，就回傳 N/A
            "markets": market_data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
