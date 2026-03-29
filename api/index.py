from flask import Flask, jsonify, request # 🟢 引入 request
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

@app.route('/api/data')
def get_data():
    debug_logs = {}
    
    # 🟢 接收前端傳來的指定開始日期 (例如 "2024-03-01")
    start_date = request.args.get('start') 
    
    try:
        # 1. 獲取真實 PE 
        pe = None
        try:
            tracker = yf.Ticker("2800.HK") 
            pe = tracker.info.get('trailingPE') or tracker.info.get('forwardPE')
        except Exception as e:
            debug_logs['pe_error'] = str(e)

        # 2. 🟢 獲取恆指修補包 (根據指定的日期動態抓取)
        hsi_recent_data = {"dates": [], "prices": []}
        try:
            hsi_t = yf.Ticker("^HSI")
            if start_date:
                hsi_recent = hsi_t.history(start=start_date) # 精準抓取斷層期間的數據
            else:
                hsi_recent = hsi_t.history(period="1y") # 預設值
                
            if not hsi_recent.empty:
                hsi_recent_data["prices"] = [round(p, 2) for p in hsi_recent['Close'].dropna().tolist()]
                hsi_recent_data["dates"] = [d.strftime('%Y-%m-%d') for d in hsi_recent.index]
        except Exception as e:
            debug_logs['hsi_recent_error'] = str(e)

        # 3. 獲取其他資產近一年數據
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
            except Exception as e:
                debug_logs[key] = str(e)

        return jsonify({
            "status": "success",
            "hsi_pe": round(pe, 2) if pe else "N/A",
            "hsi_recent": hsi_recent_data, # 🟢 回傳修補包
            "markets": market_data,
            "debug": debug_logs
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
