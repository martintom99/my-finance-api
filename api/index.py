from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import requests

app = Flask(__name__)
CORS(app)

# 偽裝成瀏覽器，避免被 Yahoo 阻擋
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
})

@app.route('/api/data')
def get_data():
    try:
        # 1. 僅獲取最新 PE (極快)
        pe = 8.75
        try:
            tracker = yf.Ticker("2800.HK", session=session)
            pe = tracker.info.get('trailingPE', 8.75)
        except:
            pass

        # 2. 僅獲取其他資產近一年數據 (快)
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

        # 回傳 JSON 格式 (不再包含龐大的 20 年歷史資料)
        return jsonify({
            "status": "success",
            "hsi_pe": round(pe, 2),
            "markets": market_data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
