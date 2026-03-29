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

        # 🟢 加入這段：3. 獲取恆指近期數據 (作為前端靜態圖表的修補包)
        hsi_recent_data = {"dates": [], "prices": []}
        try:
            hsi_t = yf.Ticker("^HSI")
            hsi_recent = hsi_t.history(period="3mo") # 只抓近 3 個月，極快
            if not hsi_recent.empty:
                hsi_recent_data["prices"] = [round(p, 2) for p in hsi_recent['Close'].dropna().tolist()]
                hsi_recent_data["dates"] = [d.strftime('%Y-%m-%d') for d in hsi_recent.index]
        except Exception as e:
            debug_logs['hsi_recent_error'] = str(e)

        # ... (後面獲取其他資產近一年數據的代碼保持不變) ...

        return jsonify({
            "status": "success",
            "hsi_pe": round(pe, 2) if pe else "N/A",
            "hsi_recent": hsi_recent_data, # 🟢 記得把修補包加進回傳的 JSON 裡！
            "markets": market_data,
            "debug": debug_logs
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
