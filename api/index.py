from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import requests

app = Flask(__name__)
CORS(app)

# 🚀 升級版偽裝：加入完整的真實瀏覽器特徵，突破 Yahoo 封鎖
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
})

@app.route('/api/data')
def get_data():
    debug_logs = {}
    try:
        # 1. 獲取真實 PE
        pe = None
        try:
            tracker = yf.Ticker("2800.HK", session=session)
            pe = tracker.info.get('trailingPE') or tracker.info.get('forwardPE')
        except Exception as e:
            debug_logs['pe_error'] = str(e)

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
                else:
                    debug_logs[key] = "Yahoo 回傳了空資料"
            except Exception as e:
                debug_logs[key] = str(e)

        return jsonify({
            "status": "success",
            "hsi_pe": round(pe, 2) if pe else "N/A",
            "markets": market_data,
            "debug": debug_logs # 把錯誤訊息傳給前端，方便我們抓蟲
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
