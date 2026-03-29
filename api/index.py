from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

@app.route('/api/data')
def get_data():
    debug_logs = {}
    try:
        # 1. 獲取真實 PE (讓 yfinance 自己處理連線)
        pe = None
        try:
            tracker = yf.Ticker("2800.HK") 
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
                t = yf.Ticker(symbol)
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
            "debug": debug_logs
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
