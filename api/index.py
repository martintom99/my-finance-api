from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
# 允許跨網域請求 (CORS)
CORS(app)

@app.route('/api/data')
def get_data():
    try:
        # 1. 獲取盈富基金 (2800.HK) 作為恆指最新 PE 參考
        pe = 8.75
        try:
            tracker = yf.Ticker("2800.HK")
            pe = tracker.info.get('trailingPE', 8.75)
        except:
            pass

        # 2. 獲取恆生指數 (^HSI) 過去 20 年的真實價格 (按月抓取以加快速度)
        hsi_history_data = {"dates": [], "prices": []}
        try:
            hsi = yf.Ticker("^HSI")
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
            t = yf.Ticker(symbol)
            hist = t.history(period="1y")
            if not hist.empty:
                prices = [round(p, 2) for p in hist['Close'].dropna().tolist()]
                dates = [d.strftime('%Y-%m-%d') for d in hist.index]
                market_data[key] = {
                    "prices": prices,
                    "dates": dates
                }

        # 4. 回傳 JSON 格式 (包含 hsi_history)
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
