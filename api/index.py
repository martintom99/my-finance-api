from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
# 允許跨網域請求 (CORS)，這樣你的 HTML 才能讀取這個 API
CORS(app)

@app.route('/api/data')
def get_data():
    try:
        # 1. 獲取盈富基金 (2800.HK) 作為恆指 PE 參考
        pe = 8.75
        try:
            tracker = yf.Ticker("2800.HK")
            pe = tracker.info.get('trailingPE', 8.75)
        except:
            pass # 如果抓取失敗，保留預設值

        # 2. 定義要抓取的資產代號
        tickers = {
            'spx': '^GSPC', # 標普500
            'dji': '^DJI',  # 道瓊斯
            'ndx': '^IXIC', # 納斯達克
            'gold': 'GC=F', # 黃金
            'oil': 'CL=F'   # 原油
        }

        market_data = {}
        
        # 3. 逐一抓取過去一年的每日數據
        for key, symbol in tickers.items():
            t = yf.Ticker(symbol)
            hist = t.history(period="1y")
            
            if not hist.empty:
                # 提取收盤價並捨入到小數點後兩位
                prices = [round(p, 2) for p in hist['Close'].dropna().tolist()]
                # 提取日期格式 YYYY-MM-DD
                dates = [d.strftime('%Y-%m-%d') for d in hist.index]
                
                market_data[key] = {
                    "prices": prices,
                    "dates": dates
                }

        # 4. 回傳 JSON 格式
        return jsonify({
            "status": "success",
            "hsi_pe": round(pe, 2),
            "markets": market_data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 這行是給 Vercel 運作 Flask 用的
if __name__ == '__main__':
    app.run(debug=True)
