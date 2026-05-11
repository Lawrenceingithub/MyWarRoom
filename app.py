import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 系統設定與初始化 (已預載你的真實持倉)
# ==========================================
st.set_page_config(page_title="戰術雷達 V1.6", layout="wide", page_icon="🎯")

if 'my_portfolio' not in st.session_state:
    st.session_state.my_portfolio = [
        {"代碼": "NVDA", "成本": 190.88, "股數": 20, "均線": 20, "容忍度": 1.5},
        {"代碼": "CEG", "成本": 259.59, "股數": 10, "均線": 20, "容忍度": 1.5},
        {"代碼": "ETN", "成本": 412.97, "股數": 18, "均線": 20, "容忍度": 1.5},
        {"代碼": "3690.HK", "成本": 77.0, "股數": 200, "均線": 60, "容忍度": 2.5},
        {"代碼": "0939.HK", "成本": 7.7, "股數": 2000, "均線": 60, "容忍度": 2.0},
        {"代碼": "1919.HK", "成本": 15.49, "股數": 500, "均線": 60, "容忍度": 3.0}
    ]

st.title("🦅 戰術雷達監控中心 V1.6 (Windows 部署版)")

# ==========================================
# 2. 側邊欄：動態配置面板
# ==========================================
with st.sidebar:
    st.header("⚙️ 陣地配置")
    edited_df = st.data_editor(
        pd.DataFrame(st.session_state.my_portfolio),
        num_rows="dynamic",
        key="portfolio_editor"
    )
    if st.button("💾 儲存並同步", use_container_width=True):
        st.session_state.my_portfolio = edited_df.to_dict('records')
        st.success("部隊配置已更新！")

# ==========================================
# 3. 核心運算邏輯
# ==========================================
@st.cache_data(ttl=60)
def analyze_stock(ticker, ma_window, max_volatility):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if len(hist) < ma_window + 1: return None
        hist[f'MA_{ma_window}'] = hist['Close'].rolling(window=ma_window).mean()
        latest, prev = hist.iloc[-1], hist.iloc[-2]
        price, ma_val = latest['Close'], latest[f'MA_{ma_window}']
        change = ((price - prev['Close']) / prev['Close']) * 100
        dist = ((price - ma_val) / ma_val) * 100
        can_buy = (-1.0 <= dist <= 2.0) and (abs(change) <= max_volatility)
        return {"price": price, "change": change, "ma": ma_val, "dist": dist, "can_buy": can_buy}
    except: return None

# ==========================================
# 4. 主介面渲染
# ==========================================
st.markdown("---")
tab1, tab2 = st.tabs(["🛡️ 核心陣地監控", "🔍 單兵偵察系統"])

with tab1:
    portfolio = st.session_state.my_portfolio
    cols = st.columns(3)
    for i, stock in enumerate(portfolio):
        with cols[i % 3]:
            ticker = stock['代碼']
            res = analyze_stock(ticker, stock['均線'], stock['容忍度'])
            st.markdown(f"### 🎯 {ticker}")
            if res:
                st.metric("目前市價", f"${res['price']:.2f}", f"{res['change']:.2f}%")
                st.metric(f"MA{stock['均線']} 防線", f"${res['ma']:.2f}", f"距離 {res['dist']:.2f}%", delta_color="inverse")
                if res['can_buy']: st.success("🟢 穩定進入伏擊區")
                elif res['dist'] < -1.0: st.error("🚨 跌破防線")
                else: st.info("⚪ 觀望中")
            st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.write("（此分頁可用於輸入任何代碼，如 TSLA 或 0700.HK 進行即時偵察）")