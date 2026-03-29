from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import requests

app = Flask(__name__)
# 允許跨網域請求 (CORS)
CORS(app)

# 🚀 關鍵修復：建立一個偽裝成 Google Chrome 瀏覽器的 Session，避免被 Yahoo 阻擋
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
})

@app.route('/api/data')
def get_data():
    try:
        # 1. 獲取盈富基金 (2800.HK) 作為恆指最新 PE 參考
        pe = 8.75
        try:
            # 加入 session 偽裝
            tracker = yf.Ticker("2800.HK", session=session)
            pe = tracker.info.get('trailingPE', 8.75)
        except:
            pass

        # 2. 獲取恆生指數 (^HSI) 過去 20 年的真實價格
        hsi_history_data = {"dates": [], "prices": []}
        try:
            hsi = yf.Ticker("^HSI", session=session)
            hsi_hist = hsi.history(period="20y", interval="1mo")
            if not hsi_hist.empty:
                hsi_history_data["prices"] = [round(p, 2) for p in hsi_hist['Close'].dropna().tolist()]
                hsi_history_data["dates"] = [d.strftime('%Y-%m') for d in hsi_hist.dropna().index]
        except:
            pass

        # 3. 獲取其他資產近一年數據
        tickers = {
            'spx': '^GSPC', # 標普500
            'dji': '^DJI',  # 道瓊斯
            'ndx': '^IXIC', # 納斯達克
            'gold': 'GC=F', # 黃金
            'oil': 'CL=F'   # 原油
        }

        market_data = {}
        for key, symbol in tickers.items():
            try:
                t = yf.Ticker(symbol, session=session)
                hist = t.history(period="1y")
                if not hist.empty:
                    prices = [round(p, 2) for p in hist['Close'].dropna().tolist()]
                    dates = [d.strftime('%Y-%m-%d') for d in hist.index]
                    market_data[key] = {
                        "prices": prices,
                        "dates": dates
                    }
            except:
                continue

        # 4. 回傳 JSON 格式
        return jsonify({
            "status": "success",
            "hsi_pe": round(pe, 2),
            "hsi_history": hsi_history_data,
            "markets": market_data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
